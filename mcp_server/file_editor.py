from fastmcp import FastMCP
import os

mcp = FastMCP("File Editor Server")

@mcp.tool()
def apply_patch(file_path: str, old_code_snippet: str, new_code_snippet: str) -> str:
    """
    Securely applies a targeted line-level patch to a specific file.
    Replaces exactly the first occurrence of old_code_snippet with new_code_snippet.
    """
    # Security: Ensure we are only editing files inside client_app/
    if "client_app" not in file_path:
        return "Error: Security violation. Can only edit files inside client_app/ directory."
        
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
        
    try:
        with open(file_path, "r") as f:
            content = f.read()
            
        if old_code_snippet not in content:
            # Fallback string manipulation if whitespace differs slightly
            normalized_content = " ".join(content.split())
            normalized_old = " ".join(old_code_snippet.split())
            if normalized_old not in normalized_content:
                return "Error: old_code_snippet not found in the target file exactly as provided."
            else:
                return "Error: old_code_snippet found but whitespace differs. Please provide exact string match including newlines."
                
        # Apply the patch
        updated_content = content.replace(old_code_snippet, new_code_snippet, 1)
        
        with open(file_path, "w") as f:
            f.write(updated_content)
            
        return f"Successfully patched {file_path}"
        
    except Exception as e:
        return f"Error applying patch: {e}"

if __name__ == "__main__":
    mcp.run()
