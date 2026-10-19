import os
import httpx

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8001").rstrip("/")

def process_monthly_subscription(user_id: str, amount_cents: int):
    """Business Intent: Charge the customer's credit card for their monthly subscription."""
    url = f"{API_BASE}/charge"
    payload = {"amount": {"value": amount_cents, "currency": "USD"}, "user_id": user_id}
    try:
        response = httpx.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Payment failed with status {e.response.status_code}: {e.response.text}")
        raise

def process_refund(transaction_id: str):
    """Business Intent: Process a full refund for a returned order."""
    url = f"{API_BASE}/refunds/create"
    payload = {
        "transaction_id": transaction_id
    }
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
