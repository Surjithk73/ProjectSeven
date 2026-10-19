import os
import httpx

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8001").rstrip("/")

def log_transaction_event(event_type: str, user_id: str, metadata: dict):
    """Business Intent: Record an analytics event for a user transaction."""
    url = f"{API_BASE}/analytics/log"
    payload = {"event": event_type, "user": user_id, "data": metadata}
    response = httpx.post(url, json=payload, timeout=5.0)
    response.raise_for_status()
    return response.json()["data"]

def get_spending_summary(user_id: str):
    """Business Intent: Retrieve the user's spending summary for the dashboard."""
    url = f"{API_BASE}/analytics/summary/{user_id}"
    response = httpx.get(url, timeout=5.0)
    response.raise_for_status()
    return response.json()["data"]
