import json
import networkx as nx
import os

def analyze_impact(endpoint: str = "API_Endpoint_Charge", sig_path: str = "sig_engine/sig_store.json"):
    """
    Queries the Semantic Intent Graph to find impacted call sites and their business intents
    for a given broken API endpoint.
    """
    if not os.path.exists(sig_path):
        raise FileNotFoundError(f"SIG store not found at {sig_path}")
        
    with open(sig_path, "r") as f:
        data = json.load(f)
        
    G = nx.node_link_graph(data)
    
    impacted_sites = []
    
    if endpoint in G:
        # Find all call sites that invoke this endpoint
        for neighbor in G.successors(endpoint):
            node_data = G.nodes[neighbor]
            if node_data.get("type") == "call_site":
                # Find the intent this call site serves
                intent = "Unknown Intent"
                for intent_neighbor in G.successors(neighbor):
                    if G.nodes[intent_neighbor].get("type") == "intent":
                        intent = intent_neighbor
                        break
                        
                impacted_sites.append({
                    "call_site": neighbor,
                    "file": node_data.get("file"),
                    "line": node_data.get("line"),
                    "code": node_data.get("code"),
                    "intent": intent
                })
                
    return impacted_sites

if __name__ == "__main__":
    impact = analyze_impact()
    print("Impact Analysis:")
    print(json.dumps(impact, indent=2))
