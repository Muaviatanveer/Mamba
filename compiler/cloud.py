# compiler/cloud.py - Mamba Global Cloud Engine
import os
import sys
import json
import time
import signal
import re
import urllib.request
import urllib.error
import http.client
import shutil
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from compiler.builder import mamba_build

DEPLOYMENTS_FILE = "dist/deployments.json"
LOG_FILE = "dist/mamba.log"
REPOS_DIR = "mamba_cloud_repos"
WORKSPACE_DIR = "mamba_cloud_workspace"
ROOT_DOMAIN = "mambacloud.app"
CLOUD_API_URL = "http://157.245.196.64/api/cloud-deploy"

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
    if not os.path.exists(main_script) and os.path.exists("app.mb"):
        main_script = "app.mb"

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
        print(f"   ➜ Global Public HTTPS URL: {live_url}")
    print(f"   ➜ Process PID: {proc.pid}\n")


# ==============================================================================
# 1. CLIENT CLI: `mamba deploy --cloud` (Runs on Developer Laptop)
# ==============================================================================
def deploy_to_remote_cloud(project_dir="."):
    app_id = os.path.basename(os.path.abspath(project_dir)).lower().replace("_", "-").replace(" ", "-")
    print("=" * 55)
    print("  🐍 MAMBA CLOUD GLOBAL DEPLOYMENT ENGINE")
    print("=" * 55)
    print(f"📦 Packaging project '{app_id}'...")

    files_bundle = {}
    for root, _, files in os.walk(project_dir):
        if "dist" in root or "venv" in root or ".git" in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, project_dir)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    files_bundle[rel_path] = f.read()
            except Exception:
                pass

    payload = {
        "app_id": app_id,
        "files": files_bundle
    }

    print(f"🚀 Uploading bundle ({len(files_bundle)} files) to https://mambacloud.app...")
    
    try:
        req = urllib.request.Request(
            CLOUD_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Mamba-CLI-v0.3.0"}
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            
            if res_data.get("status") == "success":
                print("\n" + "=" * 55)
                print("🎉 DEPLOYMENT LIVE TO THE ENTIRE WORLD!")
                print(f"🔗 Public URL: {res_data['url']}")
                print(f"⚡ Engine: Native C++20 (Port: {res_data['port']})")
                print("=" * 55)
            else:
                print(f"❌ Deployment Failed: {res_data.get('message')}")
    except Exception as e:
        print(f"❌ Cloud Connection Error: {e}")

# ==============================================================================
# 2. SERVER RECEIVER: Handles Remote Deployments on VPS
# ==============================================================================
def handle_server_cloud_deploy(post_data_bytes):
    try:
        data = json.loads(post_data_bytes.decode("utf-8"))
        app_id = data["app_id"]
        files = data["files"]

        app_dir = f"/opt/mamba-apps/{app_id}"
        os.makedirs(app_dir, exist_ok=True)

        for rel_path, content in files.items():
            full_path = os.path.join(app_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        port = 8100
        deps = load_deployments()
        used_ports = [info["port"] for info in deps.values() if "port" in info]
        while port in used_ports:
            port += 1

        if app_id in deps:
            try:
                os.kill(deps[app_id]["pid"], signal.SIGTERM)
            except Exception:
                pass

        entry_file = "main.mb" if os.path.exists(os.path.join(app_dir, "main.mb")) else "app.mb"
        build_cmd = ["/opt/mamba-cloud/mamba", "build", entry_file, "--release"]
        build_res = subprocess.run(build_cmd, cwd=app_dir, capture_output=True, text=True)

        if build_res.returncode != 0:
            return {"status": "error", "message": f"Compilation failed: {build_res.stderr}"}

        binary_path = os.path.join(app_dir, "dist", "mamba_app")
        env = os.environ.copy()
        env["PORT"] = str(port)
        proc = subprocess.Popen([binary_path], cwd=app_dir, env=env)

        custom_domain = f"https://{app_id}.{ROOT_DOMAIN}"
        deps[app_id] = {
            "type": "MAMBA",
            "pid": proc.pid,
            "port": port,
            "status": "running",
            "custom_domain": custom_domain,
            "updated_at": time.time()
        }
        save_deployments(deps)

        return {
            "status": "success",
            "url": custom_domain,
            "port": port
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_deployments(data):
    os.makedirs(os.path.dirname(DEPLOYMENTS_FILE) or ".", exist_ok=True)
    with open(DEPLOYMENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==============================================================================
# 3. REVERSE PROXY GATEWAY WITH REMOTE API ROUTER
# ==============================================================================
class MambaGatewayHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/cloud-deploy":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            result = handle_server_cloud_deploy(post_data)
            
            self.send_response(200 if result.get("status") == "success" else 500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        self.proxy_request("POST")

    def do_GET(self):
        self.proxy_request("GET")

    def proxy_request(self, method):
        host = self.headers.get("Host", "").split(":")[0].lower()
        deps = load_deployments()
        
        domain_map = {}
        for app_id, info in deps.items():
            domain_map[f"{app_id}.{ROOT_DOMAIN}"] = info["port"]
            domain_map[app_id] = info["port"]

        target_port = domain_map.get(host)
        
        if not target_port:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """<!DOCTYPE html>
<html>
<head><title>Mamba Cloud Platform</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-zinc-950 text-white min-h-screen flex items-center justify-center font-mono">
    <div class="max-w-xl p-8 bg-zinc-900 border border-zinc-800 rounded-2xl space-y-4 text-center">
        <h1 class="text-3xl font-bold text-emerald-400">🐍 Mamba Cloud Platform</h1>
        <p class="text-zinc-400 text-xs leading-relaxed">The global push-to-deploy cloud engine for Mamba native applications.</p>
        <div class="bg-black/60 p-4 rounded-xl text-left text-xs text-emerald-300 border border-zinc-800">
            <code>$ mamba deploy --cloud</code>
        </div>
        <div class="text-[11px] text-zinc-500">Version: v0.3.0 Native Engine</div>
    </div>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        try:
            conn = http.client.HTTPConnection("127.0.0.1", target_port, timeout=10)
            headers = {k: v for k, v in self.headers.items()}
            body = None
            if "Content-Length" in self.headers:
                body = self.rfile.read(int(self.headers["Content-Length"]))
            
            conn.request(method, self.path, body=body, headers=headers)
            res = conn.getresponse()

            self.send_response(res.status)
            for k, v in res.getheaders():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(res.read())
            conn.close()
        except Exception:
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"502 Bad Gateway - Application is starting or unreachable.")

def start_reverse_proxy(proxy_port=8000):
    server = HTTPServer(("0.0.0.0", proxy_port), MambaGatewayHandler)
    print(f"🔀 Mamba Global Gateway listening on http://0.0.0.0:{proxy_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Proxy Gateway stopped.")

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

    if os.path.exists(DEPLOYMENTS_FILE):
        os.remove(DEPLOYMENTS_FILE)