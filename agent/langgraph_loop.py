import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END

from agent.monitor import get_api_diff, is_breaking_change
from agent.analyzer import analyze_impact
from agent.planner import generate_patch_plan

class AgentState(TypedDict):
    diff: str
    impacted_sites: List[Dict]
    patch_plans: List[Dict]
    final_status: str

def monitor_node(state: AgentState):
    print("\n--- STAGE: MONITOR ---")
    diff = get_api_diff()
    if is_breaking_change(diff):
        print("Breaking change detected!")
        return {"diff": diff}
    else:
        print("No breaking changes detected.")
        return {"diff": "", "final_status": "No Break"}

def analyze_node(state: AgentState):
    print("\n--- STAGE: ANALYZE ---")
    if not state.get("diff"):
        return {"impacted_sites": []}
    
    impacted_sites = analyze_impact()
    print(f"Found {len(impacted_sites)} impacted call sites via Semantic Intent Graph.")
    return {"impacted_sites": impacted_sites}

def plan_node(state: AgentState):
    print("\n--- STAGE: PLAN ---")
    plans = []
    for site in state["impacted_sites"]:
        print(f"Planning patch for {site['file']} conditioned on intent: '{site['intent']}'")
        plan = generate_patch_plan(state["diff"], site["code"], site["intent"])
        
        # Add metadata for the executor
        plan["file"] = site["file"]
        plans.append(plan)
        
    return {"patch_plans": plans}

from mcp_server.file_editor import apply_patch
from mcp_server.test_runner import run_tests_and_score_ips

def execute_node(state: AgentState):
    print("\n--- STAGE: EXECUTE (Applying Patch via MCP Boundary) ---")
    
    patch_results = []
    for plan in state.get("patch_plans", []):
        file_path = plan.get('file')
        print(f"Applying patch to {file_path}...")
        
        # Call the secure file editor
        result = apply_patch(
            file_path=file_path,
            old_code_snippet=plan.get('old_code_snippet'),
            new_code_snippet=plan.get('new_code_snippet')
        )
        print(result)
        patch_results.append(result)
        
    print("\n--- STAGE: VALIDATE (Running Tests & IPS Scoring) ---")
    # Grab the intent from the first impacted site for the IPS prompt
    intent = "Unknown"
    if state.get("impacted_sites"):
        intent = state["impacted_sites"][0].get("intent", "Unknown")
        
    validation = run_tests_and_score_ips(original_intent=intent)
    
    if validation.get("tests_passed"):
        print("[PASS] Automated Tests PASSED!")
    else:
        print("[FAIL] Automated Tests FAILED!")
        print(validation.get("test_output"))
        
    print(f"[IPS] Intent Preservation Score: {validation.get('ips_score')}/100")
    
    return {"final_status": "Self-Healing Cycle Complete!"}


# Build Graph
builder = StateGraph(AgentState)
builder.add_node("monitor", monitor_node)
builder.add_node("analyze", analyze_node)
builder.add_node("plan", plan_node)
builder.add_node("execute", execute_node)

builder.add_edge(START, "monitor")

# Conditional routing after monitor
def route_after_monitor(state: AgentState):
    if state.get("diff") and state["diff"] != "":
        return "analyze"
    return END

builder.add_conditional_edges("monitor", route_after_monitor)
builder.add_edge("analyze", "plan")
builder.add_edge("plan", "execute")
builder.add_edge("execute", END)

app = builder.compile()

if __name__ == "__main__":
    print("Starting MAPE-K Loop...")
    initial_state = {"diff": "", "impacted_sites": [], "patch_plans": [], "final_status": ""}
    final_state = app.invoke(initial_state)
    print("\nFinal State Status:", final_state["final_status"])
