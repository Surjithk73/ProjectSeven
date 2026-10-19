"""Read-only overview of retained original and updated API contracts."""
import hashlib
import json
from .comparison import _operations
from .commands import redact_data


def contract_overview(base, target):
    if any(not isinstance(spec.get('info', {}), dict) for spec in (base, target)):
        raise ValueError('Invalid API information metadata')
    old, new = _operations(base), _operations(target)
    def snapshot(spec, operations):
        return {'info':spec.get('info',{}), 'components':spec.get('components',{}), 'operations':[{'method':method,'endpoint':endpoint,
                'definition':definition['operation'],'path_settings':definition['path_settings']}
                for (method, endpoint), definition in sorted(operations.items())]}
    shared_changed = any(base.get(k) != target.get(k) for k in ('components','security','servers'))
    changes = [{'method':method,'endpoint':endpoint,'status':'added' if key not in old else 'removed' if key not in new else 'changed',
                'before':old.get(key), 'after':new.get(key)}
               for key in sorted(set(old)|set(new)) for method, endpoint in [key]
               if old.get(key)!=new.get(key)]
    return {'before':snapshot(base,old),'after':snapshot(target,new),'changes':changes,
            'shared_changes':{k:{'before':base.get(k),'after':target.get(k)} for k in ('components','security','servers') if base.get(k)!=target.get(k)},
            'metadata_changes':{k:{'before':base.get('info',{}).get(k),'after':target.get('info',{}).get(k)} for k in set(base.get('info',{}))|set(target.get('info',{})) if base.get('info',{}).get(k)!=target.get('info',{}).get(k)},
            'shared_changed':shared_changed}


def retained_overview(path, report):
    specs=[]
    try:
        for name in ('base','target'):
            file=path/'contracts'/f'{name}.json'
            if file.is_symlink() or file.stat().st_size > 8*1024*1024:
                raise ValueError('Retained contract cannot be displayed safely')
            content=file.read_bytes()
            if hashlib.sha256(content).hexdigest()!=report.get(f'{name}_spec_hash'):
                raise ValueError('Retained contract differs from the recorded hash')
            specs.append(json.loads(content))
        return redact_data(contract_overview(*specs))
    except (OSError,ValueError,TypeError):
        return {'unavailable':'Original API contract details are unavailable for this run; source findings remain below.'}
