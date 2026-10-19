"""Canonical NexusPay demonstration provider (port 8001).

Version contracts and exported fixtures come from the same typed applications.
The control endpoints are development-only; switching is in-memory and restart
uses API_VERSION (v1 by default).
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Literal
from fastapi import FastAPI, Request
from pydantic import BaseModel, ConfigDict, StrictInt, StringConstraints

ACTIVE_VERSION = os.getenv("API_VERSION", "v1")
if ACTIVE_VERSION not in {"v1", "v2", "v3"}:
    raise ValueError("API_VERSION must be v1, v2, or v3")
NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")

class ChargeRequestV1(Contract):
    amount: StrictInt
    user_id: NonEmpty

class CurrencyAmount(Contract):
    value: StrictInt
    currency: NonEmpty

class ChargeRequestV2(Contract):
    amount: CurrencyAmount
    user_id: NonEmpty

class ChargeRequestV3(ChargeRequestV2):
    send_email_receipt: bool = False

class RefundRequest(Contract):
    transaction_id: NonEmpty

class BillingAddress(Contract):
    street: NonEmpty
    city: NonEmpty
    country: NonEmpty

class InvoiceRequestV1(Contract):
    user_id: NonEmpty
    period: NonEmpty

class InvoiceRequestV2(InvoiceRequestV1):
    billing_address: BillingAddress

class SendInvoiceRequest(Contract):
    user_id: NonEmpty
    invoice_id: NonEmpty

class AnalyticsRequest(Contract):
    event: NonEmpty
    user: NonEmpty
    data: dict[str, Any]

class ChargeResponse(BaseModel):
    status: str
    charge_id: str
    amount_charged: StrictInt
    user_id: str

class RefundResponse(BaseModel):
    status: str
    refund_id: str
    transaction_id: str

class StatusResponse(BaseModel):
    status: str
    charge_id: str
    payment_status: str

class InvoiceResponse(BaseModel):
    status: str
    invoice_id: str
    user_id: str
    period: str
    pdf_url: str

class SendInvoiceResponse(BaseModel):
    status: str
    invoice_id: str
    user_id: str

class InvoiceHistoryResponse(BaseModel):
    user_id: str
    invoices: list[InvoiceResponse]

class AnalyticsResponse(BaseModel):
    status: str
    event: str
    user_id: str
    metadata: dict[str, Any]

class WrappedAnalyticsResponse(BaseModel):
    data: AnalyticsResponse

class SummaryResponse(BaseModel):
    user_id: str
    total_spent: StrictInt
    currency: str

class WrappedSummaryResponse(BaseModel):
    data: SummaryResponse


def create_version_app(version: str) -> FastAPI:
    api = FastAPI(title="NexusPay Payment Gateway", version=version)
    def charge(request):
        cents = request.amount if version == "v1" else request.amount.value
        return {"status": "success", "charge_id": "ch_123", "amount_charged": cents, "user_id": request.user_id}
    charge.__annotations__["request"] = {"v1": ChargeRequestV1, "v2": ChargeRequestV2, "v3": ChargeRequestV3}[version]
    api.add_api_route("/charge", charge, methods=["POST"], response_model=ChargeResponse)

    @api.post("/refund" if version == "v1" else "/refunds/create", response_model=RefundResponse)
    def refund(request: RefundRequest):
        return {"status": "success", "refund_id": "rf_123", "transaction_id": request.transaction_id}

    @api.get("/status/{charge_id}", response_model=StatusResponse)
    def payment_status(charge_id: str):
        return {"status": "success", "charge_id": charge_id, "payment_status": "paid"}

    def invoice(request):
        return {"status": "success", "invoice_id": "inv_123", "user_id": request.user_id, "period": request.period, "pdf_url": "/invoices/inv_123.pdf"}
    invoice.__annotations__["request"] = InvoiceRequestV1 if version == "v1" else InvoiceRequestV2
    api.add_api_route("/invoice/generate", invoice, methods=["POST"], response_model=InvoiceResponse)

    @api.post("/invoice/send", response_model=SendInvoiceResponse)
    def send_invoice(request: SendInvoiceRequest):
        return {"status": "success", "invoice_id": request.invoice_id, "user_id": request.user_id}

    @api.get("/invoice/history", response_model=InvoiceHistoryResponse)
    def invoice_history(user: NonEmpty):
        return {"user_id": user, "invoices": []}

    @api.post("/analytics/log", response_model=AnalyticsResponse if version == "v1" else WrappedAnalyticsResponse)
    def analytics(request: AnalyticsRequest):
        result = {"status": "success", "event": request.event, "user_id": request.user, "metadata": request.data}
        return result if version == "v1" else {"data": result}

    @api.get("/analytics/summary/{user_id}", response_model=SummaryResponse if version == "v1" else WrappedSummaryResponse)
    def summary(user_id: str):
        result = {"user_id": user_id, "total_spent": 5000, "currency": "USD"}
        return result if version == "v1" else {"data": result}
    return api


VERSION_APPS = {version: create_version_app(version) for version in ("v1", "v2", "v3")}
app = FastAPI(title="NexusPay Provider Controls")
request_logs = []

class VersionRequest(Contract):
    version: Literal["v1", "v2", "v3"]

@app.get("/api/version")
def get_version():
    return {"version": ACTIVE_VERSION}

@app.post("/api/version")
def set_version(request: VersionRequest):
    global ACTIVE_VERSION
    ACTIVE_VERSION = request.version
    request_logs.clear()
    return {"version": ACTIVE_VERSION}

@app.get("/api/raw_spec")
def get_raw_spec():
    return VERSION_APPS[ACTIVE_VERSION].openapi()

@app.get("/api/provider/logs")
def get_logs():
    return {"logs": request_logs}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    payload = None
    if request.method == "POST" and not request.url.path.startswith("/api/"):
        try:
            payload = await request.json()
        except (ValueError, UnicodeDecodeError):
            pass
    response = await call_next(request)
    if not request.url.path.startswith("/api/"):
        request_logs.insert(0, {"id": f"req_{datetime.now(timezone.utc).timestamp()}", "timestamp": datetime.now(timezone.utc).isoformat(), "method": request.method, "path": request.url.path, "status": response.status_code, "payload": payload})
        del request_logs[50:]
    return response

async def dispatch_version(scope, receive, send):
    await VERSION_APPS[ACTIVE_VERSION](scope, receive, send)

app.mount("/", dispatch_version)
app.openapi = get_raw_spec

def export_specs():
    specs_dir = Path(__file__).parent / "specs"
    specs_dir.mkdir(exist_ok=True)
    for version, api in VERSION_APPS.items():
        (specs_dir / f"{version}_spec.json").write_text(json.dumps(api.openapi(), indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    import sys
    import uvicorn
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_specs()
    else:
        uvicorn.run(app, host="127.0.0.1", port=8001)
