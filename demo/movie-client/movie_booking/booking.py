"""Orchestration preserves show/seat identity and confirms only after payment."""
from .payment_client import PaymentClient
from .theatre_client import TheatreClient


class BookingClient:
    def __init__(self, theatre=None, payment=None):
        self.theatre = TheatreClient(theatre)
        self.payment = PaymentClient(payment)

    def book(self, show_id, seat_ids, idempotency_key):
        hold = self.theatre.hold_seats(show_id, seat_ids, idempotency_key)
        payment_id = self.payment.create_payment(hold['hold_id'], hold['amount_paise'], 'INR', idempotency_key)
        return self.theatre.confirm_booking(hold['hold_id'], payment_id)
