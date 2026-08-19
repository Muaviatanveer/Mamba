import os
import sys
import json
import subprocess
import time
import signal
import re
import urllib.request
import http.client
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from compiler.builder import mamba_build

DEPLOYMENTS_FILE = "dist/deployments.json"
LOG_FILE = "dist/mamba.log"
REPOS_DIR = "mamba_cloud_repos"
WORKSPACE_DIR = "mamba_cloud_workspace"
ROOT_DOMAIN = "mambacloud.app"

def fix_terminal():
    sys.stdout.write("\r\033[K\033[0m")
    sys.stdout.flush()

def init_git_repo(repo_name="my_app"):
    print(f"🐍 Initializing Mamba Cloud Git Repository: '{repo_name}'...")
    
    os.makedirs(REPOS_DIR, exist_ok=True)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    repo_path = os.path.abspath(os.path.join(REPOS_DIR, f"{repo_name}.git"))
    workspace_path = os.path.abspath(os.path.join(WORKSPACE_DIR, repo_name))

    subprocess.run(f"git init --bare '{repo_path}'", shell=True)

    hook_path = os.path.join(repo_path, "hooks", "post-receive")
    mamba_cli_path = os.path.abspath("mamba")

    hook_script = f"""#!/bin/bash
echo "=================================================="
echo "  🐍 Mamba Cloud: Git Push Intercepted for '{repo_name}'!"
echo "=================================================="

WORK_TREE="{workspace_path}"
mkdir -p "$WORK_TREE"

GIT_WORK_TREE="$WORK_TREE" git checkout -f main 2>/dev/null || GIT_WORK_TREE="$WORK_TREE" git checkout -f master

cd "$WORK_TREE"
echo "📦 Building & Deploying '{repo_name}' via Mamba Cloud..."
"{mamba_cli_path}" deploy 8081
"""

    with open(hook_path, "w") as f:
        f.write(hook_script)

    subprocess.run(f"chmod +x '{hook_path}'", shell=True)

    print(f"\n✨ Mamba Cloud Bare Git Repository Created!")
    print(f"   ➜ Repo Path: {repo_path}")
    print(f"\n👉 Next Step: Add git remote & push to deploy:")
    print(f"   git remote add {repo_name}_cloud {repo_path}")
    print(f"   git push {repo_name}_cloud main")

def deploy_app(project_dir=".", port=8080, public=False, live=False):
    fix_terminal()
    print("==================================================")
    print("  🐍 MAMBA CLOUD DEPLOYMENT ENGINE (v0.3.0)")
    print("==================================================")
    
    os.makedirs("dist", exist_ok=True)

    target_type = None
    main_script = "examples/master_app.mb" if os.path.exists("examples/master_app.mb") else "main.mb"
    if not os.path.exists(main_script) and os.path.exists("examples/web.mb"):
        main_script = "examples/web.mb"

    if os.path.exists(os.path.join(project_dir, "package.json")):
        print("✓ Detected Project Type: Node.js Application")
        target_type = "node"
    elif os.path.exists(os.path.join(project_dir, "requirements.txt")) or os.path.exists(os.path.join(project_dir, "app.py")):
        print("✓ Detected Project Type: Python Application")
        target_type = "python"
    elif os.path.exists(main_script) or os.path.exists("mamba.json"):
        print("✓ Detected Project Type: Mamba Native C++ Application")
        target_type = "mamba"
    else:
        print("❌ Error: Unrecognized project structure. Missing main.mb, app.py, or package.json.")
        return

    log_fp = open(LOG_FILE, "a")
    env = os.environ.copy()
    env["PORT"] = str(port)

    # 1. Build Stage
    if target_type == "mamba":
        print(f"🔨 Compiling Mamba C++ Release Binary (-O3)...")
        mamba_build(main_script, target="cpp", release=True)
        binary_path = "dist/mamba_app"
        if not os.path.exists(binary_path):
            print("❌ Build Failed!")
            return
        start_cmd = f"./{binary_path}"

    elif target_type == "node":
        print("🔨 Installing Node.js dependencies (npm install)...")
        subprocess.run("npm install", shell=True, cwd=project_dir)
        start_cmd = "npm start" if os.path.exists(os.path.join(project_dir, "package.json")) else "node index.js"

    elif target_type == "python":
        req_file = os.path.join(project_dir, "requirements.txt")
        if os.path.exists(req_file):
            print("🔨 Installing Python dependencies...")
            subprocess.run("pip3 install -r requirements.txt", shell=True)
        
        py_entry = "app.py" if os.path.exists(os.path.join(project_dir, "app.py")) else "main.py"
        start_cmd = f"python3 {py_entry}"

    stop_deployment(quiet=True)

    print(f"🚀 Deploying {target_type.upper()} App to Mamba Cloud Runtime on Port {port}...")
    proc = subprocess.Popen(start_cmd, shell=True, env=env, cwd=project_dir, stdout=log_fp, stderr=log_fp)
    time.sleep(1.5)

    health_status = "HEALTHY (200 OK)"
    try:
        urllib.request.urlopen(f"http://localhost:{port}/", timeout=2)
    except Exception:
        health_status = "RUNNING"

    app_id = os.path.basename(os.path.abspath(project_dir)).lower().replace("_", "-").replace(" ", "-")
    custom_domain = f"https://{app_id}.{ROOT_DOMAIN}"

    live_url = "N/A"
    if live or public:
        print("🌐 Opening Cloudflare Global HTTPS Tunnel...")
        if shutil.which("cloudflared"):
            tunnel_cmd = f"cloudflared tunnel --url http://localhost:{port}"
            tunnel_proc = subprocess.Popen(tunnel_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            start_time = time.time()
            while time.time() - start_time < 6:
                line = tunnel_proc.stdout.readline()
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    live_url = match.group(0)
                    break

    deployments = {}
    if os.path.exists(DEPLOYMENTS_FILE):
        with open(DEPLOYMENTS_FILE, "r") as f:
            try: deployments = json.load(f)
            except: pass

    deployments[app_id] = {
        "type": target_type.upper(),
        "pid": proc.pid,
        "port": port,
        "status": health_status,
        "local_url": f"http://localhost:{port}",
        "custom_domain": custom_domain,
        "live_url": live_url,
        "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(DEPLOYMENTS_FILE, "w") as f:
        json.dump(deployments, f, indent=2)

    fix_terminal()
    print("\n✨ DEPLOYMENT SUCCESSFUL!")
    print(f"   ➜ Type: {target_type.upper()}")
    print(f"   ➜ Local Port: http://localhost:{port}")
    print(f"   ➜ Local Domain: {custom_domain}")
    if live_url != "N/A":
        print(f"   ➜ Global Public HTTPS URL: {live_url}/api/showcase/info")
    print(f"   ➜ Process PID: {proc.pid}\n")

def start_reverse_proxy(proxy_port=8000):
    deployments = load_deployments()
    if not deployments:
        print("No active Mamba Cloud deployments found.")
        return

    domain_map = {}
    for app_id, info in deployments.items():
        subdomain = f"{app_id.lower()}.{ROOT_DOMAIN}"
        domain_map[subdomain] = info["port"]
        domain_map[app_id.lower()] = info["port"]

    class MambaProxyHandler(BaseHTTPRequestHandler):
        def _proxy(self, method):
            host_header = self.headers.get("Host", "").split(":")[0].lower()
            parsed_path = urllib.parse.urlparse(self.path).path
            
            target_port = None
            if host_header in domain_map:
                target_port = domain_map[host_header]
            else:
                for k, p in domain_map.items():
                    target_port = p
                    break

            if not target_port:
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                
                route_items = "".join([f"<li style='margin:15px;'><a style='color:#00e676; font-size:18px; font-family:monospace; text-decoration:none;' href='{info['custom_domain']}'>➜ {info['custom_domain']} ({info.get('type', 'APP')}) ➔ Port {info['port']}</a></li>" for app_id, info in deployments.items()])
                if not route_items: route_items = "<li>No active deployments</li>"

                html = f"""<!DOCTYPE html>
                <html>
                <head><meta charset="UTF-8"><title>Mamba Cloud Gateway</title></head>
                <body style="background:#0f111a; color:#fff; font-family:sans-serif; text-align:center; padding:50px;">
                    <h1 style="color:#00e676;">🔀 Mamba Local Domain Gateway</h1>
                    <p style="color:#aaa;">Active Subdomains:</p>
                    <ul style="list-style:none; padding:0;">{route_items}</ul>
                </body>
                </html>
                """
                self.wfile.write(html.encode("utf-8"))
                return

            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len) if content_len > 0 else None
                
                conn = http.client.HTTPConnection("127.0.0.1", target_port)
                conn.request(method, self.path, body=body, headers=dict(self.headers))
                resp = conn.getresponse()
                
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    self.send_header(k, v)
                self.end_headers()
                
                self.wfile.write(resp.read())
                conn.close()
                print(f"🔀 [Mamba Proxy] {method} http://{host_header}{self.path} ➔ Forwarded to Port {target_port} (Status {resp.status})")
            except Exception:
                self.send_response(502)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"502 Bad Gateway - Target App Offline")
                print(f"❌ [Mamba Proxy] 502 Bad Gateway for Port {target_port}")

        def do_GET(self): self._proxy("GET")
        def do_POST(self): self._proxy("POST")
        def do_PUT(self): self._proxy("PUT")
        def do_DELETE(self): self._proxy("DELETE")
        def log_message(self, format, *args): return

    server = None
    while server is None:
        try:
            server = HTTPServer(('0.0.0.0', proxy_port), MambaProxyHandler)
        except OSError:
            print(f"⚠️ Port {proxy_port} is occupied. Trying port {proxy_port + 1}...")
            proxy_port += 1

    print("==================================================")
    print(f"  🔀 Mamba Local Domain Gateway on http://localhost:{proxy_port}")
    print("==================================================")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\n🛑 Proxy Gateway stopped.")

def load_deployments():
    if os.path.exists(DEPLOYMENTS_FILE):
        try:
            with open(DEPLOYMENTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def check_status():
    deployments = load_deployments()
    if not deployments:
        print("No active Mamba Cloud deployments found.")
        return

    print("==================================================")
    print("  🐍 Mamba Cloud Active Deployments")
    print("==================================================")
    for app_id, info in deployments.items():
        print(f"• App ID: {app_id} [{info.get('type', 'MAMBA')}]")
        print(f"  Local Domain: {info.get('custom_domain', 'N/A')}")
        print(f"  Local Port: {info['local_url']}")
        print(f"  PID: {info['pid']}")
        print(f"  Status: {info['status']}")
        print("--------------------------------------------------")

def show_logs():
    if os.path.exists(LOG_FILE):
        print(f"📜 Streaming Mamba Cloud Logs ({LOG_FILE}):\n---------------------------------")
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            for line in lines[-30:]:
                print(line, end="")
    else:
        print("No log file found.")

def stop_deployment(quiet=False):
    if not os.path.exists(DEPLOYMENTS_FILE):
        if not quiet: print("No active deployments to stop.")
        return

    with open(DEPLOYMENTS_FILE, "r") as f:
        deployments = json.load(f)

    for app_id, info in deployments.items():
        pid = info.get("pid")
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                if not quiet: print(f"🛑 Stopped deployment (PID: {pid}).")
            except Exception:
                pass

    os.remove(DEPLOYMENTS_FILE)