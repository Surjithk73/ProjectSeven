import httpx
from src import bankclient


def reply(data):
    return httpx.Response(200, json=data, request=httpx.Request('GET', 'https://bank.test'))


def test_balance_preserves_integer_cents(monkeypatch):
    monkeypatch.setattr(httpx, 'get', lambda url: reply({'balance':{'value':123456,'currency':'USD'}}))
    assert bankclient.balance('checking') == 123456


def test_transfer_preserves_exact_amount_and_accounts(monkeypatch):
    def post(url, json):
        assert url == 'https://bank.test/transfers'
        assert json == {'source':'checking','destination':'savings','amount':{'value':1234,'currency':'USD'}}
        return reply({'id':'tx-1','amount_cents':1234})
    monkeypatch.setattr(httpx, 'post', post)
    assert bankclient.transfer('checking','savings',1234)['amount_cents'] == 1234


def test_refund_preserves_transaction_identity(monkeypatch):
    def post(url, json):
        assert url == 'https://bank.test/refunds/create'
        assert json == {'transaction_id':'tx-1'}
        return reply({'refunded':True})
    monkeypatch.setattr(httpx, 'post', post)
    assert bankclient.refund('tx-1')['refunded'] is True


def test_unchanged_accounts_and_history(monkeypatch):
    monkeypatch.setattr(httpx, 'get', lambda url: reply({'accounts':[{'id':'checking'}], 'transactions':[], 'beneficiaries':[]}))
    assert bankclient.accounts() == [{'id':'checking'}]
    assert bankclient.transactions() == []
    assert bankclient.beneficiaries() == []
