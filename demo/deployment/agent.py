"""System B polls merged PRs. It never executes PR branches or merges them."""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import uuid

import httpx
from apishield.contract_fetch import canonical_hash
from apishield.github_cli import GhClient, repository_name, sha
from apishield.jobs import atomic_json
from apishield.merge_tracking import classify_merge
from .receipt import publish_receipt
from .release import ReleaseManager


def candidate_from_pr(pr, checks, config):
    if pr.get('user', {}).get('login', '').casefold() != config['publisher'].casefold() or pr.get('base', {}).get('ref') != config['base']:
        return None
    body = pr.get('body') or ''
    metadata = re.search(r'<!-- APIShield workflow (\{[^\n]+\}) -->', body)
    candidate = re.search(r'<!-- APIShield candidate ([0-9a-f]{40}) -->', body)
    if not metadata or not candidate:
        return None
    workflow = json.loads(metadata.group(1))
    if workflow['repository'].casefold() != config['repository'].casefold() or workflow['project_id'] != config['project_id'] or workflow['base'] != config['base']:
        return None
    status = classify_merge(pr, checks, candidate.group(1))
    if status['state'] != 'merged':
        return None
    return {'workflow': workflow, 'merge_sha': status['merge_sha'], 'number': pr['number']}


class DeploymentAgent:
    def __init__(self, config):
        self.config = config
        repository_name(config['repository'])
        self.github = GhClient()
        self.url = f'http://127.0.0.1:{int(config.get("client_port", 8100))}'
        self.manager = ReleaseManager(config['releases'], self.prepare, self.start, self.stop, self.verify)
        self.children = {}
        self.receipts = self.manager.root / 'receipts.json'

    def command(self, argv, cwd):
        result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=240,
                                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        if result.returncode:
            raise ValueError('Release preparation failed; inspect the configured repository, requirements and client tests')

    def prepare(self, revision, path):
        if not path.exists():
            self.command(['git', 'clone', '--no-checkout', f'https://github.com/{self.config["repository"]}.git', str(path)], self.manager.root)
        self.command(['git', 'fetch', 'origin', sha(revision)], path)
        self.command(['git', 'checkout', '--detach', sha(revision)], path)
        current = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        if current != revision:
            raise ValueError('Fetched client revision does not match the merged PR')
        python = path / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        if not python.exists():
            self.command([sys.executable, '-m', 'venv', str(path / '.venv')], path)
        self.command([str(python), '-m', 'pip', 'install', '-r', 'requirements-cinema.txt'], path)
        self.command([str(python), '-m', 'pytest', 'movie_booking/tests', '-q'], path)

    def start(self, revision, path):
        instance = uuid.uuid4().hex
        python = path / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        environment = {k: v for k, v in os.environ.items() if not re.search('TOKEN|SECRET|KEY|CREDENTIAL|PASSWORD', k, re.I)}
        environment.update(CINEMA_DEPLOYED_SHA=revision, CINEMA_INSTANCE_ID=instance,
            CINEMA_THEATRE_URL=self.config['providers']['theatre'], CINEMA_PAYMENT_URL=self.config['providers']['payment'])
        log = (self.manager.root / 'client.log').open('ab')
        try:
            process = subprocess.Popen([str(python), '-m', 'uvicorn', 'movie_booking.app:create_app', '--factory', '--host',
                '0.0.0.0', '--port', str(self.config.get('client_port', 8100))], cwd=path, env=environment,
                stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        finally:
            log.close()
        self.children[process.pid] = process
        for _ in range(30):
            if process.poll() is not None:
                raise ValueError('Client process exited during startup; check client.log')
            try:
                info = httpx.get(self.url + '/health', timeout=1, trust_env=False).json()
                if info.get('revision') == revision and info.get('instance') == instance:
                    return {'pid': process.pid, 'instance': instance}
            except (httpx.HTTPError, ValueError):
                pass
            time.sleep(.5)
        process.terminate()
        raise ValueError('Client did not start at the expected port and revision')

    def stop(self, active):
        process = self.children.get(active['pid'])
        if process:
            process.terminate()
            process.wait(timeout=15)
            return
        info = httpx.get(self.url + '/health', timeout=3, trust_env=False).json()
        if info.get('pid') != active['pid'] or info.get('instance') != active['instance']:
            raise ValueError('Refusing to stop a process that does not match the managed client identity')
        os.kill(int(active['pid']), signal.SIGTERM)
        time.sleep(1)

    def verify(self, active):
        try:
            health = httpx.get(self.url + '/health', timeout=4, trust_env=False)
            if health.status_code != 200 or health.json().get('revision') != active['sha'] or health.json().get('instance') != active['instance']:
                return False
            response = httpx.post(self.url + '/internal/smoke', timeout=25, trust_env=False)
            passed = response.status_code == 200 and response.json().get('status') == 'confirmed'
            if passed and getattr(self, 'current_workflow', None):
                self.provider_hashes(self.current_workflow)
            return passed
        except (httpx.HTTPError, ValueError):
            return False

    def bootstrap(self):
        """Explicit initial baseline only; subsequent updates require an associated PR."""
        state = self.manager.state()
        if state.get('pending'):
            started = state['pending'].get('started')
            if started:
                try:
                    self.stop(started)
                except httpx.ConnectError:
                    pass
            state['pending'] = None
            self.manager.save(state)
        if state['active']:
            active = state['active']
            try:
                response = httpx.get(self.url + '/health', timeout=3, trust_env=False)
                if response.json().get('instance') == active['instance']:
                    return
            except (httpx.HTTPError, ValueError):
                pass
            state['active'] = {**self.start(active['sha'], self.manager.path(active['sha'])), 'sha':active['sha']}
            self.manager.save(state)
            return
        repo = repository_name(self.config['repository'])
        deadline = time.monotonic()+45
        ref = self.github.api('GET', f'repos/{repo}/git/ref/heads/{self.config["base"]}', None, deadline=deadline)
        revision = sha(ref['object']['sha'])
        checks = self.github.api('GET', f'repos/{repo}/commits/{revision}/check-runs?per_page=100', None, deadline=deadline).get('check_runs', [])
        if not any(c.get('name')=='cinema-client' and c.get('head_sha')==revision and c.get('status')=='completed' and c.get('conclusion')=='success' for c in checks):
            raise ValueError('Initial CinemaFlow baseline must have successful client CI before bootstrap')
        result = self.manager.deploy(revision)
        if result['status'] not in {'verified','already_deployed'}:
            raise ValueError(result.get('error','Initial client baseline did not start'))

    def provider_hashes(self, workflow):
        hashes = {}
        for provider, expected in workflow['providers'].items():
            url = self.config['providers'][provider].rstrip('/') + '/openapi.json'
            response = httpx.get(url, timeout=10, trust_env=False)
            response.raise_for_status()
            hashes[provider] = canonical_hash(response.json())
            if hashes[provider] != expected['observed_hash']:
                raise ValueError('Live provider changed after candidate validation; wait for a new proposal')
        return hashes

    def tick(self):
        done = json.loads(self.receipts.read_text()) if self.receipts.exists() else {}
        deadline = time.monotonic() + 60
        repo = repository_name(self.config['repository'])
        prs = self.github.api('GET', f'repos/{repo}/pulls?state=closed&base={self.config["base"]}&sort=updated&direction=desc&per_page=30', None, deadline=deadline)
        head = self.github.api('GET', f'repos/{repo}/git/ref/heads/{self.config["base"]}', None, deadline=deadline)['object']['sha']
        for summary in prs:
            if not summary.get('merged_at'):
                continue
            pr = self.github.api('GET', f'repos/{repo}/pulls/{int(summary["number"])}', None, deadline=deadline)
            merged = sha(pr.get('merge_commit_sha'))
            if merged != head:
                continue  # Never roll back main by discovering an older merged PR later.
            if merged in done:
                # A previous network error after deploy must retry receipt publication, never redeploy.
                if not done[merged].get('published'):
                    publish_receipt(self.github, repo, pr['number'], merged, done[merged]['receipt'], self.config['deployment_actor'])
                    done[merged]['published'] = True
                    atomic_json(self.receipts, done)
                continue
            checks = self.github.api('GET', f'repos/{repo}/commits/{merged}/check-runs?per_page=100', None, deadline=deadline).get('check_runs', [])
            candidate = candidate_from_pr(pr, checks, self.config)
            if not candidate:
                continue
            workflow = candidate['workflow']
            hashes = self.provider_hashes(workflow)
            self.current_workflow = workflow
            outcome = self.manager.deploy(merged)
            self.current_workflow = None
            if outcome['status'] == 'already_deployed':
                outcome['status'] = 'verified'
            receipt = {**outcome, 'version': 1, 'workflow_id': workflow['workflow_id'], 'project_id': workflow['project_id'], 'provider_hashes': hashes}
            done[merged] = {'receipt': receipt, 'published': False}
            atomic_json(self.receipts, done)
            publish_receipt(self.github, repo, candidate['number'], merged, receipt, self.config['deployment_actor'])
            done[merged]['published'] = True
            atomic_json(self.receipts, done)
            return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--bootstrap', action='store_true')
    args = parser.parse_args()
    from demo.setup import workspace_path
    config = json.loads(workspace_path(args.config).read_text(encoding='utf-8'))
    config['releases'] = str(workspace_path(config['releases']))
    agent = DeploymentAgent(config)
    if args.bootstrap:
        agent.bootstrap()
    while True:
        try:
            agent.tick()
        except Exception as error:
            atomic_json(agent.manager.root / 'last-error.json', {'error': str(error)[:1000]})
            if args.once:
                raise
        if args.once:
            break
        time.sleep(10)


if __name__ == '__main__':
    main()
