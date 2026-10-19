"""V1 integration. Tests target V2 to expose required migration changes."""
import httpx

API_BASE = 'https://bank.test'


def accounts():
    """Business Intent: List the customer's accounts."""
    response = httpx.get(f'{API_BASE}/accounts')
    response.raise_for_status()
    return response.json()['accounts']


def balance(account_id):
    """Business Intent: Read an account balance in exact integer cents."""
    response = httpx.get(f'{API_BASE}/accounts/{account_id}/balance')
    response.raise_for_status()
    return response.json()['balance']['value']


def transfer(source, destination, amount_cents):
    """Business Intent: Move exact cents between accounts without losing money."""
    response = httpx.post(f'{API_BASE}/transfers', json={'source': source, 'destination': destination, 'amount': {'value': amount_cents, 'currency': 'USD'}})
    response.raise_for_status()
    return response.json()


def transactions():
    """Business Intent: Read transaction history."""
    response = httpx.get(f'{API_BASE}/transactions')
    response.raise_for_status()
    return response.json()['transactions']


def refund(transaction_id):
    """Business Intent: Reverse a transfer exactly once."""
    response = httpx.post(f'{API_BASE}/refunds/create', json={'transaction_id': transaction_id})
    response.raise_for_status()
    return response.json()


def beneficiaries():
    """Business Intent: List saved transfer recipients."""
    response = httpx.get(f'{API_BASE}/beneficiaries')
    response.raise_for_status()
    return response.json()['beneficiaries']
