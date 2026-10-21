"""Revisioned project and workflow state outside source repositories."""
from contextlib import contextmanager
import json
from pathlib import Path

from .jobs import _job_transaction, atomic_json
from .projects import ClientProject, ProviderBinding, identifier


class ProjectStore:
    def __init__(self, root):
        self.root = Path(root).resolve() / '_projects'

    def directory(self, project_id):
        identifier(project_id)
        path = self.root / project_id
        if self.root.is_symlink() or path.is_symlink():
            raise ValueError('Unsafe project state directory')
        path.mkdir(parents=True, exist_ok=True)
        return path

    @contextmanager
    def transaction(self, project_id):
        directory = self.directory(project_id)
        for name in ('state.json', 'state.lock'):
            if (directory / name).is_symlink():
                raise ValueError('Unsafe project state file')
        with _job_transaction(directory):
            file = directory / 'state.json'
            state = json.loads(file.read_text()) if file.exists() else {'project': None, 'workflows': []}
            yield state
            atomic_json(file, state)

    def save(self, data, expected_revision):
        project = ClientProject(**data)
        with self.transaction(project.project_id) as state:
            revision = state['project']['revision'] if state['project'] else 0
            if type(expected_revision) is not int or expected_revision != revision:
                raise ValueError('Project changed; reload before saving')
            project.revision = revision + 1
            state['project'] = project.to_dict()
            return project.to_dict()

    def load_project(self, project_id):
        with self.transaction(project_id) as state:
            if not state['project']:
                raise KeyError('Unknown client project')
            return ClientProject(**state['project'])

    def list(self):
        if not self.root.exists():
            return []
        return [self.load_project(p.name).to_dict() for p in self.root.iterdir() if p.is_dir() and (p / 'state.json').is_file()
                and json.loads((p / 'state.json').read_text()).get('project')]

    def workflows(self, project_id):
        with self.transaction(project_id) as state:
            return json.loads(json.dumps(state['workflows']))

    def ensure_legacy(self, integration_id, repository, base_url):
        try:
            return self.load_project(integration_id)
        except KeyError:
            self.save(ClientProject(integration_id, str(repository), [ProviderBinding(integration_id, integration_id, base_url)]).to_dict(), 0)
            return self.load_project(integration_id)
