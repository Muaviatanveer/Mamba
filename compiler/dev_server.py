import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from lark import Lark
from compiler.preprocessor import resolve_imports

COMPILER_DIR = os.path.dirname(os.path.abspath(__file__))
GRAMMAR_PATH = os.path.join(COMPILER_DIR, 'grammar.lark')

def start_mamba_server(filename, port=8000):
    env_port = os.environ.get("PORT")
    if env_port: port = int(env_port)

    with open(GRAMMAR_PATH, 'r') as g_file: grammar = g_file.read()
    parser = Lark(grammar, parser='lalr')
    code = resolve_imports(filename)
    tree = parser.parse(code)

    routes = {}
    for stmt in tree.children:
        if hasattr(stmt, 'data') and stmt.data == 'route_def':
            method = stmt.children[0].value
            path = stmt.children[1].value[1:-1]
            routes[(method, path)] = stmt.children[2]

    class MambaHTTPHandler(BaseHTTPRequestHandler):
        def _handle_request(self, method):
            parsed = urllib.parse.urlparse(self.path)
            parsed_path = parsed.path
            
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else ""

            if (method, parsed_path) in routes:
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                resp_json = json.dumps({
                    "status": "success",
                    "method": method,
                    "path": parsed_path,
                    "body": post_body
                })
                self.wfile.write(resp_json.encode("utf-8"))
                print(f"⚡ [Mamba Dev Server] 200 OK - {method} {parsed_path}")
            elif parsed_path == "/" and ("GET", "/") not in routes:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                route_items = "".join([f"<li style='margin:10px;'><a style='color:#00e676; font-size:20px; text-decoration:none;' href='{path}'>➜ {m} {path}</a></li>" for (m, path) in routes.keys()])
                if not route_items: route_items = "<li>No routes registered</li>"
                response_html = f"<html><body style='background:#0f111a; color:#fff; text-align:center; padding:50px;'><h1 style='color:#00e676;'>🐍 Mamba Dev Server</h1><ul>{route_items}</ul></body></html>"
                self.wfile.write(response_html.encode("utf-8"))
                print(f"⚡ [Mamba Dev Server] 200 OK - {method} /")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 - Mamba Route Not Found")
                print(f"❌ [Mamba Dev Server] 404 Not Found - {method} {parsed_path}")

        def do_GET(self): self._handle_request("GET")
        def do_POST(self): self._handle_request("POST")
        def do_PUT(self): self._handle_request("PUT")
        def do_DELETE(self): self._handle_request("DELETE")
        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def log_message(self, format, *args): return

    server = None
    while server is None:
        try:
            server = HTTPServer(('0.0.0.0', port), MambaHTTPHandler)
        except OSError:
            print(f"⚠️ Port {port} is occupied. Trying port {port + 1}...")
            port += 1

    print(f"==================================================")
    print(f"  🐍 Mamba Dev Web Server Running on http://localhost:{port}")
    print(f"==================================================")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\n🛑 Server stopped.")