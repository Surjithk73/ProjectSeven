"""Credential-bearing Google requests with one absolute network deadline."""
import http.client
import ipaddress
import socket
import time
from types import SimpleNamespace
from urllib.parse import urlsplit

import httpx

from .contract_fetch import _DeadlineSocket, _resolve, ContractFetchError

HOSTS = {'oauth2.googleapis.com', 'aiplatform.googleapis.com', 'generativelanguage.googleapis.com'}
LIMIT = 2 * 1024 * 1024


def remaining(deadline):
    value=deadline-time.monotonic()
    if value<=0:
        raise TimeoutError('Google request deadline exceeded')
    return value


def request_bytes(method, url, headers, body, deadline):
    parts=urlsplit(str(url))
    if parts.scheme!='https' or parts.hostname not in HOSTS or parts.port not in {None,443} or parts.username or parts.password or parts.fragment:
        raise ValueError('Unsupported Google request destination')
    remaining(deadline)
    connection=None
    try:
        addresses=_resolve(parts.hostname,443,deadline)
        if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
            raise ValueError('Unsupported Google network destination')
        # DNS can return an unreachable IPv6 route before a healthy address.
        # Bound each TCP/TLS attempt; retry only before any request is sent.
        for address in addresses:
            connect_deadline=min(deadline,time.monotonic()+5)
            connection=http.client.HTTPSConnection(parts.hostname,443,timeout=remaining(connect_deadline))
            def connect_socket(addr,timeout,*args):
                sock=socket.create_connection((address,443),timeout=remaining(connect_deadline))
                try:
                    sock.settimeout(remaining(connect_deadline))
                    return sock
                except Exception:
                    sock.close()
                    raise
            connection._create_connection=connect_socket
            connection.response_class=lambda sock,**kwargs:http.client.HTTPResponse(_DeadlineSocket(sock,deadline),**kwargs)
            try:
                connection.connect()
                break
            except OSError:
                connection.close()
                connection=None
                if address == addresses[-1]:
                    raise
        connection.sock.settimeout(remaining(deadline))
        original_send=connection.send
        def send(data):
            connection.sock.settimeout(remaining(deadline))
            original_send(data)
            remaining(deadline)
        connection.send=send
        safe_headers={key:value for key,value in headers.items() if key.lower() not in {'cookie','proxy-authorization','accept-encoding','host'}}
        safe_headers['Accept-Encoding']='identity'
        path=parts.path or '/'
        if parts.query:
            path+='?'+parts.query
        connection.request(method,path,body=body,headers=safe_headers)
        connection.sock.settimeout(remaining(deadline))
        response=connection.getresponse()
        if 300<=response.status<400:
            raise ValueError('Google request redirects are not supported')
        size=response.getheader('Content-Length')
        if size and int(size)>LIMIT:
            raise ValueError('Google response exceeds 2 MiB')
        content=bytearray()
        while True:
            chunk=response.read1(min(65536,LIMIT+1-len(content)))
            remaining(deadline)
            if not chunk:
                break
            content.extend(chunk)
            if len(content)>LIMIT:
                raise ValueError('Google response exceeds 2 MiB')
        return response.status,dict(response.getheaders()),bytes(content)
    except (OSError,http.client.HTTPException,ContractFetchError) as error:
        if isinstance(error,(TimeoutError,ContractFetchError)):
            raise TimeoutError('Google request timed out') from None
        raise ValueError('Google network request failed') from None
    finally:
        if connection:
            connection.close()


class DeadlineTransport(httpx.BaseTransport):
    def __init__(self, deadline):
        self.deadline=deadline

    def handle_request(self, request):
        status,headers,body=request_bytes(request.method,str(request.url),dict(request.headers),request.read(),self.deadline)
        return httpx.Response(status,headers=headers,content=body,request=request)


def oauth_request(deadline):
    def request(url,method='GET',body=None,headers=None,**kwargs):
        status,response_headers,data=request_bytes(method,url,headers or {},body,deadline)
        if status != 200:
            # Stop google-auth before its internal backoff sleeps outside our deadline.
            from google.auth.exceptions import RefreshError
            error=RefreshError('Google authentication request failed',retryable=False)
            error.code=status
            raise error
        return SimpleNamespace(status=status,headers=response_headers,data=data)
    return request
