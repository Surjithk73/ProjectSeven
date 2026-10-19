"""Client project identity and explicitly attributed provider calls."""
from dataclasses import asdict, dataclass, field
import copy
from pathlib import Path
import re
from urllib.parse import urlsplit

from .configuration import relative_path
from .contract_fetch import validate_url


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', value) or re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])', value):
        raise ValueError('Invalid project/provider identifier')
    return value


@dataclass
class ProviderBinding:
    provider_id: str
    integration_id: str
    base_url: str
    path_prefix: str = ''
    source_files: list[str] = field(default_factory=list)

    def __post_init__(self):
        identifier(self.provider_id); identifier(self.integration_id)
        validate_url(self.base_url, True)
        parts = urlsplit(self.base_url)
        if parts.path not in {'', '/'} or parts.query or parts.fragment:
            raise ValueError('Provider base URL must be an origin; configure path_prefix separately')
        if not isinstance(self.path_prefix, str) or (self.path_prefix and not self.path_prefix.startswith('/')) or '?' in self.path_prefix or '#' in self.path_prefix:
            raise ValueError('Invalid provider path prefix')
        self.base_url = self.base_url.rstrip('/')
        self.path_prefix = self.path_prefix.rstrip('/')
        self.source_files = [relative_path(value) for value in self.source_files]


@dataclass
class ClientProject:
    project_id: str
    repository: str
    providers: list[ProviderBinding]
    automation_mode: str = 'manual'
    revision: int = 0
    version: int = 1
    target_repository: str = ''
    base_branch: str = 'main'
    deployment_actor: str = ''
    display_name: str = ''
    client_url: str = ''

    def __post_init__(self):
        identifier(self.project_id)
        self.providers = [ProviderBinding(**p) if isinstance(p, dict) else p for p in self.providers]
        if not self.providers or len({p.provider_id for p in self.providers}) != len(self.providers) or len({p.integration_id for p in self.providers}) != len(self.providers):
            raise ValueError('A project requires distinct provider and integration IDs')
        files = [f for p in self.providers for f in p.source_files]
        if len(files) != len(set(files)):
            raise ValueError('A source file cannot be assigned to two providers')
        if self.automation_mode not in {'manual', 'automatic_edit'}:
            raise ValueError('Choose manual or automatic_edit mode')
        if self.version != 1 or type(self.revision) is not int or self.revision < 0:
            raise ValueError('Unsupported project record')
        if not Path(self.repository).is_absolute():
            raise ValueError('Project repository must be an absolute local path')
        if self.target_repository:
            from .github_cli import repository_name
            repository_name(self.target_repository)
        if not re.fullmatch(r'[A-Za-z0-9_./-]{1,200}', self.base_branch) or '..' in self.base_branch or self.base_branch.startswith('-'):
            raise ValueError('Invalid base branch')
        if self.deployment_actor and not re.fullmatch(r'[A-Za-z0-9-]{1,39}', self.deployment_actor):
            raise ValueError('Invalid deployment account')
        if self.client_url:
            validate_url(self.client_url, True)

    def to_dict(self):
        return asdict(self)

    def http_bindings(self):
        return {name: {'provider_id': provider.provider_id, 'base_url': provider.base_url + provider.path_prefix,
                       'receiver': 'self.client'} for provider in self.providers for name in provider.source_files}


def resolve_provider(call_url, bindings):
    try:
        url = urlsplit(call_url)
        if url.scheme not in {'http', 'https'} or not url.hostname or '{' in url.netloc:
            return None
        matches = [b for b in bindings if url.scheme == urlsplit(b.base_url).scheme and url.netloc.lower() == urlsplit(b.base_url).netloc.lower()
                   and (not b.path_prefix or url.path == b.path_prefix or url.path.startswith(b.path_prefix + '/'))]
        if not matches:
            return None
        matches.sort(key=lambda b: len(b.path_prefix), reverse=True)
        if len(matches) > 1 and len(matches[0].path_prefix) == len(matches[1].path_prefix):
            return None
        return matches[0].provider_id
    except (ValueError, TypeError):
        return None


def combined_contract(documents):
    """Internal-only namespace lets the existing engine localize all providers."""
    output = {'openapi': '3.0.3', 'info': {'title': 'Client provider contracts', 'version': '1.0.0'}, 'paths': {}, 'components': {}}
    for provider_id, original in sorted(documents.items()):
        identifier(provider_id)
        doc = copy.deepcopy(original)
        def rewrite(value):
            if isinstance(value, dict):
                for key, item in list(value.items()):
                    if key == '$ref' and isinstance(item, str) and item.startswith('#/components/'):
                        parts = item.split('/')
                        if len(parts) < 4:
                            raise ValueError('Invalid component reference')
                        parts[3] = provider_id + '__' + parts[3]
                        value[key] = '/'.join(parts)
                    else:
                        rewrite(item)
            elif isinstance(value, list):
                for item in value:
                    rewrite(item)
        rewrite(doc)
        for path, definition in doc.get('paths', {}).items():
            output['paths'][f'/__provider__/{provider_id}{path}'] = definition
        for section, entries in doc.get('components', {}).items():
            output['components'].setdefault(section, {}).update({provider_id + '__' + name: value for name, value in entries.items()})
    return output
