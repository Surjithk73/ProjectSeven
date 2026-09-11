import tree_sitter_python as tspython
from tree_sitter import Language, Parser

def get_http_call_sites(file_path: str):
    """
    Parses a python file and returns a list of dictionaries containing
    metadata about any HTTP POST call sites it finds.
    """
    PY_LANGUAGE = Language(tspython.language())
    parser = Parser(PY_LANGUAGE)
    
    with open(file_path, 'rb') as f:
        src = f.read()
        
    tree = parser.parse(src)
    root = tree.root_node
    
    call_sites = []
    
    # Simple recursive function to find function definitions and their call sites
    def traverse(node, current_func=None):
        if node.type == 'function_definition':
            # Extract function name
            name_node = node.child_by_field_name('name')
            if name_node:
                current_func = {
                    'name': src[name_node.start_byte:name_node.end_byte].decode('utf-8'),
                    'body': src[node.start_byte:node.end_byte].decode('utf-8'),
                    'line': node.start_point[0] + 1
                }
                
        # Look for httpx.post
        if node.type == 'call':
            func_node = node.child_by_field_name('function')
            if func_node:
                func_text = src[func_node.start_byte:func_node.end_byte].decode('utf-8')
                if func_text in ('httpx.post', 'requests.post'):
                    site_info = {
                        'file': file_path,
                        'call_code': src[node.start_byte:node.end_byte].decode('utf-8'),
                        'line': node.start_point[0] + 1,
                        'parent_function': current_func['name'] if current_func else 'global',
                        'function_context': current_func['body'] if current_func else src[node.start_byte:node.end_byte].decode('utf-8')
                    }
                    call_sites.append(site_info)
                    
        for child in node.children:
            traverse(child, current_func)
            
    traverse(root)
    return call_sites

if __name__ == "__main__":
    import sys
    sites = get_http_call_sites(sys.argv[1] if len(sys.argv) > 1 else "../client_app/payment_service.py")
    for site in sites:
        print(f"Found call to {site['parent_function']} at line {site['line']}")
