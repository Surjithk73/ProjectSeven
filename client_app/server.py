from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import importlib
import uvicorn
import os
import sys

# Ensure parent dir is on path so client_app can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="SwiftPay BFF")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory transaction store
transactions = []

def get_payment_fn():
    """
    Dynamically reload payment_service on every call so changes made
    by the APIShield agent are picked up instantly — no server restart needed.
    """
    import client_app.payment_service as ps
    importlib.reload(ps)
    return ps.process_monthly_subscription

@app.get("/api/transactions")
def get_transactions():
    return {"transactions": transactions}

@app.post("/api/pay")
def process_payment():
    tx = {
        "id": f"tx_{len(transactions) + 1}",
        "timestamp": datetime.now().isoformat(),
        "amount": "$50.00",
        "description": "Monthly Subscription"
    }

    try:
        process_monthly_subscription = get_payment_fn()
        result = process_monthly_subscription("u_123", 5000)

        tx["status"] = "success"
        transactions.insert(0, tx)
        return {"status": "success", "data": result}

    except Exception as e:
        error_msg = str(e)
        if hasattr(e, "response"):
            error_msg = f"{e.response.status_code} - Schema Mismatch"

        tx["status"] = "failed"
        tx["error"] = error_msg
        transactions.insert(0, tx)

        raise HTTPException(status_code=422, detail=error_msg)

def get_refund_fn():
    import client_app.payment_service as ps
    importlib.reload(ps)
    return ps.process_refund

def get_invoice_fn():
    import client_app.invoice_service as i_s
    importlib.reload(i_s)
    return i_s.generate_monthly_invoice

def get_analytics_fn():
    import client_app.analytics_service as a_s
    importlib.reload(a_s)
    return a_s.get_spending_summary

@app.post("/api/refund")
def process_refund():
    tx = {
        "id": f"tx_{len(transactions) + 1}",
        "timestamp": datetime.now().isoformat(),
        "amount": "-$50.00",
        "description": "Refund Processed"
    }

    try:
        process_refund_fn = get_refund_fn()
        result = process_refund_fn("tx_000")

        tx["status"] = "success"
        transactions.insert(0, tx)
        return {"status": "success", "data": result}
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, "response"):
            error_msg = f"{e.response.status_code} - Schema Mismatch"

        tx["status"] = "failed"
        tx["error"] = error_msg
        transactions.insert(0, tx)

        raise HTTPException(status_code=422, detail=error_msg)

class InvoiceInput(BaseModel):
    user_id: str = "u_123"
    billing_period: str = "Sep-2026"
    billing_address: dict | None = None

@app.post("/api/invoice/generate")
def generate_invoice(request: InvoiceInput):
    try:
        generate_fn = get_invoice_fn()
        result = generate_fn(request.user_id, request.billing_period, billing_address=request.billing_address)
        return {"status": "success", "data": result}
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, "response"):
            error_msg = f"{e.response.status_code} - Schema Mismatch"
        raise HTTPException(status_code=422, detail=error_msg)

@app.get("/api/analytics/summary/{user_id}")
def get_analytics(user_id: str):
    try:
        get_summary = get_analytics_fn()
        result = get_summary(user_id)
        return {"status": "success", "data": result}
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, "response"):
            error_msg = f"{e.response.status_code} - Schema Mismatch"
        raise HTTPException(status_code=422, detail=error_msg)

if __name__ == "__main__":
    print("Starting SwiftPay BFF Server on port 8003...")
    print("NOTE: reload=False — payment_service.py changes are picked up dynamically per-request.")
    uvicorn.run("server:app", host="127.0.0.1", port=8003, reload=False)
