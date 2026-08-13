import os
import re

def init_project(project_name):
    print(f"🚀 Initializing new Mamba project: '{project_name}'...")
    os.makedirs(project_name, exist_ok=True)
    
    main_code = """import "helpers.mb"

let app_name = "Mamba Web App"
print("Starting " + app_name + "...")

route GET "/api/info" {
    print("Mamba API Hit!")
}
"""
    helpers_code = """fn add(a, b) { return a + b }"""
    mamba_config = f'{{\n  "name": "{project_name}",\n  "version": "0.2.0",\n  "main": "main.mb"\n}}\n'
    
    with open(os.path.join(project_name, "main.mb"), "w") as f: f.write(main_code)
    with open(os.path.join(project_name, "helpers.mb"), "w") as f: f.write(helpers_code)
    with open(os.path.join(project_name, "mamba.json"), "w") as f: f.write(mamba_config)
    with open(os.path.join(project_name, ".gitignore"), "w") as f: f.write("dist/\nbuild/\n.DS_Store\n")
    
    print(f"✨ Project '{project_name}' scaffolded successfully!")

def format_code(filename):
    print(f"🎨 Formatting '{filename}'...")
    with open(filename, "r") as f: code = f.read()

    lines = code.split("\n")
    formatted_lines = []
    indent_level = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append("")
            continue
        if stripped.startswith("}"): indent_level = max(0, indent_level - 1)
        indent = "    " * indent_level
        cleaned_line = re.sub(r'\s*=\s*', ' = ', stripped)
        formatted_lines.append(f"{indent}{cleaned_line}")
        if stripped.endswith("{"): indent_level += 1

    formatted_code = "\n".join(formatted_lines)
    with open(filename, "w") as f: f.write(formatted_code)
    print(f"✨ '{filename}' formatted cleanly!")