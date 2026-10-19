import os
from client_app import payment_service

def test_payload_is_v2_format(provider_http):
    """A unit conversion, wrong customer or charge substitution fails this check."""
    result = payment_service.process_monthly_subscription("customer_9", 5001)
    assert result["status"] == "success"
    assert result["amount_charged"] == 5001
    assert result["user_id"] == "customer_9"
    logs = provider_http.get("/api/provider/logs").json()["logs"]
    charge = next(log for log in logs if log["path"] == "/charge")
    expected = 5001 if os.getenv("API_VERSION", "v2") == "v1" else {"value": 5001, "currency": "USD"}
    assert charge["payload"] == {"amount": expected, "user_id": "customer_9"}

def test_check_payment_status():
    assert payment_service.check_payment_status("ch_9") == {"status": "success", "charge_id": "ch_9", "payment_status": "paid"}
