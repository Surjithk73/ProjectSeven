import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from mock_provider import main

@pytest.fixture
def provider():
    main.ACTIVE_VERSION = "v1"
    with TestClient(main.app) as client:
        yield client

@pytest.mark.parametrize("version", ["v1", "v2", "v3"])
def test_version_switch_and_complete_matching_contract(provider, version):
    assert provider.post("/api/version", json={"version": version}).status_code == 200
    assert provider.get("/api/version").json()["version"] == version
    spec = provider.get("/api/raw_spec").json()
    assert spec == json.loads((Path(main.__file__).parent / "specs" / f"{version}_spec.json").read_text())
    refund_path = "/refund" if version == "v1" else "/refunds/create"
    assert set(spec["paths"]) == {"/charge", refund_path, "/status/{charge_id}", "/invoice/generate", "/invoice/send", "/invoice/history", "/analytics/log", "/analytics/summary/{user_id}"}
    amount = 5001 if version == "v1" else {"value": 5001, "currency": "USD"}
    charge = provider.post("/charge", json={"amount": amount, "user_id": "customer_9"})
    assert charge.status_code == 200
    assert charge.json()["amount_charged"] == 5001
    assert provider.get("/status/ch_123").json()["charge_id"] == "ch_123"
    assert provider.post(refund_path, json={"transaction_id": "txn_9"}).json()["transaction_id"] == "txn_9"
    wrong_refund = "/refunds/create" if version == "v1" else "/refund"
    assert provider.post(wrong_refund, json={"transaction_id": "txn_9"}).status_code == 404
    payload = {"user_id": "customer_9", "period": "Oct-2026"}
    if version != "v1":
        payload["billing_address"] = {"street": "42 Oak Road", "city": "Pune", "country": "IN"}
    assert provider.post("/invoice/generate", json=payload).status_code == 200
    assert provider.post("/invoice/send", json={"user_id": "customer_9", "invoice_id": "inv_123"}).json()["invoice_id"] == "inv_123"
    assert provider.get("/invoice/history", params={"user": "customer_9"}).json()["user_id"] == "customer_9"
    analytics = provider.post("/analytics/log", json={"event": "paid", "user": "customer_9", "data": {"amount": 5001}}).json()
    assert (analytics if version == "v1" else analytics["data"])["event"] == "paid"
    summary = provider.get("/analytics/summary/customer_9").json()
    assert (summary if version == "v1" else summary["data"])["user_id"] == "customer_9"
    logs = provider.get("/api/provider/logs").json()["logs"]
    assert any(log["path"] == "/charge" and log["status"] == 200 for log in logs)

def test_invalid_version_does_not_change_provider(provider):
    assert provider.post("/api/version", json={"version": "v99"}).status_code == 422
    assert provider.get("/api/version").json()["version"] == "v1"

@pytest.mark.parametrize("amount", [50.01, "5001", True])
@pytest.mark.parametrize("version", ["v1", "v2", "v3"])
def test_amount_is_strict_integer_cents(provider, amount, version):
    provider.post("/api/version", json={"version": version})
    payload = amount if version == "v1" else {"value": amount, "currency": "USD"}
    assert provider.post("/charge", json={"amount": payload, "user_id": "customer_9"}).status_code == 422

@pytest.mark.parametrize("address", [None, {}, "123 Main St", {"street": " ", "city": "Pune", "country": "IN"}])
@pytest.mark.parametrize("version", ["v2", "v3"])
def test_invoice_rejects_missing_or_empty_address(provider, address, version):
    provider.post("/api/version", json={"version": version})
    payload = {"user_id": "customer_9", "period": "Oct-2026", "billing_address": address}
    assert provider.post("/invoice/generate", json=payload).status_code == 422


def test_reset_restores_runnable_v1_clients_and_graph(tmp_path, monkeypatch, provider):
    import importlib.util
    import httpx
    import reset
    from sig_engine import graph_builder
    monkeypatch.setattr(graph_builder, "infer_intent", lambda code: pytest.fail("Reset called paid inference"))
    (tmp_path / "client_app").mkdir()
    (tmp_path / "sig_engine").mkdir()
    (tmp_path / "dashboard_state.json").write_text("stale")
    reset.reset(workspace=tmp_path, switch_provider=False)
    assert not (tmp_path / "dashboard_state.json").exists()
    graph = json.loads((tmp_path / "sig_engine" / "sig_store.json").read_text())
    assert graph["nodes"]
    calls = []
    def post(url, **kwargs):
        calls.append((httpx.URL(url).path, kwargs["json"]))
        response = provider.post(httpx.URL(url).path, json=kwargs["json"])
        return httpx.Response(response.status_code, content=response.content, request=httpx.Request("POST", url))
    monkeypatch.setattr(httpx, "post", post)
    modules = {}
    for name in ("payment_service", "invoice_service", "analytics_service"):
        spec = importlib.util.spec_from_file_location("reset_" + name, tmp_path / "client_app" / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[name] = module
    assert modules["payment_service"].process_monthly_subscription("customer_9", 5001)["amount_charged"] == 5001
    assert modules["payment_service"].process_refund("txn_9")["transaction_id"] == "txn_9"
    assert modules["invoice_service"].generate_monthly_invoice("customer_9", "Oct-2026", billing_address={"street": "42 Oak Road", "city": "Pune", "country": "IN"})["status"] == "success"
    assert modules["analytics_service"].log_transaction_event("paid", "customer_9", {})["status"] == "success"
    assert calls[:3] == [("/charge", {"amount": 5001, "user_id": "customer_9"}), ("/refund", {"transaction_id": "txn_9"}), ("/invoice/generate", {"user_id": "customer_9", "period": "Oct-2026"})]
