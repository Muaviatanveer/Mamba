import os

with open("compiler/cloud.py", "r") as f:
    content = f.read()

# 1. Add imports
if "import base64" not in content:
    content = content.replace("import sys\n", "import sys\nimport base64\nimport urllib.error\n")

# 2. Add CLOUD_API_URL
if "CLOUD_API_URL" not in content:
    content = content.replace('ROOT_DOMAIN = "mambacloud.app"\n', 'ROOT_DOMAIN = "mambacloud.app"\nCLOUD_API_URL = "https://mambacloud.app/api/cloud-deploy"\n')

# 3. The new functions and proxy replacement
new_code = """
# ==============================================================================
# 1. CLIENT CLI: `mamba deploy --cloud` (Runs on Alice's Laptop)
# ==============================================================================
def deploy_to_remote_cloud(project_dir="."):
    app_id = os.path.basename(os.path.abspath(project_dir)).lower().replace("_", "-").replace(" ", "-")
    print("=" * 55)
    print("  🐍 MAMBA CLOUD GLOBAL DEPLOYMENT ENGINE")
    print("=" * 55)
    print(f"📦 Packaging project '{app_id}'...")

    # Collect project files (.mb files and public/ folder)
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
                print("\\n" + "=" * 55)
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

        # Write received files
        for rel_path, content in files.items():
            full_path = os.path.join(app_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        # Pick dynamic available port (8100 - 8900)
        port = 8100
        deps = load_deployments()
        used_ports = [info["port"] for info in deps.values() if "port" in info]
        while port in used_ports:
            port += 1

        # Stop existing process for this app if running
        if app_id in deps:
            try:
                os.kill(deps[app_id]["pid"], signal.SIGTERM)
            except Exception:
                pass

        # Build C++ release binary on VPS
        entry_file = "main.mb" if os.path.exists(os.path.join(app_dir, "main.mb")) else "app.mb"
        build_cmd = ["/opt/mamba-cloud/mamba", "build", entry_file, "--release"]
        build_res = subprocess.run(build_cmd, cwd=app_dir, capture_output=True, text=True)

        if build_res.returncode != 0:
            return {"status": "error", "message": f"Compilation failed: {build_res.stderr}"}

        # Spawn binary daemon with PORT environment variable
        binary_path = os.path.join(app_dir, "dist", "mamba_app")
        env = os.environ.copy()
        env["PORT"] = str(port)
        proc = subprocess.Popen([binary_path], cwd=app_dir, env=env)

        custom_domain = f"https://{app_id}.{ROOT_DOMAIN}"
        
        # Save deployment registry
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
        # Intercept Cloud Deployments from Alice/Developers
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
        
        # Domain map
        domain_map = {}
        for app_id, info in deps.items():
            domain_map[f"{app_id}.{ROOT_DOMAIN}"] = info["port"]
            domain_map[app_id] = info["port"]

        target_port = domain_map.get(host)
        
        # If root domain or unknown, show Mamba Cloud Landing
        if not target_port:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = f\"\"\"
            <!DOCTYPE html>
            <html>
            <head><title>Mamba Cloud Platform 🐍</title><script src="https://cdn.tailwindcss.com"></script></head>
            <body class="bg-zinc-950 text-white min-h-screen flex items-center justify-center font-mono">
                <div class="max-w-xl p-8 bg-zinc-900 border border-zinc-800 rounded-2xl space-y-4 text-center">
                    <h1 class="text-3xl font-bold text-emerald-400">🐍 Mamba Cloud Platform</h1>
                    <p class="text-zinc-400 text-xs leading-relaxed">The global push-to-deploy cloud engine for Mamba native applications.</p>
                    <div class="bg-black/60 p-4 rounded-xl text-left text-xs text-emerald-300 border border-zinc-800">
                        <code>$ mamba deploy --cloud</code>
                    </div>
                    <div class="text-[11px] text-zinc-500">Active Apps: {len(deps)} | Version: v0.3.0</div>
                </div>
            </body>
            </html>
            \"\"\"
            self.wfile.write(html.encode("utf-8"))
            return

        # Forward request to C++ Binary port
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
        print("\\n🛑 Proxy Gateway stopped.")

def load_deployments():"""

# Find where `def start_reverse_proxy` starts and replace up to `def load_deployments():`
import re
pattern = re.compile(r"def start_reverse_proxy\(.*?\):.*?def load_deployments\(\):", re.DOTALL)
content = pattern.sub(new_code, content)

with open("compiler/cloud.py", "w") as f:
    f.write(content)
