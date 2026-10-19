"""
reset.py — Run this before every demo to restore the system to its initial state.
"""
import os
from pathlib import Path
import httpx

V1_CLIENT_CODE = '''import os
import httpx

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8001").rstrip("/")

def process_monthly_subscription(user_id: str, amount_cents: int):
    """Business Intent: Charge the customer's credit card for their monthly subscription."""
    url = f"{API_BASE}/charge"
    payload = {"amount": amount_cents, "user_id": user_id}
    try:
        response = httpx.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Payment failed with status {e.response.status_code}: {e.response.text}")
        raise

def process_refund(transaction_id: str):
    """Business Intent: Process a full refund for a returned order."""
    url = f"{API_BASE}/refund"
    payload = {"transaction_id": transaction_id}
    response = httpx.post(url, json=payload, timeout=5.0)
    response.raise_for_status()
    return response.json()

def check_payment_status(charge_id: str):
    """Business Intent: Verify the status of an ongoing payment transaction."""
    url = f"{API_BASE}/status/{charge_id}"
    response = httpx.get(url, timeout=5.0)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Test the client
    print("Attempting to process $50.00 subscription...")
    result = process_monthly_subscription("u_123", 5000)
    print("Result:", result)
'''

V1_INVOICE_CODE = '''import os
import httpx

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8001").rstrip("/")

def generate_monthly_invoice(user_id: str, billing_period: str, billing_address: dict = None):
    """Business Intent: Generate a PDF invoice for the monthly billing cycle."""
    url = f"{API_BASE}/invoice/generate"
    payload = {"user_id": user_id, "period": billing_period}
    response = httpx.post(url, json=payload, timeout=5.0)
    response.raise_for_status()
    return response.json()

def send_invoice_email(user_id: str, invoice_id: str):
    """Business Intent: Email the generated invoice to the customer."""
    url = f"{API_BASE}/invoice/send"
    payload = {"user_id": user_id, "invoice_id": invoice_id}
    response = httpx.post(url, json=payload, timeout=5.0)
    response.raise_for_status()
    return response.json()

def fetch_past_invoices(user_id: str):
    """Business Intent: Retrieve the user's past invoice history."""
    url = f"{API_BASE}/invoice/history"
    response = httpx.get(url, params={"user": user_id}, timeout=5.0)
    response.raise_for_status()
    return response.json()
'''

V1_ANALYTICS_CODE = '''import os
import httpx

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8001").rstrip("/")

def log_transaction_event(event_type: str, user_id: str, metadata: dict):
    """Business Intent: Record an analytics event for a user transaction."""
    url = f"{API_BASE}/analytics/log"
    payload = {"event": event_type, "user": user_id, "data": metadata}
    response = httpx.post(url, json=payload, timeout=5.0)
    response.raise_for_status()
    return response.json()

def get_spending_summary(user_id: str):
    """Business Intent: Retrieve the user's spending summary for the dashboard."""
    url = f"{API_BASE}/analytics/summary/{user_id}"
    response = httpx.get(url, timeout=5.0)
    response.raise_for_status()
    return response.json()
'''

def reset(workspace=None, infer_with_llm=False, switch_provider=True):
    """Restore V1 source and graph; paid inference is an explicit opt-in.

    The default workspace is this script's directory, independent of cwd.
    A running development provider is reset when available. Provider restart
    should use API_VERSION=v1 if no server is running during reset.
    """
    root = Path(workspace).resolve() if workspace is not None else Path(__file__).resolve().parent
    print("Resetting system to initial V1 state...")
    for filename, code in (("payment_service.py", V1_CLIENT_CODE),
                           ("invoice_service.py", V1_INVOICE_CODE),
                           ("analytics_service.py", V1_ANALYTICS_CODE)):
        (root / "client_app" / filename).write_text(code, encoding="utf-8")
        print(f"  [OK] client_app/{filename} restored to V1")
    (root / "dashboard_state.json").unlink(missing_ok=True)
    (root / "agent" / "result.json").unlink(missing_ok=True)
    from sig_engine.graph_builder import build_sig
    build_sig(client_dir=str(root / "client_app"),
              output_path=str(root / "sig_engine" / "sig_store.json"),
              infer_with_llm=infer_with_llm)
    if switch_provider:
        base = os.getenv("API_BASE", "http://127.0.0.1:8001").rstrip("/")
        try:
            response = httpx.post(f"{base}/api/version", json={"version": "v1"}, timeout=5.0)
            response.raise_for_status()
        except httpx.HTTPError as error:
            print(f"  Provider was not reset: {error}. Start it with API_VERSION=v1.")
    print("V1 clients and graph restored. Start the provider in V1 mode before the demo.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Restore the local demonstration to V1")
    parser.add_argument("--infer-with-llm", action="store_true", help="Explicitly enable paid intent inference")
    parser.add_argument("--no-provider-switch", action="store_true", help="Restore source/graph without contacting the provider")
    args = parser.parse_args()
    reset(infer_with_llm=args.infer_with_llm, switch_provider=not args.no_provider_switch)
