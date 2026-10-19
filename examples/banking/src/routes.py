"""Source-only route definitions for the integration's frontend boundary."""
from fastapi import APIRouter
from src.services import account_overview, send_money, reverse_transfer, history, recipients

app = APIRouter()


@app.get('/api/banking/accounts')
def overview():
    return account_overview()


@app.post('/api/banking/transfer')
def pay(source, destination, amount_cents):
    return send_money(source, destination, amount_cents)


@app.post('/api/banking/refund')
def reverse(transaction_id):
    return reverse_transfer(transaction_id)


@app.get('/api/banking/transactions')
def activity():
    return history()


@app.get('/api/banking/beneficiaries')
def saved_recipients():
    return recipients()
