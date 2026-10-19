"""Managed release directories and a durable rollback journal; no file deletion."""
import json
from pathlib import Path

from apishield.engine import _execution_lock
from apishield.github_cli import sha
from apishield.jobs import atomic_json, timestamp


class ReleaseManager:
    def __init__(self, root, prepare, start, stop, verify):
        raw = Path(root)
        if raw.is_symlink():
            raise ValueError('Release directory cannot be a symlink')
        self.root = raw.resolve()
        marker = self.root / '.apishield-demo-releases'
        if self.root.exists() and any(self.root.iterdir()) and not marker.is_file():
            raise ValueError('Existing directory is not a managed demo release root')
        self.root.mkdir(parents=True, exist_ok=True)
        marker.touch(exist_ok=True)
        self.prepare, self.start, self.stop, self.verify = prepare, start, stop, verify

    def state(self):
        path = self.root / 'deployment.json'
        if path.is_symlink():
            raise ValueError('Unsafe deployment journal')
        return json.loads(path.read_text()) if path.exists() else {'active': None, 'pending': None, 'history': []}

    def save(self, state):
        atomic_json(self.root / 'deployment.json', state)

    def path(self, revision):
        path = self.root / sha(revision)
        if path.is_symlink() or path.resolve().parent != self.root:
            raise ValueError('Release escapes the managed root')
        return path

    def deploy(self, revision):
        revision = sha(revision)
        with _execution_lock(self.root) as owned:
            if not owned:
                raise ValueError('Another deployment is in progress')
            state = self.state()
            previous = state['active']
            if previous and previous['sha'] == revision and self.verify(previous):
                return {'status': 'already_deployed', 'deployed_sha': revision, 'health_passed': True, 'smoke_passed': True}
            result = {'status': 'failed', 'deployed_sha': revision, 'previous_sha': previous['sha'] if previous else None,
                      'started_at': timestamp(), 'health_passed': False, 'smoke_passed': False}
            state['pending'] = {'sha': revision, 'previous': previous}
            self.save(state)
            active = None
            stopped = False
            try:
                self.prepare(revision, self.path(revision))
                if previous:
                    self.stop(previous)
                    stopped = True
                active = {**self.start(revision, self.path(revision)), 'sha': revision}
                state['pending']['started'] = active
                self.save(state)
                if not self.verify(active):
                    raise ValueError('New client did not pass revision, health and isolated booking verification')
                state.update(active=active, pending=None)
                result.update(status='verified', health_passed=True, smoke_passed=True)
            except Exception as error:
                result['error'] = str(error)[:1000]
                if active:
                    self.stop(active)
                if previous and stopped:
                    try:
                        state['active'] = {**self.start(previous['sha'], self.path(previous['sha'])), 'sha': previous['sha']}
                        result['rollback_sha'] = previous['sha']
                    except Exception as rollback_error:
                        state['active'] = None
                        result['rollback_error'] = str(rollback_error)[:1000]
                state['pending'] = None
            result['finished_at'] = timestamp()
            state['history'].append(result)
            self.save(state)
            return result
