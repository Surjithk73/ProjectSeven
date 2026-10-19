"""GPay-style simulated payment provider with intentionally incompatible V2."""
import json
import os
from pathlib import Path
import uuid

from fastapi import Depends, FastAPI, HTTPException

from ..setup import DEMO_ROOT
from .state import Store, fingerprint, local_admin, required_text


def create_app(database=None):
    app = FastAPI(title='CinemaPay · simulated payments', openapi_url=None)
    store = Store(database or Path(os.environ.get('CINEMA_STATE_DIR', DEMO_ROOT / 'providers')) / 'payment.db')
    app.state.store = store

    @app.get('/health')
    def health():
        return {'status': 'ok', 'provider': 'payment', 'version': store.version, 'simulated': True}

    @app.get('/openapi.json')
    def contract():
        return json.loads((Path(__file__).parents[1] / 'contracts' / f'payment-v{store.version}.json').read_text())

    @app.post('/admin/version', dependencies=[Depends(local_admin)])
    def version(body: dict):
        return store.switch(body.get('version'))

    @app.get('/payments')
    def payments():
        with store.connect() as db:
            return [json.loads(row['result']) for row in db.execute('SELECT result FROM payments')]

    @app.get('/payments/{payment_id}')
    def status(payment_id: str):
        with store.connect() as db:
            row = db.execute('SELECT result FROM payments WHERE id=?', (payment_id,)).fetchone()
            if not row:
                raise HTTPException(404, 'Payment not found')
            return json.loads(row['result'])

    @app.post('/payments')
    def create(body: dict):
        store_version = store.version
        key = required_text(body, 'idempotency_key')
        booking_id = required_text(body, 'booking_id')
        if store_version == 1:
            amount, currency = body.get('amount_paise'), body.get('currency')
        else:
            money = body.get('amount', {})
            if not isinstance(money, dict):
                raise HTTPException(422, 'V2 requires amount.value in paise and amount.currency=INR')
            amount, currency = money.get('value'), money.get('currency')
        if type(amount) is not int or amount <= 0 or amount > 100_000_000 or currency != 'INR':
            raise HTTPException(422, 'An exact positive integer amount in paise and INR currency are required')
        payload = fingerprint({'booking_id': booking_id, 'amount_paise': amount, 'currency': currency,
                               'simulate_decline': bool(body.get('simulate_decline', False))})
        with store.connect() as db:
            prior = db.execute('SELECT payload,result FROM payments WHERE key=?', (key,)).fetchone()
            if prior:
                if prior['payload'] != payload:
                    raise HTTPException(409, 'Idempotency key was already used with different payment details')
                return present(json.loads(prior['result']), store_version)
            result = {'payment_id': uuid.uuid4().hex, 'booking_id': booking_id, 'amount_paise': amount,
                      'currency': currency, 'status': 'declined' if body.get('simulate_decline') else 'succeeded'}
            db.execute('INSERT INTO payments VALUES (?,?,?,?)', (result['payment_id'], key, payload, json.dumps(result)))
        return present(result, store_version)

    # Read version before entering a SQLite transaction to avoid a nested connection lock.
    # Idempotent results retain canonical evidence while the API presents its current shape.
    def present(result, version):
        return result if version == 1 else {'payment': {'id': result['payment_id'], 'state': result['status'],
            'booking_id': result['booking_id'], 'amount': {'value': result['amount_paise'], 'currency': result['currency']}}}

    return app
