from fastmcp import FastMCP
import subprocess
import os
from google import genai
from dotenv import dotenv_values

mcp = FastMCP("Test Runner & IPS Validator")

@mcp.tool()
def run_tests_and_score_ips(test_path: str = "client_app/tests/test_payment.py", original_intent: str = "Charge monthly subscription") -> dict:
    """
    Runs the pytest suite and uses an LLM-as-a-judge to compute the Intent Preservation Score (IPS).
    """
    results = {}
    
    # 1. Run automated tests
    try:
        # Note: We need to use sys.executable to ensure we use the venv python
        import sys
        cmd = [sys.executable, "-m", "pytest", test_path, "-v"]
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        results["tests_passed"] = (process.returncode == 0)
        results["test_output"] = process.stdout
    except Exception as e:
        results["tests_passed"] = False
        results["test_output"] = str(e)
        
    # 2. Compute IPS (Intent Preservation Score)
    # We read the updated code to judge it
    try:
        with open("client_app/payment_service.py", "r") as f:
            updated_code = f.read()
            
        env_vars = dotenv_values(".env")
        api_key = env_vars.get("GEMINI_API_KEY")
        if not api_key:
             results["ips_score"] = "Error: GEMINI_API_KEY not set in .env"
        else:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            You are an expert code reviewer judging a repaired API integration.
            The original business intent was: "{original_intent}"
            
            Here is the newly repaired code:
            {updated_code}
            
            Does this new code still correctly fulfill the original business intent despite any schema changes?
            Output ONLY a number between 0 and 100 representing your confidence score.
            """
            response = client.models.generate_content(
                model='gemini-3.5-flash-lite',
                contents=prompt,
            )
            score_str = response.text.strip()
            # Clean up the output in case it included text
            import re
            match = re.search(r'\d+', score_str)
            if match:
                results["ips_score"] = int(match.group())
            else:
                results["ips_score"] = score_str
                
    except Exception as e:
        results["ips_score"] = f"Error computing IPS: {e}"
        
    return results

if __name__ == "__main__":
    mcp.run()
