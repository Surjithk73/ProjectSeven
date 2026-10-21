import importlib
import sys
from pathlib import Path

import httpx
import httpx2
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[1] / 'demo/movie-client'))


@pytest.fixture
def services(tmp_path):
    from demo.providers.payment import create_app as payment_app
    from demo.providers.theatre import create_app as theatre_app
    from movie_booking.booking import BookingClient
    payment = TestClient(payment_app(tmp_path / 'payment.db'))
    theatre = TestClient(theatre_app(tmp_path / 'theatre.db', payment_client=payment))
    return payment, theatre, BookingClient(theatre, payment)


def test_v1_booking_and_payment_idempotency(services):
    payment, theatre, client = services
    booking = client.book('show-001', ['A1'], 'order-001')
    assert booking['status'] == 'confirmed'
    assert booking['amount_paise'] == 25000
    duplicate = client.book('show-001', ['A1'], 'order-001')
    assert duplicate == booking
    assert len(payment.get('/payments').json()) == 1
    assert theatre.get('/shows/show-001/seats').json()['seats'][0]['available'] is False


@pytest.mark.parametrize('provider_index', [0, 1])
def test_v2_breaks_unchanged_v1_adapter(services, provider_index):
    services[provider_index].post('/admin/version', json={'version': 2}).raise_for_status()
    with pytest.raises((httpx.HTTPStatusError, httpx2.HTTPStatusError, KeyError)):
        services[2].book('show-001', ['A2'], 'order-v2')


def test_gpay_v2_rejects_old_payment_without_taking_money_or_confirming_seats(services):
    payment, theatre, client = services
    payment.post('/admin/version', json={'version':2}).raise_for_status()
    with pytest.raises((httpx.HTTPStatusError, httpx2.HTTPStatusError)) as failure:
        client.book('show-001',['A2'],'gpay-v2-error')
    assert failure.value.response.status_code == 422
    assert failure.value.response.json()['detail'].startswith('Payment failed:')
    assert payment.get('/payments').json() == []
    with theatre.app.state.store.connect() as db:
        assert db.execute('SELECT COUNT(*) FROM holds WHERE result IS NOT NULL').fetchone()[0] == 0


def test_exact_paise_and_key_payload_conflict(services):
    payment, _, _ = services
    body = {'booking_id': 'hold-1', 'amount_paise': 25001, 'currency': 'INR', 'idempotency_key': 'key-1'}
    response = payment.post('/payments', json=body)
    assert response.json()['amount_paise'] == 25001
    assert payment.post('/payments', json={**body, 'amount_paise': 25002}).status_code == 409
    assert payment.post('/payments', json={**body, 'idempotency_key': 'key-2', 'amount_paise': True}).status_code == 422


def test_seats_expired_holds_declines_and_unpaid_confirmation(services):
    payment, theatre, _ = services
    body = {'show_id': 'show-001', 'seat_ids': ['A3'], 'idempotency_key': 'hold-one'}
    hold = theatre.post('/holds', json=body).json()
    assert theatre.post('/holds', json={**body, 'idempotency_key': 'hold-two'}).status_code == 409
    assert theatre.post('/bookings', json={'hold_id': hold['hold_id'], 'payment_id': 'missing'}).status_code == 409
    declined = payment.post('/payments', json={'booking_id': hold['hold_id'], 'amount_paise': hold['amount_paise'],
        'currency': 'INR', 'idempotency_key': 'decline-one', 'simulate_decline': True}).json()
    assert theatre.post('/bookings', json={'hold_id': hold['hold_id'], 'payment_id': declined['payment_id']}).status_code == 409
    with theatre.app.state.store.connect() as db:
        db.execute('UPDATE holds SET expires_at=0')
    assert theatre.post('/bookings', json={'hold_id': hold['hold_id'], 'payment_id': declined['payment_id']}).status_code == 409


def test_active_contract_and_persistent_state(tmp_path):
    from demo.providers.payment import create_app
    path = tmp_path / 'pay.db'
    first = TestClient(create_app(path))
    assert first.post('/admin/version', json={'version': 2}).status_code == 200
    second = TestClient(create_app(path))
    assert second.get('/openapi.json').json()['info']['version'] == '2.0.0'
    assert second.post('/admin/version', json={'version': 7}).status_code == 422


def test_provider_admin_rejects_remote_browser(services):
    app = services[0].app
    remote = TestClient(app, client=('192.168.1.60', 1234))
    assert remote.post('/admin/version', json={'version': 2}).status_code == 403


def test_smoke_checks_browsing_not_only_booking(monkeypatch):
    from movie_booking import app as client_app
    class PartialRepair:
        def __init__(self,*args):
            self.theatre=self
        def list_shows(self):return [{'id':'show-001'}]
        def get_seats(self,show_id):raise KeyError('seats')
        def book(self,*args):return {'status':'confirmed'}
    monkeypatch.setattr(client_app,'BookingClient',PartialRepair)
    client=TestClient(client_app.create_app())
    assert client.post('/internal/smoke').status_code==502
