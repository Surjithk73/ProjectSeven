"""User-requested prewritten CinemaFlow demo hints, excluded from unseeded runs.

These are prompt references, never an automatic or fallback patch applicator.
"""

PAYMENT_FILE = 'movie_booking/payment_client.py'
THEATRE_FILE = 'movie_booking/theatre_client.py'

REFERENCES = [
    ('payment', '/payments', 'post', 'requestBody', 'amount', PAYMENT_FILE,
     """    def create_payment(self, booking_id, amount_paise, currency, idempotency_key):
        response = self.client.post('/payments', json={'booking_id': booking_id, 'amount_paise': amount_paise,
            'currency': currency, 'idempotency_key': idempotency_key})
        response.raise_for_status()
        return response.json()['payment_id']""",
     """    def create_payment(self, booking_id, amount_paise, currency, idempotency_key):
        response = self.client.post('/payments', json={'booking_id': booking_id,
            'amount': {'value': amount_paise, 'currency': currency}, 'idempotency_key': idempotency_key})
        response.raise_for_status()
        return response.json()['payment']['id']"""),
    ('theatre', '/shows/{show_id}/seats', 'get', 'responses', 'availability', THEATRE_FILE,
     """    def get_seats(self, show_id):
        response = self.client.get(f'/shows/{show_id}/seats')
        response.raise_for_status()
        return response.json()['seats']""",
     """    def get_seats(self, show_id):
        response = self.client.get(f'/shows/{show_id}/seats')
        response.raise_for_status()
        return response.json()['availability']['seats']"""),
    ('theatre', '/holds', 'post', 'responses', 'hold', THEATRE_FILE,
     """    def hold_seats(self, show_id, seat_ids, idempotency_key):
        response = self.client.post('/holds', json={'show_id': show_id, 'seat_ids': seat_ids, 'idempotency_key': idempotency_key})
        response.raise_for_status()
        return response.json()""",
     """    def hold_seats(self, show_id, seat_ids, idempotency_key):
        response = self.client.post('/holds', json={'show_id': show_id, 'seat_ids': seat_ids, 'idempotency_key': idempotency_key})
        response.raise_for_status()
        data = response.json()
        hold = data['hold']
        return {**data, 'hold_id': hold['id'], 'amount_paise': hold['total']['value'],
                'expires_at': hold['expires_at']}"""),
    ('theatre', '/bookings', 'post', 'requestBody', 'confirmation', THEATRE_FILE,
     """    def confirm_booking(self, hold_id, payment_id):
        response = self.client.post('/bookings', json={'hold_id': hold_id, 'payment_id': payment_id})
        response.raise_for_status()
        return response.json()""",
     """    def confirm_booking(self, hold_id, payment_id):
        response = self.client.post('/bookings', json={'confirmation': {'hold_id': hold_id, 'payment_id': payment_id}})
        response.raise_for_status()
        return response.json()"""),
]


def reference_patches(context, workflow):
    if not workflow or workflow.get('project_id') != 'cinemaflow' or workflow.get('repository', '').casefold() != 'surjithk73/apiguardtesting':
        return []
    patches = []
    paths = context['target_spec'].get('paths', {})
    for provider, path, method, side, field, file, old, new in REFERENCES:
        if file not in context['allowed_files'] or context['sources'].get(file, '').count(old) != 1:
            continue
        operation = paths.get(f'/__provider__/{provider}{path}', {}).get(method, {})
        body = operation.get(side, {})
        if side == 'responses':
            body = body.get('200', {})
        schema = body.get('content', {}).get('application/json', {}).get('schema', {})
        if field in schema.get('properties', {}):
            patches.append({'file': file, 'old_code_snippet': old, 'new_code_snippet': new})
    return patches
