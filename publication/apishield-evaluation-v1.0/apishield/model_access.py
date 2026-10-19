"""Explicit, immutable controller-only Google model connection snapshots."""
from contextlib import contextmanager
from dataclasses import dataclass, field
import json
import os
import re
import time
from pathlib import Path
import subprocess
import csv
import base64
import stat

from .model_http import DeadlineTransport, oauth_request, remaining


@dataclass(frozen=True)
class ModelConnection:
    provider: str
    project: str | None = None
    location: str = 'global'
    credential_json: bytes | None = field(default=None,repr=False)

    @property
    def ready(self):
        return self.provider == 'google_cloud' and bool(self.credential_json)

    def metadata(self):
        return {'provider':self.provider,**({'project':self.project,'location':self.location} if self.provider=='google_cloud' else {})}


def disabled_connection():
    return ModelConnection('disabled')


def environment_connection():
    try:
        path = credential_path()
    except ValueError:
        return disabled_connection()
    return file_connection(path) if path.is_file() else disabled_connection()


def credential_path():
    configured = os.environ.get('APISHIELD_CREDENTIALS_FILE')
    if configured:
        return Path(configured)
    try:
        return Path.home() / '.apishield/credentials/service-account.json'
    except RuntimeError:
        raise ValueError('Private credential directory unavailable; set APISHIELD_CREDENTIALS_FILE') from None


def _private_credential_path():
    path = credential_path().absolute()
    for part in (path, *path.parents):
        try:
            attributes = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(attributes.st_mode) or getattr(attributes, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('Unsafe private credential path')
    if path.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError('Private credentials must stay outside the project')
    return path


def persist_cloud_connection(raw):
    connection = cloud_connection(raw)
    path = _private_credential_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.name == 'nt':
        try:
            identity = subprocess.check_output(['whoami', '/user', '/fo', 'csv', '/nh'], text=True, timeout=10)
            sid = next(csv.reader(identity.strip().splitlines()))[1]
            if not re.fullmatch(r'S-1-[0-9-]+', sid):
                raise ValueError('Invalid account identity')
            directory = str(path.parent).replace("'", "''")
            script = ("$acl = New-Object System.Security.AccessControl.DirectorySecurity; "
                      f"$acl.SetSecurityDescriptorSddlForm('D:P(A;OICI;FA;;;{sid})(A;OICI;FA;;;SY)', [System.Security.AccessControl.AccessControlSections]::Access); "
                      f"[System.IO.Directory]::SetAccessControl('{directory}', $acl)")
            encoded = base64.b64encode(script.encode('utf-16le')).decode('ascii')
            subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded],
                           check=True, capture_output=True, timeout=10)
        except (OSError, subprocess.SubprocessError, IndexError):
            raise ValueError('Could not restrict the private credential directory permissions') from None
    else:
        path.parent.chmod(0o700)
    from .jobs import _atomic_bytes
    _atomic_bytes(path, connection.credential_json)
    if os.name != 'nt':
        path.chmod(0o600)
    return connection


def clear_managed_connection():
    path = _private_credential_path()
    path.unlink(missing_ok=True)
    return disabled_connection()


def file_connection(path):
    try:
        with open(path,'rb') as source:
            raw=source.read(65537)
        return cloud_connection(raw)
    except OSError:
        raise ValueError('Cannot read the selected service-account JSON file') from None


def _credentials(raw):
    from google.oauth2 import service_account
    return service_account.Credentials.from_service_account_info(json.loads(raw),scopes=['https://www.googleapis.com/auth/cloud-platform'])


def cloud_connection(raw):
    try:
        if not isinstance(raw,bytes) or not 1<=len(raw)<=65536:
            raise ValueError()
        info=json.loads(raw.decode('utf-8-sig'))
        if not isinstance(info,dict) or info.get('type')!='service_account' or info.get('token_uri')!='https://oauth2.googleapis.com/token':
            raise ValueError()
        if any(info.get(key) for key in ('subject','delegated_subject')) or info.get('universe_domain','googleapis.com')!='googleapis.com':
            raise ValueError()
        if not isinstance(info.get('project_id'),str) or not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]',info['project_id']):
            raise ValueError()
        if not isinstance(info.get('client_email'),str) or not re.fullmatch(r'[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.iam\.gserviceaccount\.com',info['client_email']):
            raise ValueError()
        if not isinstance(info.get('private_key'),str) or not info['private_key']:
            raise ValueError()
        safe={key:info[key] for key in ('type','project_id','client_email','private_key','token_uri')}
        if isinstance(info.get('private_key_id'),str):
            safe['private_key_id']=info['private_key_id']
        normalized=json.dumps(safe).encode()
        _credentials(normalized)  # Validate signer/key structure; no network.
        return ModelConnection('google_cloud',project=safe['project_id'],credential_json=normalized)
    except Exception:
        raise ValueError('Select a valid Google service-account JSON (at most 64 KiB), without delegation or custom endpoints') from None


def connection_error(error):
    code=getattr(error,'code',None)
    if code in {401}:
        category,message='authentication','Google could not authenticate this credential. Select a valid service-account file.'
    elif code==403:
        category,message='permissions','Google denied access. Check the selected project API and service-account permissions.'
    elif code==402:
        category,message='billing','Google reports unavailable billing credits. Correct project billing before retrying.'
    elif code==404:
        category,message='model_access','This model is unavailable for the selected Google project/provider.'
    elif code in {429,500,502,503,504}:
        category,message='service','Google is temporarily unavailable or rate-limited. Retry within the existing job budget.'
    elif isinstance(error,TimeoutError):
        category,message='timeout','The Google request exceeded its deadline. Retry or review connectivity.'
    else:
        from google.auth.exceptions import GoogleAuthError
        category,message=('authentication','Google could not authenticate this service account. Check its validity and project access.') if isinstance(error,GoogleAuthError) else ('configuration','The Google request failed. Review the selected credential and connection settings.')
    return {'category':category,'message':message,**({'code':code} if type(code) is int else {})}


@contextmanager
def model_client(connection,deadline,check=None):
    from google import genai
    from google.genai import types
    if not connection.ready:
        raise ValueError('Configure a model connection before requesting AI repair')
    if check: check()
    arguments={}
    credentials=_credentials(connection.credential_json)
    credentials.refresh(oauth_request(deadline))
    arguments.update(enterprise=True,vertexai=True,credentials=credentials,project=connection.project,location='global')
    if check: check()
    options=types.HttpOptions(api_version='v1',
        base_url='https://aiplatform.googleapis.com/',
        timeout=max(1,int(remaining(deadline)*1000)),retry_options=types.HttpRetryOptions(attempts=1),
        client_args={'trust_env':False,'transport':DeadlineTransport(deadline)},async_client_args={'trust_env':False})
    client=genai.Client(**arguments,http_options=options)
    try:
        yield client
    finally:
        client.close()


def test_connection(connection,model='gemini-3.8-flash'):
    from google.genai import types
    started=time.monotonic()
    try:
        with model_client(connection,started+45) as client:
            response=client.models.generate_content(model=model,contents='Reply with exactly: APIShield connection works',
                config=types.GenerateContentConfig(max_output_tokens=512,thinking_config=types.ThinkingConfig(thinking_level='LOW'),automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)))
        return {'success':True,'model':model,'text':response.text,'usage':response.usage_metadata.model_dump(mode='json') if response.usage_metadata else {},'elapsed_seconds':round(time.monotonic()-started,2)}
    except Exception as error:
        return {'success':False,'model':model,'error':connection_error(error),'elapsed_seconds':round(time.monotonic()-started,2)}
