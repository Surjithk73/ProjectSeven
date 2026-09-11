import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Determine which version is active
ACTIVE_VERSION = os.getenv("API_VERSION", "v1")

app = FastAPI(
    title="FinTech Payment Gateway",
    description="Mock upstream API",
    version=ACTIVE_VERSION,
)

# --- V1 Schema ---
class ChargeRequestV1(BaseModel):
    amount: int
    user_id: str

# --- V2 Schema ---
class CurrencyAmount(BaseModel):
    value: int
    currency: str

class ChargeRequestV2(BaseModel):
    amount: CurrencyAmount
    user_id: str


if ACTIVE_VERSION == "v1":
    @app.post("/charge")
    def create_charge(request: ChargeRequestV1):
        return {"status": "success", "charge_id": "ch_123", "amount_charged": request.amount}

elif ACTIVE_VERSION == "v2":
    @app.post("/charge")
    def create_charge(request: ChargeRequestV2):
        return {"status": "success", "charge_id": "ch_123", "amount_charged": request.amount.value}


def export_specs():
    """Helper to export OpenAPI specs for both versions"""
    base_dir = os.path.dirname(__file__)
    specs_dir = os.path.join(base_dir, "specs")
    
    # Build a temp app for v1
    app_v1 = FastAPI(title="FinTech Payment Gateway", version="v1")
    @app_v1.post("/charge")
    def charge_v1(request: ChargeRequestV1): pass
    
    with open(os.path.join(specs_dir, "v1_spec.json"), "w") as f:
        json.dump(app_v1.openapi(), f, indent=2)

    # Build a temp app for v2
    app_v2 = FastAPI(title="FinTech Payment Gateway", version="v2")
    @app_v2.post("/charge")
    def charge_v2(request: ChargeRequestV2): pass
    
    with open(os.path.join(specs_dir, "v2_spec.json"), "w") as f:
        json.dump(app_v2.openapi(), f, indent=2)

if __name__ == "__main__":
    import uvicorn
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        print("Exporting OpenAPI specs...")
        export_specs()
        print("Done.")
    else:
        print(f"Starting server in {ACTIVE_VERSION} mode...")
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
