import pytest
import httpx
from unittest.mock import patch, MagicMock
from client_app.payment_service import process_monthly_subscription


def make_mock_response(payload: dict):
    """Creates a mock httpx response that returns success."""
    amount = payload.get("amount", 0)
    amount_charged = amount.get("value", 0) if isinstance(amount, dict) else amount
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "status": "success",
        "charge_id": "ch_v2_001",
        "amount_charged": amount_charged,
    }
    return mock_resp


def test_payload_is_v2_format():
    """
    After agent repair, payment_service.py must send amount as a
    {value, currency} object — not a flat integer. This test verifies
    the repaired code structure WITHOUT needing the server to be up.
    """
    captured_payload = {}

    def mock_post(url, json=None, timeout=None):
        captured_payload.update(json or {})
        return make_mock_response(json or {})

    with patch.object(httpx, "post", side_effect=mock_post):
        result = process_monthly_subscription("u_123", 5000)

    # 1. Call must succeed
    assert result.get("status") == "success", f"Expected success, got: {result}"

    # 2. The amount field must now be a dict (V2 format) — not an int (V1 format)
    amount = captured_payload.get("amount")
    assert isinstance(amount, dict), (
        f"AGENT REPAIR FAILED: 'amount' should be a dict in V2 format but got {type(amount).__name__}: {amount!r}"
    )

    # 3. The dict must have 'value' and 'currency'
    assert "value" in amount, f"Missing 'value' key in amount: {amount}"
    assert "currency" in amount, f"Missing 'currency' key in amount: {amount}"

    # 4. Value must be the original amount in cents
    assert amount["value"] == 5000, f"Expected amount.value=5000, got {amount['value']}"

    print(f"\n[TEST PASSED] Payload is correctly in V2 format: {captured_payload}")
