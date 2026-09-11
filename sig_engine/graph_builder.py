import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import networkx as nx
from google import genai
from google.genai import types
from dotenv import dotenv_values
from sig_engine.parser import get_http_call_sites

def infer_intent(function_code: str) -> str:
    """Uses Gemini to infer the business intent of the given code block."""
    env_vars = dotenv_values(".env")
    api_key = env_vars.get("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("Strict Mode: Please insert your custom API key into the .env file. The system background key has been disabled.")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Analyze the following Python function. It makes an HTTP API call.
    What is the high-level business intent of this API call?
    Keep it to one concise phrase (e.g. "Charge monthly subscription", "Send SMS alert").
    Do NOT include quotes, backticks, or extra explanation.
    
    Code:
    {function_code}
    """
    
    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt,
    )
    return response.text.strip()

def build_sig(client_file: str, output_path: str = "sig_engine/sig_store.json"):
    """Parses the client code, infers intent, and saves a Semantic Intent Graph."""
    print(f"Building Semantic Intent Graph for {client_file}...")
    
    # 1. Parse AST to find call sites
    call_sites = get_http_call_sites(client_file)
    if not call_sites:
        print("No HTTP call sites found.")
        return
        
    G = nx.DiGraph()
    
    # 2. Build the graph
    for site in call_sites:
        # Node 1: The Endpoint (we infer this from the code roughly, or just use a placeholder node)
        # For simplicity, we just create an "Endpoint" node.
        endpoint_node = "API_Endpoint_Charge" 
        
        # Node 2: The Call Site
        site_node = f"{site['file']}:{site['line']}"
        
        # Node 3: The Intent
        print(f"Inferring intent for {site['parent_function']}...")
        intent = infer_intent(site['function_context'])
        print(f"-> Inferred Intent: {intent}")
        
        # Add nodes
        G.add_node(endpoint_node, type="endpoint")
        G.add_node(site_node, type="call_site", file=site['file'], line=site['line'], code=site['function_context'])
        G.add_node(intent, type="intent")
        
        # Add edges
        G.add_edge(endpoint_node, site_node, relation="invoked_by")
        G.add_edge(site_node, intent, relation="serves")
        
    # 3. Save graph
    data = nx.node_link_data(G)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Semantic Intent Graph saved to {output_path} with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

if __name__ == "__main__":
    import sys
    target_file = sys.argv[1] if len(sys.argv) > 1 else "client_app/payment_service.py"
    build_sig(target_file)
