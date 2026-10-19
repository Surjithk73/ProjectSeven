import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

import pytest

from apishield.contract_fetch import canonical_hash, fetch_contract, ContractFetchError, validate_url


SPEC = {'openapi': '3.0.0', 'info': {'title': 'Fixture', 'version': '1'}, 'paths': {}}


@pytest.fixture
def contract_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.server.headers_seen = dict(self.headers)
            if self.path == '/slow':
                time.sleep(.15)
            if self.path == '/loop':
                self.send_response(302)
                self.send_header('Location', '/loop')
                self.end_headers()
                return
            if self.path == '/redirect':
                self.send_response(302)
                self.send_header('Location', '/spec')
                self.end_headers()
                return
            if self.path == '/metadata':
                self.send_response(302)
                self.send_header('Location', 'http://169.254.169.254/latest')
                self.end_headers()
                return
            body = {'/bad': b'no json', '/object': b'[]', '/empty': b'{}',
                    '/nonfinite': b'{"openapi":"3.0.0", "value":NaN}',
                    '/large': b' ' * (2 * 1024 * 1024 + 1),
                    '/streamlarge': b' ' * (2 * 1024 * 1024 + 1)}.get(self.path, json.dumps(SPEC).encode())
            self.send_response(200)
            if self.path != '/streamlarge':
                self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server, f'http://127.0.0.1:{server.server_port}'
    server.shutdown()
    server.server_close()


def test_local_fetch_requires_opt_in_and_never_uses_credentials(contract_server, monkeypatch):
    server, url = contract_server
    monkeypatch.setenv('HTTP_PROXY', 'http://127.0.0.1:1')
    monkeypatch.setenv('GEMINI_API_KEY', 'never-send-this')
    with pytest.raises(ContractFetchError):
        fetch_contract(url)
    result = fetch_contract(url + '/redirect', allow_local=True)
    assert result.document == SPEC
    assert result.content_hash == canonical_hash(SPEC)
    assert 'Authorization' not in server.headers_seen
    assert 'Cookie' not in server.headers_seen
    assert server.headers_seen['Host'] == url.split('://')[1]


@pytest.mark.parametrize('path', ['/bad', '/object', '/empty', '/nonfinite', '/large', '/streamlarge', '/metadata', '/loop'])
def test_invalid_or_disallowed_responses_are_rejected(contract_server, path):
    with pytest.raises(ContractFetchError):
        fetch_contract(contract_server[1] + path, allow_local=True)


@pytest.mark.parametrize('url', ['https://u:p@example.com/spec', 'https://example.com/?api_key=x',
    'http://example.com/spec', 'https://0.0.0.0/spec', 'https://224.0.0.1/spec',
    'https://169.254.169.254/spec', 'https://[::]/spec', 'file:///tmp/spec'])
def test_url_policy(url):
    with pytest.raises(ContractFetchError):
        validate_url(url, allow_local=False)


def test_canonical_hash_ignores_keys_but_preserves_arrays():
    assert canonical_hash({'b': 1, 'a': [1, 2]}) == canonical_hash({'a': [1, 2], 'b': 1})
    assert canonical_hash({'a': [1, 2]}) != canonical_hash({'a': [2, 1]})


def test_all_dns_destinations_checked_and_connected_ip_pinned(monkeypatch):
    import apishield.contract_fetch as module
    monkeypatch.setattr(module, '_resolve', lambda host, port, deadline: ['8.8.8.8', '127.0.0.1'])
    with pytest.raises(ContractFetchError):
        fetch_contract('https://fixture.example/spec')
    seen = []
    monkeypatch.setattr(module, '_resolve', lambda host, port, deadline: ['8.8.8.8'])
    def connect(address, timeout, *args, **kwargs):
        seen.append(address)
        raise OSError('fixture stop')
    monkeypatch.setattr(module.socket, 'create_connection', connect)
    with pytest.raises(ContractFetchError):
        fetch_contract('https://fixture.example/spec')
    assert seen == [('8.8.8.8', 443)]


def test_deadline_remaining_timeout(monkeypatch):
    import apishield.contract_fetch as module
    with pytest.raises(ContractFetchError, match='timed out'):
        module._remaining(time.monotonic() - 1)


def test_real_slow_response_obeys_deadline(contract_server, monkeypatch):
    import apishield.contract_fetch as module
    monkeypatch.setattr(module,'TIMEOUT',.03)
    began=time.monotonic()
    with pytest.raises(ContractFetchError):
        fetch_contract(contract_server[1]+'/slow',True)
    assert time.monotonic()-began < .13


@pytest.mark.parametrize('phase',['headers','chunk_size'])
def test_trickled_protocol_bytes_obey_absolute_deadline(monkeypatch,phase):
    import socketserver
    import apishield.contract_fetch as module
    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            self.request.recv(4096)
            if phase=='chunk_size':
                self.request.sendall(b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n')
                trickle=b'0'*30+b'1\r\nx\r\n0\r\n\r\n'
            else:
                trickle=b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\n{}'
            try:
                for value in trickle:
                    self.request.sendall(bytes([value]))
                    time.sleep(.025)
            except OSError:
                pass
    server=socketserver.ThreadingTCPServer(('127.0.0.1',0),Handler)
    server.daemon_threads=True
    threading.Thread(target=server.serve_forever,daemon=True).start()
    monkeypatch.setattr(module,'TIMEOUT',.15)
    try:
        began=time.monotonic()
        with pytest.raises(ContractFetchError):
            fetch_contract(f'http://127.0.0.1:{server.server_address[1]}/',True)
        assert time.monotonic()-began < .4
    finally:
        server.shutdown();server.server_close()
