"""In-memory banking demonstration. No credentials, external calls or real funds."""
from copy import deepcopy
from pathlib import Path
import json
import threading
import types
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from typing import Literal
from .browser_setup import local_browser

FIXTURE = Path(__file__).resolve().parents[1] / 'examples/banking'


class BankingDemo:
    def __init__(self):
        self.version, self.repaired = 'v1', False
        self.adapter_root = None
        self.accounts = [{'id':'checking','name':'Everyday account','balance_cents':125000},
                         {'id':'savings','name':'Savings','balance_cents':300000}]
        self.transactions = []
        self.lock = threading.RLock()

    def snapshot(self):
        with self.lock:
            return deepcopy({'version':self.version, 'repaired':self.repaired,
                             'accounts':self.accounts, 'transactions':self.transactions})

    def provider(self, request):
        path, method = request.url.path, request.method
        body = json.loads(request.content) if request.content else {}
        def response(status, data):
            return httpx.Response(status, json=data, request=request)
        with self.lock:
            if method == 'GET' and path == '/accounts':
                return response(200, {'accounts':deepcopy(self.accounts)})
            if method == 'GET' and path.startswith('/accounts/') and path.endswith('/balance'):
                account = next((a for a in self.accounts if a['id'] == path.split('/')[2]), None)
                if not account:
                    return response(404, {'detail':'Account not found'})
                value = account['balance_cents']
                return response(200, {'balance_cents':value} if self.version == 'v1' else {'balance':{'value':value,'currency':'USD'}})
            if method == 'GET' and path == '/transactions':
                return response(200, {'transactions':deepcopy(self.transactions)})
            if method == 'GET' and path == '/beneficiaries':
                return response(200, {'beneficiaries':[{'id':'savings','name':'Savings'}]})
            if method == 'POST' and path == '/transfers':
                amount = body.get('amount_cents') if self.version == 'v1' else body.get('amount', {}).get('value')
                if self.version == 'v2' and body.get('amount', {}).get('currency') != 'USD':
                    return response(422, {'detail':'V2 requires amount.value in cents and amount.currency=USD'})
                accounts = {a['id']:a for a in self.accounts}
                source, destination = accounts.get(body.get('source')), accounts.get(body.get('destination'))
                if type(amount) is not int or amount <= 0 or not source or not destination or source is destination or source['balance_cents'] < amount:
                    return response(422, {'detail':'Choose different accounts and a positive affordable amount in cents'})
                source['balance_cents'] -= amount; destination['balance_cents'] += amount
                tx = {'id':f'tx-{len(self.transactions)+1}', 'source':source['id'], 'destination':destination['id'], 'amount_cents':amount,'refunded':False}
                self.transactions.append(tx)
                return response(200, deepcopy(tx))
            refund_path = '/refunds' if self.version == 'v1' else '/refunds/create'
            if method == 'POST' and path == refund_path:
                tx = next((t for t in self.transactions if t['id'] == body.get('transaction_id')), None)
                accounts = {a['id']:a for a in self.accounts}
                if not tx or tx['refunded'] or accounts[tx['destination']]['balance_cents'] < tx['amount_cents']:
                    return response(422, {'detail':'Transfer cannot be refunded again or funds are unavailable'})
                accounts[tx['destination']]['balance_cents'] -= tx['amount_cents']
                accounts[tx['source']]['balance_cents'] += tx['amount_cents']
                tx['refunded'] = True
                return response(200, deepcopy(tx))
            return response(404, {'detail':'Endpoint not found in this provider version'})

    def call(self, name, *args):
        # Only the shipped adapter and shipped candidate are used by this demo.
        source = ((self.adapter_root or FIXTURE) / 'src/bankclient.py').read_text(encoding='utf-8')
        if self.repaired and self.adapter_root is None:
            for patch in json.loads((FIXTURE / 'candidate.json').read_text())['patches']:
                source = source.replace(patch['old_code_snippet'], patch['new_code_snippet'])
        module = types.ModuleType('bank_demo_adapter')
        exec(compile(source, 'bank_demo_adapter', 'exec'), module.__dict__)
        with self.lock, httpx.Client(transport=httpx.MockTransport(self.provider)) as client:
            module.httpx = client
            return getattr(module, name)(*args)

    def transfer(self, source, destination, amount_cents):
        return self.call('transfer', source, destination, amount_cents)

    def refund(self, transaction_id):
        return self.call('refund', transaction_id)


demo = BankingDemo()
router = APIRouter(prefix='/api/banking', dependencies=[Depends(local_browser)])


def active_contract():
    with demo.lock:
        return json.loads((FIXTURE / ('base.json' if demo.version == 'v1' else 'target.json')).read_text())


@router.get('/openapi')
def documentation():
    return active_contract()


class Transfer(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source: Literal['checking','savings']
    destination: Literal['checking','savings']
    amount_cents: StrictInt = Field(gt=0, le=100000000)


class Refund(BaseModel):
    model_config = ConfigDict(extra='forbid')
    transaction_id: str = Field(min_length=1, max_length=64)


class Controls(BaseModel):
    model_config = ConfigDict(extra='forbid')
    version: Literal['v1','v2']
    adapter: Literal['original'] = 'original'


def invoke(name, *args):
    try:
        return demo.call(name, *args)
    except (httpx.HTTPStatusError, KeyError) as error:
        detail = error.response.json().get('detail') if isinstance(error, httpx.HTTPStatusError) else 'V2 changed the balance response shape'
        raise HTTPException(422, detail) from None


@router.get('/state')
def state(request: Request):
    from .dashboard_jobs import service
    from .configuration import load_config
    jobs = service(request)
    if 'banking-example' in jobs.integrations:
        root = load_config(jobs.integrations['banking-example']).repository
        with demo.lock:
            demo.adapter_root = root
            demo.repaired = (root / 'src/bankclient.py').read_bytes() != (FIXTURE / 'src/bankclient.py').read_bytes()
    return demo.snapshot()


@router.post('/controls')
def controls(body: Controls):
    with demo.lock:
        demo.version = body.version
    return demo.snapshot()


@router.post('/reset')
def reset(request: Request):
    from .dashboard_jobs import service
    from .configuration import load_config
    from .jobs import _atomic_bytes, atomic_json
    from .current_api import capture_api_context
    jobs = service(request)
    root = load_config(jobs.integrations['banking-example']).repository if 'banking-example' in jobs.integrations else None
    with demo.lock:
        if root:
            source = root / 'src/bankclient.py'
            if source.is_symlink():
                raise HTTPException(409, 'Unsafe demo adapter path')
            _atomic_bytes(source, (FIXTURE / 'src/bankclient.py').read_bytes())
        demo.adapter_root = root
        fresh = BankingDemo()
        demo.version, demo.repaired = fresh.version, fresh.repaired
        demo.accounts, demo.transactions = fresh.accounts, fresh.transactions
    if root:
        context = capture_api_context(jobs, 'banking-example')
        atomic_json(jobs.store.root / '_current_api/banking-example/state.json',
                    {'config_identity': context['config_identity'], 'accepted_hash': context['observed_hash']})
    return demo.snapshot()


@router.get('/accounts')
def accounts():
    return {'accounts':invoke('accounts'), 'balance_cents':invoke('balance','checking')}


@router.get('/transactions')
def transactions():
    return invoke('transactions')


@router.get('/beneficiaries')
def beneficiaries():
    return invoke('beneficiaries')


@router.post('/transfer')
def transfer(body: Transfer):
    return invoke('transfer', body.source, body.destination, body.amount_cents)


@router.post('/refund')
def refund(body: Refund):
    return invoke('refund', body.transaction_id)
