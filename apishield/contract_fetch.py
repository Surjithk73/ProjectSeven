"""Bounded, credential-free OpenAPI downloads with pinned DNS destinations."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import http.client
import ipaddress
import io
import json
import queue
import socket
import threading
import time
from urllib.parse import parse_qsl, urljoin, urlsplit

from .configuration import SECRET_NAME

LIMIT = 2 * 1024 * 1024
TIMEOUT = 15


class ContractFetchError(ValueError):
    pass


@dataclass(frozen=True)
class FetchedContract:
    document: dict
    raw: bytes
    raw_hash: str
    content_hash: str
    fetched_at: str


def canonical_hash(document: dict) -> str:
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def parse_contract(raw: bytes) -> FetchedContract:
    try:
        if not raw or len(raw) > LIMIT:
            raise ValueError('Contract must be nonempty and at most 2 MiB')
        def invalid_constant(value):
            raise ValueError('Nonfinite JSON values are not supported')
        document = json.loads(raw.decode('utf-8-sig'), parse_constant=invalid_constant)
        if not isinstance(document, dict) or not isinstance(document.get('openapi'), str) or not document['openapi'].startswith('3.'):
            raise ValueError('Expected a JSON OpenAPI 3 contract')
        return FetchedContract(document, raw, hashlib.sha256(raw).hexdigest(), canonical_hash(document),
                               datetime.now(timezone.utc).isoformat())
    except (ValueError, UnicodeError) as error:
        raise ContractFetchError(str(error)) from error


def _address_policy(value: str, allow_local: bool):
    address = ipaddress.ip_address(value)
    if getattr(address, 'ipv4_mapped', None):
        address = address.ipv4_mapped
    if address.is_unspecified or address.is_multicast or address.is_link_local or (not allow_local and not address.is_global):
        raise ContractFetchError('Destination is disallowed by the source policy')


def validate_url(url: str, allow_local: bool = False):
    try:
        if not isinstance(url, str) or len(url) > 2048 or any(ord(char) < 33 for char in url) or '\\' in url:
            raise ValueError('Enter a valid contract URL (at most 2048 characters)')
        parts = urlsplit(url)
        if parts.scheme not in ({'https', 'http'} if allow_local else {'https'}) or not parts.hostname:
            raise ValueError('Use HTTPS, or explicitly allow a trusted local HTTP source')
        if parts.username is not None or parts.password is not None or parts.fragment:
            raise ValueError('Contract URLs cannot contain credentials or fragments')
        if any(SECRET_NAME.search(key) for key, value in parse_qsl(parts.query)):
            raise ValueError('Contract URLs cannot contain secret query credentials')
        _ = parts.port
        try:
            ipaddress.ip_address(parts.hostname)
        except ValueError:
            pass
        else:
            _address_policy(parts.hostname, allow_local)
        return parts
    except ValueError as error:
        raise ContractFetchError(str(error)) from error


def _remaining(deadline):
    value = deadline - time.monotonic()
    if value <= 0:
        raise ContractFetchError('Contract download timed out')
    return value


def _resolve(host, port, deadline):
    result = queue.Queue(maxsize=1)
    def resolve():
        try:
            result.put(socket.getaddrinfo(host, port, type=socket.SOCK_STREAM))
        except OSError as error:
            result.put(error)
    # A stalled system resolver cannot extend the user's HTTP deadline.
    threading.Thread(target=resolve, daemon=True, name='apishield-contract-dns').start()
    try:
        addresses = result.get(timeout=_remaining(deadline))
    except queue.Empty as error:
        raise ContractFetchError('Contract DNS lookup timed out') from error
    if isinstance(addresses, OSError):
        raise ContractFetchError('Contract DNS lookup failed') from addresses
    return list(dict.fromkeys(entry[4][0] for entry in addresses))


class _DeadlineReader(io.RawIOBase):
    """Apply the remaining deadline to every raw read, including HTTP framing."""
    def __init__(self, sock, deadline):
        self.sock = sock
        self.stream = sock.makefile('rb', buffering=0)
        self.deadline = deadline

    def readable(self):
        return True

    def readinto(self, buffer):
        self.sock.settimeout(_remaining(self.deadline))
        count = self.stream.readinto(buffer)
        _remaining(self.deadline)
        return count

    def close(self):
        self.stream.close()
        super().close()


class _DeadlineSocket:
    def __init__(self, sock, deadline):
        self.sock, self.deadline = sock, deadline

    def makefile(self, mode):
        return io.BufferedReader(_DeadlineReader(self.sock, self.deadline))


def fetch_contract(url: str, allow_local: bool = False) -> FetchedContract:
    deadline = time.monotonic() + TIMEOUT
    try:
        for hop in range(6):
            parts = validate_url(url, allow_local)
            port = parts.port or (443 if parts.scheme == 'https' else 80)
            addresses = _resolve(parts.hostname, port, deadline)
            if not addresses:
                raise ContractFetchError('No usable contract destination')
            for address in addresses:
                _address_policy(address, allow_local)
            cls = http.client.HTTPSConnection if parts.scheme == 'https' else http.client.HTTPConnection
            connection = cls(parts.hostname, port, timeout=_remaining(deadline))
            connection.response_class = lambda sock, **kwargs: http.client.HTTPResponse(
                _DeadlineSocket(sock, deadline), **kwargs)
            # Connect only to the checked numeric IP; HTTPSConnection still verifies
            # the original hostname and sends it as SNI. No second DNS lookup.
            connection._create_connection = lambda addr, timeout, *args: socket.create_connection(
                (addresses[0], port), timeout=_remaining(deadline))
            try:
                path = parts.path or '/'
                if parts.query:
                    path += '?' + parts.query
                connection.request('GET', path, headers={'Accept': 'application/json', 'Accept-Encoding': 'identity'})
                connection.sock.settimeout(_remaining(deadline))
                response = connection.getresponse()
                if response.status in {301, 302, 303, 307, 308}:
                    location = response.getheader('Location')
                    if not location or hop == 5:
                        raise ContractFetchError('Contract redirect limit exceeded or destination missing')
                    url = urljoin(url, location)
                    continue
                if response.status != 200:
                    raise ContractFetchError(f'Contract source returned HTTP {response.status}')
                length = response.getheader('Content-Length')
                if length and int(length) > LIMIT:
                    raise ContractFetchError('Contract exceeds 2 MiB')
                content = bytearray()
                while True:
                    chunk = response.read1(min(65536, LIMIT + 1 - len(content)))
                    _remaining(deadline)
                    if not chunk:
                        break
                    content.extend(chunk)
                    if len(content) > LIMIT:
                        raise ContractFetchError('Contract exceeds 2 MiB')
                return parse_contract(bytes(content))
            finally:
                connection.close()
    except ContractFetchError:
        raise
    except (OSError, ValueError, http.client.HTTPException) as error:
        raise ContractFetchError(f'Contract fetch failed: {type(error).__name__}') from error
