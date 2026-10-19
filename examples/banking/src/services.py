from src.bankclient import accounts, balance, transfer, refund, transactions, beneficiaries


def account_overview():
    return {'accounts': accounts(), 'balance_cents': balance('checking')}


def send_money(source, destination, amount_cents):
    return transfer(source, destination, amount_cents)


def reverse_transfer(transaction_id):
    return refund(transaction_id)


def history():
    return transactions()


def recipients():
    return beneficiaries()
