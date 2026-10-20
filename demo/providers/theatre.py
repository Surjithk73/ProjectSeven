"""Independent theatre inventory, seat holds and paid confirmations."""
import json
import os
from pathlib import Path
import time
import uuid

import httpx
from fastapi import Depends, FastAPI, HTTPException

from ..setup import DEMO_ROOT
from .state import Store, fingerprint, local_admin, required_text

SHOWS = [{'id': 'show-001', 'movie': 'The Last Horizon', 'genre': 'Adventure · Sci-Fi',
          'theatre': 'IMAX', 'time': '19:30', 'price_paise': 25000, 'duration': '2h 18m'},
         {'id': 'show-002', 'movie': 'A Little More Summer', 'genre': 'Drama · Romance',
          'theatre': 'IMAX', 'time': '21:00', 'price_paise': 30000, 'duration': '1h 54m'}]


def find_show(show_id):
    # A separate namespace lets deployment verification leave audience seats untouched.
    if show_id.startswith('smoke-') and len(show_id) == 38:
        return {**SHOWS[0], 'id': show_id}
    return next((s for s in SHOWS if s['id'] == show_id), None)


def create_app(database=None, payment_client=None):
    app = FastAPI(title='IMAX · theatre provider', openapi_url=None)
    store = Store(database or Path(os.environ.get('CINEMA_STATE_DIR', DEMO_ROOT / 'providers')) / 'theatre.db')
    app.state.store = store

    @app.get('/health')
    def health():
        return {'status': 'ok', 'provider': 'theatre', 'version': store.version}

    @app.get('/openapi.json')
    def contract():
        return json.loads((Path(__file__).parents[1] / 'contracts' / f'theatre-v{store.version}.json').read_text())

    @app.post('/admin/version', dependencies=[Depends(local_admin)])
    def version(body: dict):
        return store.switch(body.get('version'))

    @app.get('/shows')
    def shows():
        return {'shows': SHOWS}

    @app.get('/shows/{show_id}/seats')
    def seats(show_id: str):
        show = find_show(show_id)
        if not show:
            raise HTTPException(404, 'Show not found')
        with store.connect() as db:
            occupied = {seat for row in db.execute('SELECT seats FROM holds WHERE show_id=? AND (expires_at>? OR payment_id IS NOT NULL)',
                        (show_id, time.time())) for seat in json.loads(row['seats'])}
        values = [{'id': f'{r}{c}', 'available': f'{r}{c}' not in occupied} for r in 'ABCD' for c in range(1, 9)]
        return {'seats': values, 'price_paise': show['price_paise']} if store.version == 1 else {
            'availability': {'show_id': show_id, 'seats': values, 'price': {'value': show['price_paise'], 'currency': 'INR'}}}

    @app.post('/holds')
    def hold(body: dict):
        key = required_text(body, 'idempotency_key')
        show_id = required_text(body, 'show_id')
        selected = body.get('seat_ids')
        show = find_show(show_id)
        valid = {f'{r}{c}' for r in 'ABCD' for c in range(1, 9)}
        if not show or not isinstance(selected, list) or not selected or any(not isinstance(s, str) or s not in valid for s in selected) or len(set(selected)) != len(selected):
            raise HTTPException(422, 'Choose unique seats from a valid show')
        payload = fingerprint({'show_id': show_id, 'seat_ids': sorted(selected)})
        version = store.version
        with store.connect() as db:
            prior = db.execute('SELECT * FROM holds WHERE key=?', (key,)).fetchone()
            if prior:
                if prior['payload'] != payload:
                    raise HTTPException(409, 'Booking key already belongs to another selection')
                if prior['expires_at'] <= time.time() and not prior['payment_id']:
                    raise HTTPException(409, 'Seat hold expired; choose seats again with a new booking key')
                result = {'hold_id': prior['id'], 'amount_paise': prior['amount'], 'expires_at': prior['expires_at']}
            else:
                busy = {seat for row in db.execute('SELECT seats FROM holds WHERE show_id=? AND (expires_at>? OR payment_id IS NOT NULL)',
                        (show_id, time.time())) for seat in json.loads(row['seats'])}
                if busy.intersection(selected):
                    raise HTTPException(409, 'One of these seats is already held or booked')
                result = {'hold_id': uuid.uuid4().hex, 'amount_paise': len(selected) * show['price_paise'], 'expires_at': time.time() + 300}
                db.execute('INSERT INTO holds VALUES (?,?,?,?,?,?,?,?,?)', (result['hold_id'], key, payload, show_id,
                    json.dumps(selected), result['amount_paise'], result['expires_at'], None, None))
        return result if version == 1 else {'hold': {'id': result['hold_id'], 'expires_at': result['expires_at'],
            'total': {'value': result['amount_paise'], 'currency': 'INR'}}}

    @app.post('/bookings')
    def confirm(body: dict):
        values = body if store.version == 1 else body.get('confirmation', {})
        if not isinstance(values, dict):
            raise HTTPException(422, 'V2 requires a confirmation object')
        hold_id, payment_id = required_text(values, 'hold_id'), required_text(values, 'payment_id')
        if payment_client is not None:
            response = payment_client.get('/payments/' + payment_id)
        else:
            with httpx.Client(base_url=os.environ.get('CINEMA_PAYMENT_URL', 'http://127.0.0.1:8102'), timeout=10, trust_env=False) as client:
                response = client.get('/payments/' + payment_id)
        if response.status_code != 200:
            raise HTTPException(409, 'A successful matching payment is required')
        payment = response.json()
        with store.connect() as db:
            row = db.execute('SELECT * FROM holds WHERE id=?', (hold_id,)).fetchone()
            if not row or (row['expires_at'] <= time.time() and not row['payment_id']):
                raise HTTPException(409, 'Seat hold expired or does not exist')
            if payment['status'] != 'succeeded' or payment['booking_id'] != hold_id or payment['amount_paise'] != row['amount'] or payment['currency'] != 'INR':
                raise HTTPException(409, 'Payment amount, booking identity or status does not match the hold')
            if row['payment_id']:
                if row['payment_id'] != payment_id:
                    raise HTTPException(409, 'Booking already confirmed using another payment')
                return json.loads(row['result'])
            result = {'booking_id': hold_id, 'show_id': row['show_id'], 'seat_ids': json.loads(row['seats']),
                      'amount_paise': row['amount'], 'currency': 'INR', 'status': 'confirmed', 'payment_id': payment_id}
            db.execute('UPDATE holds SET payment_id=?,result=? WHERE id=?', (payment_id, json.dumps(result), hold_id))
        return result

    return app
