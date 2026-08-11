from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class PythonHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/user':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            payload = json.dumps({"name": "Muavia", "project": "Mamba", "role": "AI Engineer", "version": "0.1.0"})
            self.wfile.write(payload.encode('utf-8'))

    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    print("🐍 Python Web Server running on http://localhost:3001")
    HTTPServer(('0.0.0.0', 3001), PythonHandler).serve_forever()