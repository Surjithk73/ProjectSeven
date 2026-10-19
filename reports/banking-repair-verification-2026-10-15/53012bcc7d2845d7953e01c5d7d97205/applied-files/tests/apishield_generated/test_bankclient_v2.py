from unittest.mock import patch
import httpx
from src import bankclient

def test_v2_balance_handling():
    v2_response = httpx.Response(200, json={"balance": {"value": 5000, "currency": "USD"}}, request=httpx.Request("GET", "https://bank.test/accounts/acc1/balance"))
    with patch("httpx.get", return_value=v2_response) as mock_get:
        res = bankclient.balance("acc1")
        mock_get.assert_called_once_with("https://bank.test/accounts/acc1/balance")
        assert res == 5000

def test_v2_transfer_payload_format():
    v2_response = httpx.Response(200, json={"id": "t1", "source": "acc1", "destination": "acc2", "amount_cents": 2500, "refunded": False}, request=httpx.Request("POST", "https://bank.test/transfers"))
    with patch("httpx.post", return_value=v2_response) as mock_post:
        res = bankclient.transfer("acc1", "acc2", 2500)
        assert mock_post.call_count == 1
        call_args, call_kwargs = mock_post.call_args
        assert call_args[0] == "https://bank.test/transfers"
        assert call_kwargs.get("json") == {"source": "acc1", "destination": "acc2", "amount": {"value": 2500, "currency": "USD"}}
        assert res["amount_cents"] == 2500

def test_v2_refund_endpoint():
    v2_response = httpx.Response(200, json={"id": "r1", "source": "acc1", "destination": "acc2", "amount_cents": 2500, "refunded": True}, request=httpx.Request("POST", "https://bank.test/refunds/create"))
    with patch("httpx.post", return_value=v2_response) as mock_post:
        res = bankclient.refund("tx-123")
        mock_post.assert_called_once_with("https://bank.test/refunds/create", json={"transaction_id": "tx-123"})
        assert res["refunded"] is True
