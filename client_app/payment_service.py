import httpx

def process_monthly_subscription(user_id: str, amount_cents: int):
    """
    Business Intent: Charge the customer's credit card for their monthly subscription.
    """
    url = "http://127.0.0.1:8002/charge"
    
    # We are calling the mock FinTech API
    payload = {
        "amount": amount_cents,
        "user_id": user_id
    }
    
    try:
        response = httpx.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Payment failed with status {e.response.status_code}: {e.response.text}")
        raise
    except Exception as e:
        print(f"Network error: {e}")
        raise

if __name__ == "__main__":
    # Test the client
    print("Attempting to process $50.00 subscription...")
    result = process_monthly_subscription("u_123", 5000)
    print("Result:", result)
