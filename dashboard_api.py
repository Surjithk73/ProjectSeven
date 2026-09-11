import os
import sys
import json
import subprocess
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

app = FastAPI(title="Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global In-Memory State ---
class AppState:
    provider_version: str = "v1"
    agent_status: str = "idle"       # idle | running | healed | error
    last_diff: str = ""
    code_before: str = ""
    code_after: str = ""
    ips_score: int = 0
    agent_log: str = ""
    sig_graph: dict = {}

state = AppState()

def load_current_client_code():
    try:
        with open("client_app/payment_service.py", "r") as f:
            return f.read()
    except:
        return ""

# --- API Endpoints ---

@app.get("/api/state")
def get_state():
    return {
        "provider_version": state.provider_version,
        "agent_status": state.agent_status,
        "last_diff": state.last_diff,
        "code_before": state.code_before,
        "code_after": state.code_after,
        "ips_score": state.ips_score,
        "agent_log": state.agent_log,
        "sig_graph": state.sig_graph,
        "current_code": load_current_client_code(),
    }

@app.post("/api/provider/switch")
async def switch_provider(request: Request):
    body = await request.json()
    version = body.get("version")
    if version not in ["v1", "v2"]:
        raise HTTPException(status_code=400, detail="Invalid version")
    state.provider_version = version
    state.agent_status = "idle" if version == "v1" else "break_detected"
    state.last_diff = ""
    state.code_before = ""
    state.code_after = ""
    state.ips_score = 0
    state.agent_log = ""
    log(f">>> Provider switched to {version.upper()}. Agent status: {state.agent_status}")
    return {"active_version": state.provider_version, "agent_status": state.agent_status}

@app.post("/api/client/pay")
def run_client():
    log(f">>> Client payment attempt (provider is {state.provider_version.upper()})...")
    cmd = [sys.executable, "client_app/payment_service.py"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        log(f"    [OK] Payment succeeded!")
        return {"status": "success", "output": result.stdout.strip()}
    else:
        log(f"    [FAIL] Payment failed — 422 error (expected when V2 active)")
        return {"status": "error", "output": (result.stderr or result.stdout).strip()}

@app.post("/api/agent/trigger")
def trigger_agent():
    log("=" * 50)
    log(">>> MAPE-K Agent triggered!")
    state.agent_status = "running"
    state.code_before = load_current_client_code()
    log("    [MONITOR]  Captured current client code snapshot")
    log("    [MONITOR]  Running oasdiff to detect breaking changes...")

    cmd = [sys.executable, "agent/langgraph_loop.py"]
    log("    [ANALYZE]  Querying Semantic Intent Graph...")
    log("    [PLAN]     Calling Gemini to generate targeted patch...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    state.agent_log = result.stdout + (result.stderr or "")
    state.code_after = load_current_client_code()

    log("    [EXECUTE]  Patch applied to client_app/payment_service.py")
    log("    [VALIDATE] Running automated tests...")

    # Parse IPS score from logs
    ips_match = re.search(r"Intent Preservation Score:\s*(\d+)", state.agent_log)
    if ips_match:
        state.ips_score = int(ips_match.group(1))
        log(f"    [VALIDATE] IPS Score: {state.ips_score}/100")

    if "Self-Healing Cycle Complete" in state.agent_log:
        state.agent_status = "healed"
        log(">>> Self-Healing Cycle COMPLETE! System restored.")
    else:
        state.agent_status = "error"
        log(">>> Agent encountered an error. Check agent_log for details.")

    log("=" * 50)

    # Load SIG graph for visualization
    try:
        with open("sig_engine/sig_store.json", "r") as f:
            state.sig_graph = json.load(f)
    except:
        state.sig_graph = {}

    return {
        "status": state.agent_status,
        "log": state.agent_log,
        "code_before": state.code_before,
        "code_after": state.code_after,
        "ips_score": state.ips_score,
        "sig_graph": state.sig_graph,
    }

# --- The unified charge endpoint (acts as the provider) ---
@app.post("/charge")
async def create_charge(request: Request):
    data = await request.json()
    amount = data.get("amount")
    log(f"    /charge called — provider={state.provider_version}, amount type={type(amount).__name__}")

    if state.provider_version == "v1":
        if not isinstance(amount, int):
            log("    [REJECT] V1 expects flat integer — rejecting")
            raise HTTPException(status_code=422, detail="[V1] amount must be a flat integer")
        log("    [ACCEPT] V1 charge accepted")
        return {"status": "success", "charge_id": "ch_v1_001", "amount_charged": amount}

    elif state.provider_version == "v2":
        if not isinstance(amount, dict) or "value" not in amount or "currency" not in amount:
            log("    [REJECT] V2 expects {value, currency} object — rejecting")
            raise HTTPException(status_code=422, detail="[V2] amount must be {value: int, currency: string}")
        log("    [ACCEPT] V2 charge accepted")
        return {"status": "success", "charge_id": "ch_v2_001", "amount_charged": amount["value"]}

if __name__ == "__main__":
    import uvicorn
    log("Starting Self-Healing API Dashboard Backend...")
    log("NOTE: reload=False to prevent restart when agent patches payment_service.py")
    # reload=False is CRITICAL — if reload=True, uvicorn detects payment_service.py
    # being patched and restarts itself mid-agent-run, killing the test subprocess.
    uvicorn.run("dashboard_api:app", host="127.0.0.1", port=8002, reload=False)
