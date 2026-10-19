"""Revisioned GitHub targets, durable proposals and cross-process ownership."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re

from .jobs import _job_transaction,atomic_json,timestamp
from .engine import _execution_lock


class PublicationConflict(ValueError):pass


def proposal_identity(repository,base,source_commit,patch_sha256):
    data=[repository.casefold(),base,source_commit,patch_sha256]
    return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()


class PublicationStore:
    def __init__(self,root):self.root=Path(root).resolve()/'_publication'

    def _directory(self,kind,key):
        pattern=r'[A-Za-z0-9_-]{1,64}' if kind=='targets' else r'[0-9a-f]{64}'
        if not isinstance(key,str) or not re.fullmatch(pattern,key) or re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])',key):
            raise ValueError('Invalid publication identity')
        path=self.root/kind/key
        for item in (self.root,self.root/kind,path):
            if item.is_symlink():raise ValueError('Unsafe publication directory')
        path.mkdir(parents=True,exist_ok=True)
        for name in ('state.json','state.lock','execution.lock'):
            if (path/name).is_symlink():raise ValueError('Unsafe publication state path')
        return path

    def directory(self,identity):return self._directory('proposals',identity)

    @contextmanager
    def _transaction(self,kind,key,default):
        directory=self._directory(kind,key)
        with _job_transaction(directory):
            path=directory/'state.json'
            try:
                data=json.loads(path.read_text(encoding='utf-8')) if path.exists() else dict(default)
                if not isinstance(data,dict) or (data and data.get('version')!=1):raise ValueError()
                if kind=='proposals' and data and data.get('id')!=key:raise ValueError()
                if kind=='targets' and type(data.get('revision')) is not int:raise ValueError()
            except (OSError,ValueError):raise ValueError('Malformed publication state; preserve and review its files') from None
            before=json.dumps(data,sort_keys=True)
            yield data
            if json.dumps(data,sort_keys=True)!=before:atomic_json(path,data)

    def read_target(self,integration):
        default={'version':1,'revision':0,'configured':False}
        with self._transaction('targets',integration,default) as state:return json.loads(json.dumps(state))

    def save_target(self,integration,target,expected_revision):
        with self._transaction('targets',integration,{'version':1,'revision':0,'configured':False}) as state:
            if type(expected_revision) is not int or state['revision']!=expected_revision:
                raise PublicationConflict('GitHub target changed; refresh and prepare again')
            revision=state['revision']+1
            state.clear();state.update({key:target[key] for key in ('repository','base','account')})
            state.update({key:target[key] for key in ('permission','private','url') if key in target})
            state.update(version=1,revision=revision,configured=True)
            return json.loads(json.dumps(state))

    def transaction(self,identity):return self._transaction('proposals',identity,{})

    def reserve(self,identity,record):
        with self.transaction(identity) as state:
            if not state:state.update(record)
            return json.loads(json.dumps(state))

    def read(self,identity):
        with self.transaction(identity) as state:
            if not state:raise FileNotFoundError('Unknown publication proposal')
            return json.loads(json.dumps(state))

    def update(self,identity,**changes):
        with self.transaction(identity) as state:
            if not state:raise FileNotFoundError('Unknown publication proposal')
            state.update(changes,updated_at=timestamp())
            return json.loads(json.dumps(state))

    def ownership(self,identity):return _execution_lock(self.directory(identity))

    def list(self):
        path=self.root/'proposals'
        if not path.exists():return []
        if path.is_symlink():raise ValueError('Unsafe publication directory')
        return [self.read(item.name) for item in path.iterdir() if re.fullmatch('[0-9a-f]{64}',item.name)]
