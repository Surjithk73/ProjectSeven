import os
import httpx

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8001").rstrip("/")

def generate_monthly_invoice(user_id: str, billing_period: str, billing_address: dict = None):
    """Business Intent: Generate a PDF invoice for the monthly billing cycle."""
    url = f"{API_BASE}/invoice/generate"
    payload = {"user_id": user_id, "period": billing_period, "billing_address": billing_address}
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
