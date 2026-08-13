import os
import re

def resolve_imports(filename, visited=None):
    if visited is None:
        visited = set()
    
    abs_path = os.path.abspath(filename)
    if abs_path in visited:
        return ""
    visited.add(abs_path)

    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Mamba Import Error: File '{filename}' not found.")

    with open(abs_path, 'r') as f:
        lines = f.readlines()

    expanded_code = []
    for line in lines:
        match = re.match(r'^\s*import\s+"([^"]+)"', line)
        if match:
            imported_file = match.group(1)
            base_dir = os.path.dirname(abs_path)
            full_path = os.path.join(base_dir, imported_file)
            expanded_code.append(resolve_imports(full_path, visited))
        else:
            expanded_code.append(line)

    return "\n".join(expanded_code)