import os
import subprocess
import json

def get_api_diff(base_spec: str = "mock_provider/specs/v1_spec.json", 
                 revised_spec: str = "mock_provider/specs/v2_spec.json") -> str:
    """
    Calls the oasdiff binary to detect breaking changes.
    Returns a JSON string of the breaking changes.
    """
    oasdiff_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "oasdiff.exe")
    
    if not os.path.exists(oasdiff_path):
        raise FileNotFoundError(f"oasdiff binary not found at {oasdiff_path}")
        
    cmd = [
        oasdiff_path,
        "breaking",
        base_spec,
        revised_spec,
        "--format", "json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # oasdiff returns 1 if it finds breaking changes!
        if result.returncode in (0, 1):
            return result.stdout.strip()
        else:
            raise RuntimeError(f"oasdiff failed: {result.stderr}")
    except Exception as e:
        print(f"Error running oasdiff: {e}")
        return ""

def is_breaking_change(diff_json_str: str) -> bool:
    if not diff_json_str:
        return False
    try:
        diff_data = json.loads(diff_json_str)
        return len(diff_data) > 0
    except json.JSONDecodeError:
        return False

if __name__ == "__main__":
    diff = get_api_diff()
    print("Diff detected:")
    print(diff)
    print("Is breaking change:", is_breaking_change(diff))
