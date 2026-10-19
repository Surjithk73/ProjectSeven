"""Public regression tests also run in the deployment repository's CI."""
import httpx
from movie_booking.booking import BookingClient


def test_booking_preserves_exact_amount_destination_and_key():
    seen = []
    def theatre(request):
        import json
        body = json.loads(request.content)
        seen.append((request.url.path, body))
        if request.url.path == '/holds':
            return httpx.Response(200, json={'hold_id': 'hold-001', 'amount_paise': 25001})
        return httpx.Response(200, json={'status': 'confirmed', 'booking_id': body.get('hold_id', body.get('confirmation', {}).get('hold_id'))})
    def payment(request):
        import json
        body = json.loads(request.content)
        assert body['booking_id'] == 'hold-001'
        assert body['idempotency_key'] == 'order-123'
        amount = body.get('amount_paise', body.get('amount', {}).get('value'))
        currency = body.get('currency', body.get('amount', {}).get('currency'))
        assert amount == 25001 and currency == 'INR'
        return httpx.Response(200, json={'payment_id': 'payment-001'})
    client = BookingClient(httpx.Client(transport=httpx.MockTransport(theatre), base_url='http://theatre'),
                           httpx.Client(transport=httpx.MockTransport(payment), base_url='http://payment'))
    assert client.book('show-001', ['A1'], 'order-123')['status'] == 'confirmed'
    assert seen[0][1]['show_id'] == 'show-001'
    assert seen[0][1]['seat_ids'] == ['A1']
