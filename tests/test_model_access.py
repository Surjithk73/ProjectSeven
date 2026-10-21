import json
import time
from types import SimpleNamespace

import httpx
import pytest

from apishield.model_access import (cloud_connection, disabled_connection,
                                   environment_connection, model_client, connection_error)
from apishield.model_http import DeadlineTransport, request_bytes


def credential(**changes):
    return json.dumps({**dict(type='service_account',project_id='test-project-123',
        client_email='fixture@test-project-123.iam.gserviceaccount.com',private_key='PRIVATE-FIXTURE',
        private_key_id='fixture',token_uri='https://oauth2.googleapis.com/token'), **changes}).encode()


@pytest.fixture
def fake_credentials(monkeypatch):
    from google.oauth2 import service_account
    seen=[]
    class Credentials:
        token='TOKEN-FIXTURE'
        valid=True
        def refresh(self,request):
            seen.append('refresh')
    monkeypatch.setattr(service_account.Credentials,'from_service_account_info',
                        lambda data,scopes: Credentials())
    return seen


def test_cloud_metadata_and_repr_never_expose_credentials(fake_credentials):
    connection=cloud_connection(credential())
    assert connection.ready
    assert connection.metadata()=={'provider':'google_cloud','project':'test-project-123','location':'global'}
    assert 'PRIVATE-FIXTURE' not in repr(connection)
    assert 'TOKEN-FIXTURE' not in repr(connection)


@pytest.mark.parametrize('raw',[b'[]',b'no JSON',b'\xff',b' '*65537,
    b'{"type":"authorized_user"}',b'{"type":"service_account"}'],
    ids=['array','malformed','encoding','oversized','user','incomplete'])
def test_invalid_credentials_rejected_without_echo(raw):
    with pytest.raises(ValueError) as failure:
        cloud_connection(raw)
    assert raw.decode(errors='ignore').strip() not in str(failure.value) or len(raw.strip())<2


@pytest.mark.parametrize('field,value',[('token_uri','https://evil.example/token'),('project_id','../project'),
    ('client_email','not-an-email'),('subject','another-user@example.com')])
def test_unapproved_credentials_destinations_and_delegation_rejected(fake_credentials,field,value):
    data=json.loads(credential());data[field]=value
    with pytest.raises(ValueError):
        cloud_connection(json.dumps(data).encode())
    assert not fake_credentials


def test_provider_is_explicit_and_private_fields_do_not_leak(monkeypatch,fake_credentials):
    from google import genai
    captured=[]
    class Client:
        def __init__(self,**kwargs): captured.append(kwargs)
        def close(self): pass
    monkeypatch.setattr(genai,'Client',Client)
    monkeypatch.setenv('GOOGLE_GENAI_USE_VERTEXAI','true')
    monkeypatch.setenv('GOOGLE_GENAI_USE_ENTERPRISE','true')
    monkeypatch.setenv('GEMINI_API_KEY','AMBIENT-WRONG-KEY')
    with model_client(cloud_connection(credential()),time.monotonic()+1): pass
    assert captured[0]['enterprise'] is True and captured[0]['vertexai'] is True
    assert captured[0]['project']=='test-project-123' and captured[0]['location']=='global'
    assert captured[0].get('api_key') is None
    assert captured[0]['http_options'].retry_options.attempts==1
    assert captured[0]['http_options'].client_args['trust_env'] is False
    assert fake_credentials==['refresh']
    assert not disabled_connection().ready
    assert environment_connection().metadata()['provider']=='disabled'



def test_cancel_after_authentication_starts_no_inference(monkeypatch,fake_credentials):
    from google import genai
    monkeypatch.setattr(genai,'Client',lambda **kwargs:pytest.fail('cancelled auth must not build model client'))
    def check():
        if fake_credentials:
            raise RuntimeError('cancelled')
    with pytest.raises(RuntimeError,match='cancelled'):
        with model_client(cloud_connection(credential()),time.monotonic()+1,check): pass


def test_errors_classified_without_echoing_private_values():
    result=connection_error(SimpleNamespace(code=403,message='PRIVATE-FIXTURE TOKEN-FIXTURE'))
    assert result['category']=='permissions'
    assert 'FIXTURE' not in json.dumps(result)


def test_billing_disabled_is_not_misreported_as_iam_permissions():
    from google.genai.errors import ClientError
    error=ClientError(403,{'error':{'details':[{
        '@type':'type.googleapis.com/google.rpc.ErrorInfo','reason':'BILLING_DISABLED',
        'metadata':{'consumer':'PRIVATE-FIXTURE'}}]}})
    result=connection_error(error)
    assert result['category']=='billing'
    assert 'billing' in result['message'].lower()
    assert 'PRIVATE-FIXTURE' not in json.dumps(result)


@pytest.mark.parametrize('url',['http://aiplatform.googleapis.com/test','https://evil.example/test',
    'https://aiplatform.googleapis.com:444/test','https://user:password@aiplatform.googleapis.com/test'])
def test_transport_rejects_unapproved_destinations_before_connect(url):
    with pytest.raises(ValueError):
        DeadlineTransport(time.monotonic()+1).handle_request(httpx.Request('GET',url))


def test_expired_transport_starts_no_connection():
    with pytest.raises(TimeoutError):
        request_bytes('POST','https://oauth2.googleapis.com/token',{},b'',time.monotonic()-1)


def test_transport_falls_back_after_failed_address_without_replaying_request(monkeypatch):
    from apishield import model_http
    attempts, writes, closed = [], [], []
    clock = [100.0]
    monkeypatch.setattr(time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(model_http, '_resolve', lambda *args: ['2001:4860:4860::8888', '8.8.8.8'])
    class Connection:
        def __init__(self, host, port, timeout):
            assert timeout <= 5
            self.sock = SimpleNamespace(settimeout=lambda value: None)
        def connect(self):
            self._create_connection(None, self.timeout if hasattr(self, 'timeout') else 5)
        def close(self): closed.append(True)
        def send(self, data): pass
        def request(self, *args, **kwargs): writes.append(True)
        def getresponse(self):
            return SimpleNamespace(status=200, getheader=lambda key: '0',
                getheaders=lambda: [], read1=lambda size: b'')
    def connect(address, timeout):
        attempts.append(address[0])
        if len(attempts) == 1:
            clock[0] += timeout
            raise TimeoutError('unreachable address')
        return SimpleNamespace(settimeout=lambda value: None, close=lambda: None)
    monkeypatch.setattr(model_http.http.client, 'HTTPSConnection', Connection)
    monkeypatch.setattr(model_http.socket, 'create_connection', connect)
    result = request_bytes('POST', 'https://oauth2.googleapis.com/token', {}, b'', 120)
    assert result == (200, {}, b'')
    assert attempts == ['2001:4860:4860::8888', '8.8.8.8']
    assert len(writes) == 1 and len(closed) == 2
    assert clock[0] == 105


@pytest.mark.parametrize('elapsed,allowed',[(0.6,True),(1.1,False)])
def test_auth_and_inference_share_remaining_budget(monkeypatch,fake_credentials,elapsed,allowed):
    from apishield import model_access
    from google import genai
    clock=[100.0]
    captured=[]
    monkeypatch.setattr(time,'monotonic',lambda:clock[0])
    connection=cloud_connection(credential())
    monkeypatch.setattr(model_access,'_credentials',lambda raw:SimpleNamespace(refresh=lambda request:clock.__setitem__(0,100+elapsed)))
    monkeypatch.setattr(genai,'Client',lambda **kwargs:captured.append(kwargs) or SimpleNamespace(close=lambda:None))
    if allowed:
        with model_client(connection,101): pass
        assert 399<=captured[0]['http_options'].timeout<=400
    else:
        with pytest.raises(TimeoutError):
            with model_client(connection,101): pass
        assert not captured


@pytest.mark.parametrize('wire',[b'HTTP/1.1 200 OK\r\nX-Slow: ',
    b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n1',
    b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\na'])
def test_protocol_reads_cannot_outlive_absolute_deadline(monkeypatch,wire):
    import socket
    from apishield import model_http
    left,right=socket.socketpair()
    closed=[]
    class Connection:
        sock=left
        def __init__(self,*args,**kwargs): pass
        def connect(self): pass
        def send(self,*args): pass
        def request(self,*args,**kwargs): right.sendall(wire)
        def getresponse(self):
            response=self.response_class(self.sock,method='POST'); response.begin(); return response
        def close(self):
            closed.append(True);left.close();right.close()
    monkeypatch.setattr(model_http,'_resolve',lambda *args:['8.8.8.8'])
    monkeypatch.setattr(model_http.http.client,'HTTPSConnection',Connection)
    started=time.monotonic()
    with pytest.raises(TimeoutError):
        request_bytes('POST','https://aiplatform.googleapis.com/test',{},b'',started+0.08)
    assert time.monotonic()-started<1 and closed


@pytest.mark.parametrize('status,length',[(302,'0'),(200,str(2*1024*1024+1))])
def test_redirects_and_oversized_responses_close_without_transfer(monkeypatch,status,length):
    from apishield import model_http
    captured={}
    class Connection:
        sock=SimpleNamespace(settimeout=lambda value:None)
        def __init__(self,*args,**kwargs): pass
        def connect(self): pass
        def send(self,*args): pass
        def request(self,*args,**kwargs): captured.update(kwargs['headers'])
        def getresponse(self): return SimpleNamespace(status=status,getheader=lambda key:length)
        def close(self): captured['closed']=True
    monkeypatch.setattr(model_http,'_resolve',lambda *args:['8.8.8.8'])
    monkeypatch.setattr(model_http.http.client,'HTTPSConnection',Connection)
    with pytest.raises(ValueError):
        request_bytes('POST','https://oauth2.googleapis.com/token',{'Cookie':'SECRET','Proxy-Authorization':'SECRET'},b'',time.monotonic()+1)
    assert captured=={'Accept-Encoding':'identity','closed':True}


def test_exhausted_tls_handshake_starts_no_request(monkeypatch):
    from apishield import model_http
    clock=[100.0];closed=[]
    monkeypatch.setattr(time,'monotonic',lambda:clock[0])
    class Connection:
        sock=SimpleNamespace(settimeout=lambda value:None)
        def __init__(self,*args,**kwargs): pass
        def connect(self):clock[0]=102
        def send(self,*args):pytest.fail('deadline expired before write')
        def request(self,*args,**kwargs):pytest.fail('deadline expired during handshake')
        def close(self):closed.append(True)
    monkeypatch.setattr(model_http,'_resolve',lambda *args:['8.8.8.8'])
    monkeypatch.setattr(model_http.http.client,'HTTPSConnection',Connection)
    with pytest.raises(TimeoutError):
        request_bytes('POST','https://oauth2.googleapis.com/token',{},b'',101)
    assert closed


def test_oauth_transient_failure_never_sleeps_outside_deadline(monkeypatch):
    from apishield import model_http
    from google.oauth2 import _client
    from google.auth import _exponential_backoff
    clock=[100.0];calls=[]
    monkeypatch.setattr(time,'monotonic',lambda:clock[0])
    monkeypatch.setattr(_exponential_backoff.time,'sleep',lambda seconds:clock.__setitem__(0,clock[0]+seconds))
    def response(method,url,headers,body,deadline):
        model_http.remaining(deadline)
        calls.append(True);clock[0]=100.04
        return 503,{},b'{"error":"temporarily_unavailable","private_data":"PRIVATE-FIXTURE"}'
    monkeypatch.setattr(model_http,'request_bytes',response)
    with pytest.raises(Exception) as failure:
        _client.jwt_grant(model_http.oauth_request(100.05),'https://oauth2.googleapis.com/token','SYNTHETIC-ASSERTION')
    assert clock[0]<=100.05 and len(calls)==1
    assert 'PRIVATE-FIXTURE' not in str(failure.value)
