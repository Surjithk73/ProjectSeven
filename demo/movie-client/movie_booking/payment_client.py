"""Payment V1 adapter. Amounts are exact integer paise, never floating rupees."""
import os
import httpx

PAYMENT_URL = os.environ.get('CINEMA_PAYMENT_URL', 'http://127.0.0.1:8102')


class PaymentClient:
    def __init__(self, client=None):
        self.client = client or httpx.Client(base_url=PAYMENT_URL, timeout=10, trust_env=False)

    def create_payment(self, booking_id, amount_paise, currency, idempotency_key):
        response = self.client.post('/payments', json={'booking_id': booking_id, 'amount_paise': amount_paise,
            'currency': currency, 'idempotency_key': idempotency_key})
        response.raise_for_status()
        return response.json()['payment_id']
