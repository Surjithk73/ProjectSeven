"""Revisioned local monitor records and immutable, integrity-checked snapshots."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from .contract_fetch import parse_contract, validate_url
from .jobs import _atomic_bytes, _job_transaction, atomic_json


class MonitorConflict(ValueError):
    pass


def empty_state():
    return dict(version=1, revision=0, configured=False, enabled=False, source_url='', allow_local=False,
                interval_minutes=60, baseline_mode='saved', baseline_hash=None, last_observation_hash=None,
                config_token=None, last_attempt=None, last_success=None, next_due=None, error=None,
                active_check=None, changes=[], snapshots={})


class MonitorStore:
    def __init__(self, root: Path):
        self.root = Path(root).resolve() / '_monitoring'

    def _directory(self, integration):
        if not isinstance(integration, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', integration):
            raise ValueError('Invalid monitor integration name')
        path = self.root / integration
        if self.root.is_symlink() or path.is_symlink() or path.resolve().parent != self.root:
            raise ValueError('Unsafe monitor state directory')
        path.mkdir(parents=True, exist_ok=True)
        return path

    @contextmanager
    def transaction(self, integration):
        directory = self._directory(integration)
        if (directory / 'state.lock').is_symlink():
            raise ValueError('Unsafe monitor state lock')
        with _job_transaction(directory):
            path = directory / 'state.json'
            if path.is_symlink():
                raise ValueError('Unsafe monitor state file')
            try:
                state = json.loads(path.read_text(encoding='utf-8')) if path.exists() else empty_state()
                if not isinstance(state, dict) or set(state) != set(empty_state()) or state['version'] != 1 or type(state['revision']) is not int or not isinstance(state['changes'],list) or not isinstance(state['snapshots'],dict):
                    raise ValueError('Malformed monitor record')
            except (OSError, ValueError) as error:
                raise ValueError('Monitor state is unreadable; preserve its files and correct the record') from error
            before = json.dumps(state, sort_keys=True)
            yield state
            if json.dumps(state, sort_keys=True) != before:
                atomic_json(path, state)

    def read(self, integration):
        with self.transaction(integration) as state:
            return json.loads(json.dumps(state))

    def configure(self, integration, settings, expected_revision, config_token):
        fields = {'source_url','allow_local','interval_minutes','baseline_mode','enabled'}
        if set(settings) != fields or type(settings['allow_local']) is not bool or type(settings['enabled']) is not bool:
            raise ValueError('Invalid monitor settings')
        if type(settings['interval_minutes']) is not int or not 5 <= settings['interval_minutes'] <= 10080:
            raise ValueError('Choose a check interval from 5 to 10080 minutes')
        if settings['baseline_mode'] not in {'saved','first_fetch'}:
            raise ValueError('Choose saved or first-fetch baseline')
        validate_url(settings['source_url'], settings['allow_local'])
        with self.transaction(integration) as state:
            if type(expected_revision) is not int or state['revision'] != expected_revision:
                raise MonitorConflict('Monitoring changed; reload before saving')
            new_source = not state['configured'] or any(state[key] != settings[key] for key in ('source_url','allow_local','baseline_mode'))
            if new_source:
                state.update(baseline_hash=None,last_observation_hash=None,error=None,last_success=None)
            state.update(settings)
            state.update(configured=True, revision=state['revision']+1, config_token=config_token,
                         next_due=datetime.now(timezone.utc).isoformat() if settings['enabled'] else None)
            return json.loads(json.dumps(state))

    def retain(self, integration, fetched):
        directory = self._directory(integration) / 'snapshots'
        if directory.is_symlink():
            raise ValueError('Unsafe monitor snapshot directory')
        directory.mkdir(exist_ok=True)
        path = directory / (fetched.raw_hash + '.json')
        if path.is_symlink():
            raise ValueError('Unsafe monitor snapshot')
        if path.exists():
            if path.read_bytes() != fetched.raw:
                raise ValueError('Monitor snapshot integrity failure')
        else:
            _atomic_bytes(path, fetched.raw)
        with self.transaction(integration) as state:
            state['snapshots'].setdefault(fetched.content_hash, {'raw_hash':fetched.raw_hash, 'fetched_at':fetched.fetched_at})
        return fetched.content_hash

    def snapshot_path(self, integration, content_hash):
        state = self.read(integration)
        metadata = state['snapshots'].get(content_hash)
        if not metadata or not re.fullmatch(r'[0-9a-f]{64}', metadata.get('raw_hash','')):
            raise ValueError('Monitor snapshot unavailable')
        directory = self._directory(integration) / 'snapshots'
        path = directory / (metadata['raw_hash'] + '.json')
        if directory.is_symlink() or path.is_symlink():
            raise ValueError('Unsafe monitor snapshot')
        try:
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != metadata['raw_hash'] or parse_contract(raw).content_hash != content_hash:
                raise ValueError('Monitor snapshot integrity failure')
        except (OSError, ValueError) as error:
            raise ValueError('Monitor snapshot integrity failure') from error
        return path

    def accept(self, integration, change_id, expected_revision):
        state = self.read(integration)
        change = next((item for item in state['changes'] if item['id'] == change_id), None)
        if change is None:
            raise KeyError('Unknown monitor change')
        self.snapshot_path(integration, change['observed_hash'])
        with self.transaction(integration) as state:
            if state['revision'] != expected_revision:
                raise MonitorConflict('Monitoring changed; reload before accepting a baseline')
            state.update(baseline_hash=change['observed_hash'], revision=state['revision']+1, error=None)
            return json.loads(json.dumps(state))
