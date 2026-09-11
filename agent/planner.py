import os
import json
from google import genai
from google.genai import types
from dotenv import dotenv_values

def generate_patch_plan(api_diff: str, target_code: str, business_intent: str) -> dict:
    """
    Calls Gemini to generate a line-level patch plan.
    """
    env_vars = dotenv_values(".env")
    api_key = env_vars.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert autonomous program repair agent.
    An upstream API has introduced a breaking change. You must fix the downstream client code.
    
    CRITICAL CONSTRAINT: You must preserve the original business intent of the code.
    Business Intent: "{business_intent}"
    
    API Breaking Change Report (JSON diff):
    {api_diff}
    
    Current Client Code:
    {target_code}
    
    Respond ONLY with a JSON object representing the targeted patch.
    Do NOT include any markdown formatting or explanation. 
    The JSON must match this schema:
    {{
        "old_code_snippet": "the exact string to replace in the original code",
        "new_code_snippet": "the new string to drop in its place"
    }}
    """
    
    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        )
    )
    
    try:
        plan = json.loads(response.text.strip())
        return plan
    except json.JSONDecodeError:
        print("Failed to decode JSON from LLM:", response.text)
        return {"error": "Invalid JSON generated"}

if __name__ == "__main__":
    # Mock test
    mock_diff = '{"breaking_changes": [{"type": "request-property-type-changed", "path": "/charge", "property": "amount"}]}'
    mock_code = 'payload = {"amount": amount_cents, "user_id": user_id}'
    mock_intent = 'Charge monthly subscription'
    
    print("Generating plan...")
    plan = generate_patch_plan(mock_diff, mock_code, mock_intent)
    print("Plan:", json.dumps(plan, indent=2))
