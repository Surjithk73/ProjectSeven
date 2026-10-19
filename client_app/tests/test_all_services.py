import os
import httpx
import pytest
from fastapi.testclient import TestClient
from client_app import analytics_service, invoice_service, payment_service, server
ADDRESS = {"street": "42 Oak Road", "city": "Pune", "country": "IN"}

def test_process_refund(provider_http):
    result = payment_service.process_refund("txn_999")
    assert result == {"status": "success", "refund_id": "rf_123", "transaction_id": "txn_999"}
    logs = provider_http.get("/api/provider/logs").json()["logs"]
    path = "/refund" if os.getenv("API_VERSION", "v2") == "v1" else "/refunds/create"
    assert any(log["path"] == path and log["payload"] == {"transaction_id": "txn_999"} for log in logs)
    assert not any(log["path"] == "/charge" for log in logs)

def test_generate_monthly_invoice_preserves_customer_data(provider_http):
    result = invoice_service.generate_monthly_invoice("customer_9", "Oct-2026", billing_address=ADDRESS)
    assert result["status"] == "success"
    assert result["invoice_id"] == "inv_123"
    log = next(log for log in provider_http.get("/api/provider/logs").json()["logs"] if log["path"] == "/invoice/generate")
    expected = {"user_id": "customer_9", "period": "Oct-2026"}
    if os.getenv("API_VERSION", "v2") != "v1":
        expected["billing_address"] = ADDRESS
    assert log["payload"] == expected

def test_invoice_missing_address_fails_in_v2():
    if os.getenv("API_VERSION", "v2") == "v1":
        assert invoice_service.generate_monthly_invoice("customer_9", "Oct-2026")["status"] == "success"
    else:
        with pytest.raises((ValueError, httpx.HTTPStatusError)):
            invoice_service.generate_monthly_invoice("customer_9", "Oct-2026")

def test_invoice_send_and_history():
    assert invoice_service.send_invoice_email("customer_9", "inv_9")["invoice_id"] == "inv_9"
    assert invoice_service.fetch_past_invoices("customer_9")["user_id"] == "customer_9"

def test_log_transaction_event():
    assert analytics_service.log_transaction_event("subscription_paid", "customer_9", {"amount": 5001}) == {"status": "success", "event": "subscription_paid", "user_id": "customer_9", "metadata": {"amount": 5001}}

def test_spending_summary_unwraps_provider_data():
    assert analytics_service.get_spending_summary("customer_9") == {"user_id": "customer_9", "total_spent": 5000, "currency": "USD"}

def test_analytics_does_not_fabricate_success(monkeypatch):
    envelope = {"status": "failed", "event": "declined", "user_id": "customer_9", "metadata": {}}
    wrapped = envelope if os.getenv("API_VERSION", "v2") == "v1" else {"data": envelope}
    def post(url, **kwargs):
        return httpx.Response(200, json=wrapped, request=httpx.Request("POST", url))
    monkeypatch.setattr(httpx, "post", post)
    assert analytics_service.log_transaction_event("declined", "customer_9", {}) == envelope

def test_bff_passes_caller_invoice_address():
    with TestClient(server.app) as bff:
        result = bff.post("/api/invoice/generate", json={"user_id": "customer_9", "billing_period": "Oct-2026", "billing_address": ADDRESS})
    assert result.status_code == 200
    assert result.json()["data"]["user_id"] == "customer_9"
