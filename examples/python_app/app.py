from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json

port = int(os.environ.get("PORT", 3001))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {
            "status": "success",
            "message": "Python Web App Deployed via Mamba Cloud!",
            "port": port
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == '__main__':
    print(f"🐍 Python Web Server running on port {port}")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()