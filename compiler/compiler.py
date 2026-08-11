import sys
import subprocess
import os
import shutil
import re
import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from lark import Lark, Transformer

COMPILER_DIR = os.path.dirname(os.path.abspath(__file__))
GRAMMAR_PATH = os.path.join(COMPILER_DIR, 'grammar.lark')

# --- 1. Import Preprocessor ---
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

# --- 2. C++ Code Generator ---
class CppGenerator(Transformer):
    def __init__(self):
        super().__init__()
        self.has_routes = False

    def number(self, args): return str(args[0])
    def string(self, args): return f"std::string({args[0]})"
    def var(self, args): return str(args[0])
    def add(self, args): return f"({args[0]} + {args[1]})"
    def sub(self, args): return f"({args[0]} - {args[1]})"
    def mul(self, args): return f"({args[0]} * {args[1]})"
    def div(self, args): return f"({args[0]} / {args[1]})"
    def gt(self, args): return f"({args[0]} > {args[1]})"
    def lt(self, args): return f"({args[0]} < {args[1]})"
    def eq(self, args): return f"({args[0]} == {args[1]})"
    def ne(self, args): return f"({args[0]} != {args[1]})"
    def var_assign(self, args): return f"auto {args[0]} = {args[1]};"
    def print_stmt(self, args): return f"std::cout << {args[0]} << std::endl;"
    def expr_stmt(self, args): return f"{args[0]};"
    def assert_stmt(self, args): return f"if (!({args[0]})) {{ throw std::runtime_error(\"Assertion Failed: {args[0]}\"); }}"
    def test_stmt(self, args): return f"// Test: {args[0]}\ntry {args[1]} catch(...) {{ std::cout << \"❌ FAIL: \" << {args[0]} << std::endl; }}\nstd::cout << \"✓ PASS: \" << {args[0]} << std::endl;"
    def block(self, args):
        body = "\n    ".join([str(a) for a in args if a is not None])
        return f"{{\n    {body}\n}}"
    def return_stmt(self, args): return f"return {args[0]};"
    def if_stmt(self, args):
        cond, body = args[0], args[1]
        if len(args) > 2 and args[2] is not None:
            return f"if ({cond}) {body} else {args[2]}"
        return f"if ({cond}) {body}"
    def while_stmt(self, args): return f"while ({args[0]}) {args[1]}"
    def try_stmt(self, args):
        return f"try {args[0]} catch (const std::exception& {args[1]}) {args[2]}"
    
    def route_def(self, args):
        self.has_routes = True
        method, path, body = args[0], args[1], args[2]
        return f"""
        if (mamba_req.method == "{method}" && mamba_req.path == {path}) {{
            auto mamba_route_handler = [&]() {{ {body} return std::string(""); }};
            std::string body_html = mamba_route_handler();
            std::string content_type = "text/html";
            if (!body_html.empty() && (body_html[0] == '{{' || body_html[0] == '[')) {{
                content_type = "application/json";
            }}
            std::string resp = "HTTP/1.1 200 OK\\r\\nAccess-Control-Allow-Origin: *\\r\\nAccess-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\\r\\nAccess-Control-Allow-Headers: Content-Type, Authorization\\r\\nContent-Type: " + content_type + "\\r\\nContent-Length: " + std::to_string(body_html.length()) + "\\r\\n\\r\\n" + body_html;
            write(client_fd, resp.c_str(), resp.length());
            close(client_fd);
            return;
        }}
        """
    
    def map_pair(self, args):
        key = str(args[0])
        return f"{{{key}, {args[1]}}}"

    def map(self, args):
        pairs = ", ".join([str(a) for a in args if a is not None])
        return f"std::map<std::string, std::string>{{{pairs}}}"

    def index_access(self, args): return f"{args[0]}[{args[1]}]"

    def dot_call(self, args):
        obj, method = str(args[0]), str(args[1])
        call_args = ", ".join([str(a) for a in args[2:] if a is not None])
        if obj == "file" and method == "read": return f"mamba_file_read({call_args})"
        if obj == "file" and method == "write": return f"mamba_file_write({call_args})"
        if obj == "http" and method == "get": return f"mamba_http_get({call_args})"
        if obj == "env" and method == "get": return f"mamba_env_get({call_args})"
        if obj == "json" and method == "stringify": return f"mamba_json_stringify({call_args})"
        if obj == "json" and method == "parse": return f"mamba_json_parse({call_args})"
        if obj == "req" and method == "body": return "mamba_req.body"
        if obj == "req" and method == "query": return f"mamba_req_query({call_args})"
        if obj == "req" and method == "header": return f"mamba_req_header({call_args})"
        if obj == "db" and method == "open": return f"mamba_db_open({call_args})"
        if obj == "db" and method == "query": return f"mamba_db_query({call_args})"
        if obj == "str" and method == "upper": return f"mamba_str_upper({call_args})"
        if obj == "str" and method == "lower": return f"mamba_str_lower({call_args})"
        if obj == "str" and method == "replace": return f"mamba_str_replace({call_args})"
        return f"{obj}.{method}({call_args})"

    def fn_def(self, args):
        fn_name = str(args[0])
        params = [f"auto {p}" for p in args[1:-1] if p is not None]
        params_str = ", ".join(params)
        body = args[-1]
        return f"auto {fn_name} = []({params_str}) {body};"

    def fn_call(self, args):
        fn_name = str(args[0])
        call_args = ", ".join([str(a) for a in args[1:] if a is not None])
        return f"{fn_name}({call_args})"

    def start(self, args):
        statements = "\n    ".join([str(s) for s in args if s is not None])
        
        if self.has_routes:
            server_main = f"""
void handle_client(int client_fd) {{
    if (mamba_req.method == "OPTIONS") {{
        std::string cors_ok = "HTTP/1.1 204 No Content\\r\\nAccess-Control-Allow-Origin: *\\r\\nAccess-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\\r\\nAccess-Control-Allow-Headers: Content-Type, Authorization\\r\\nContent-Length: 0\\r\\n\\r\\n";
        write(client_fd, cors_ok.c_str(), cors_ok.length());
        close(client_fd);
        return;
    }}

    {statements}
    
    std::string not_found = "HTTP/1.1 404 Not Found\\r\\nAccess-Control-Allow-Origin: *\\r\\nContent-Type: text/plain\\r\\nContent-Length: 23\\r\\n\\r\\n404 - Mamba Not Found";
    write(client_fd, not_found.c_str(), not_found.length());
    close(client_fd);
}}

void start_native_cpp_server(int default_port = 8000) {{
    int port = default_port;
    char* env_port = std::getenv("PORT");
    if (env_port && std::strlen(env_port) > 0) {{
        port = std::atoi(env_port);
    }}

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);
    
    bind(server_fd, (struct sockaddr*)&address, sizeof(address));
    listen(server_fd, 10);
    
    std::cout << "==================================================" << std::endl;
    std::cout << "  ⚡ Native C++ Mamba Web Server on http://localhost:" << port << std::endl;
    std::cout << "==================================================" << std::endl;
    
    while (true) {{
        int client_fd = accept(server_fd, NULL, NULL);
        if (client_fd < 0) continue;
        
        char buffer[4096] = {{0}};
        ssize_t bytes_read = read(client_fd, buffer, 4095);
        if (bytes_read <= 0) {{ close(client_fd); continue; }}
        
        std::string raw_req(buffer, bytes_read);
        std::stringstream ss(raw_req);
        
        std::string method, full_url, http_ver;
        ss >> method >> full_url >> http_ver;
        
        mamba_req.method = method;
        mamba_req.headers.clear();
        mamba_req.query.clear();
        mamba_req.body = "";
        
        size_t q_pos = full_url.find('?');
        if (q_pos != std::string::npos) {{
            mamba_req.path = full_url.substr(0, q_pos);
            std::string q_str = full_url.substr(q_pos + 1);
            std::stringstream q_ss(q_str);
            std::string pair;
            while (std::getline(q_ss, pair, '&')) {{
                size_t eq = pair.find('=');
                if (eq != std::string::npos) {{
                    mamba_req.query[pair.substr(0, eq)] = pair.substr(eq + 1);
                }}
            }}
        }} else {{
            mamba_req.path = full_url;
        }}
        
        size_t header_end = raw_req.find("\\r\\n\\r\\n");
        if (header_end != std::string::npos) {{
            mamba_req.body = raw_req.substr(header_end + 4);
            std::string headers_str = raw_req.substr(0, header_end);
            std::stringstream h_ss(headers_str);
            std::string line;
            std::getline(h_ss, line);
            while (std::getline(h_ss, line) && line != "\\r" && !line.empty()) {{
                size_t colon = line.find(':');
                if (colon != std::string::npos) {{
                    std::string h_key = line.substr(0, colon);
                    std::string h_val = line.substr(colon + 1);
                    while (!h_val.empty() && (h_val[0] == ' ' || h_val[0] == '\\t')) h_val.erase(0, 1);
                    while (!h_val.empty() && (h_val.back() == '\\r' || h_val.back() == '\\n')) h_val.pop_back();
                    mamba_req.headers[h_key] = h_val;
                }}
            }}
        }}

        if (!method.empty()) {{
            std::cout << "⚡ [Native C++ Server] " << method << " " << mamba_req.path << std::endl;
            handle_client(client_fd);
        }} else {{
            close(client_fd);
        }}
    }}
}}

int main() {{
    start_native_cpp_server(8000);
    return 0;
}}
"""
        else:
            server_main = f"""
int main() {{
    {statements}
    return 0;
}}
"""

        return f"""#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <sqlite3.h>

struct MambaRequest {{
    std::string method;
    std::string path;
    std::map<std::string, std::string> query;
    std::map<std::string, std::string> headers;
    std::string body;
}};

thread_local MambaRequest mamba_req;

std::string mamba_req_query(const std::string& key) {{
    if (mamba_req.query.count(key)) return mamba_req.query[key];
    return "";
}}

std::string mamba_req_header(const std::string& key) {{
    if (mamba_req.headers.count(key)) return mamba_req.headers[key];
    return "";
}}

sqlite3* mamba_global_db = nullptr;

std::string mamba_db_open(const std::string& db_path) {{
    if (sqlite3_open(db_path.c_str(), &mamba_global_db) == SQLITE_OK) {{
        return "db_ok";
    }}
    return "db_error";
}}

std::string mamba_db_query(const std::string& sql) {{
    if (!mamba_global_db) return "db_not_open";
    char* err_msg = nullptr;
    if (sqlite3_exec(mamba_global_db, sql.c_str(), nullptr, nullptr, &err_msg) == SQLITE_OK) {{
        return "query_ok";
    }}
    std::string err = err_msg ? std::string(err_msg) : "query_error";
    sqlite3_free(err_msg);
    return err;
}}

std::string mamba_str_upper(std::string str) {{
    std::transform(str.begin(), str.end(), str.begin(), ::toupper);
    return str;
}}

std::string mamba_str_lower(std::string str) {{
    std::transform(str.begin(), str.end(), str.begin(), ::tolower);
    return str;
}}

std::string mamba_str_replace(std::string str, const std::string& from, const std::string& to) {{
    size_t start_pos = 0;
    while((start_pos = str.find(from, start_pos)) != std::string::npos) {{
        str.replace(start_pos, from.length(), to);
        start_pos += to.length();
    }}
    return str;
}}

std::string mamba_file_read(const std::string& path) {{
    std::ifstream file(path.c_str());
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}}

void mamba_file_write(const std::string& path, const std::string& content) {{
    std::ofstream file(path.c_str());
    file << content;
}}

std::string mamba_http_get(const std::string& url) {{
    return "[C++ HTTP Get response for " + url + "]";
}}

std::string mamba_env_get(const std::string& key) {{
    char* val = std::getenv(key.c_str());
    return val ? std::string(val) : "";
}}

std::string mamba_json_stringify(const std::map<std::string, std::string>& m) {{
    std::string out = "{{";
    bool first = true;
    for (const auto& pair : m) {{
        if (!first) out += ", ";
        out += "\\"" + pair.first + "\\": \\"" + pair.second + "\\"";
        first = false;
    }}
    out += "}}";
    return out;
}}

std::map<std::string, std::string> mamba_json_parse(const std::string& json_str) {{
    std::map<std::string, std::string> res;
    size_t pos = 0;
    while ((pos = json_str.find('"', pos)) != std::string::npos) {{
        size_t key_end = json_str.find('"', pos + 1);
        if (key_end == std::string::npos) break;
        std::string key = json_str.substr(pos + 1, key_end - pos - 1);
        
        size_t colon = json_str.find(':', key_end);
        if (colon == std::string::npos) break;
        
        size_t val_start = json_str.find('"', colon);
        if (val_start == std::string::npos) break;
        size_t val_end = json_str.find('"', val_start + 1);
        if (val_end == std::string::npos) break;
        
        std::string val = json_str.substr(val_start + 1, val_end - val_start - 1);
        res[key] = val;
        pos = val_end + 1;
    }}
    return res;
}}

{server_main}"""

# --- 3. PHP Web Code Generator ---
class PhpGenerator(Transformer):
    def number(self, args): return str(args[0])
    def string(self, args): return str(args[0])
    def var(self, args): return f"${args[0]}"
    def add(self, args): return f"({args[0]} + {args[1]})"
    def sub(self, args): return f"({args[0]} - {args[1]})"
    def mul(self, args): return f"({args[0]} * {args[1]})"
    def div(self, args): return f"({args[0]} / {args[1]})"
    def gt(self, args): return f"({args[0]} > {args[1]})"
    def lt(self, args): return f"({args[0]} < {args[1]})"
    def eq(self, args): return f"({args[0]} == {args[1]})"
    def ne(self, args): return f"({args[0]} != {args[1]})"
    def var_assign(self, args): return f"${args[0]} = {args[1]};"
    def print_stmt(self, args): return f"echo {args[0]} . \"\\n\";"
    def expr_stmt(self, args): return f"{args[0]};"
    def assert_stmt(self, args): return f"assert({args[0]});"
    def test_stmt(self, args): return f"// Test: {args[0]}\necho \"Running Test: \" . {args[0]} . \"\\n\"; {args[1]}"
    def block(self, args):
        body = "\n    ".join([str(a) for a in args if a is not None])
        return f"{{\n    {body}\n}}"
    def return_stmt(self, args): return f"return {args[0]};"
    def if_stmt(self, args):
        cond, body = args[0], args[1]
        if len(args) > 2 and args[2] is not None:
            return f"if ({cond}) {body} else {args[2]}"
        return f"if ({cond}) {body}"
    def while_stmt(self, args): return f"while ({args[0]}) {args[1]}"
    def try_stmt(self, args):
        return f"try {args[0]} catch (Exception ${args[1]}) {args[2]}"
    def map_pair(self, args):
        key = str(args[0])
        return f"{key} => {args[1]}"
    def map(self, args):
        pairs = ", ".join([str(a) for a in args if a is not None])
        return f"[{pairs}]"
    def index_access(self, args): return f"{args[0]}[{args[1]}]"
    def dot_call(self, args):
        obj, method = str(args[0]), str(args[1])
        call_args = ", ".join([str(a) for a in args[2:] if a is not None])
        if obj == "file" and method == "read": return f"file_get_contents({call_args})"
        if obj == "file" and method == "write": return f"file_put_contents({call_args})"
        if obj == "http" and method == "get": return f"file_get_contents({call_args})"
        if obj == "env" and method == "get": return f"(getenv({call_args}) ? getenv({call_args}) : \"\")"
        if obj == "json" and method == "stringify": return f"json_encode({call_args})"
        if obj == "json" and method == "parse": return f"json_decode({call_args}, true)"
        if obj == "req" and method == "body": return "file_get_contents('php://input')"
        if obj == "req" and method == "query": return f"(isset($_GET[{call_args}]) ? $_GET[{call_args}] : \"\")"
        if obj == "req" and method == "header": return f"(isset($_SERVER['HTTP_' . strtoupper(str_replace('-', '_', {call_args}))]) ? $_SERVER['HTTP_' . strtoupper(str_replace('-', '_', {call_args}))] : \"\")"
        if obj == "db" and method == "open": return f"new PDO('sqlite:' . {call_args})"
        if obj == "db" and method == "query": return f"$mamba_global_db->exec({call_args})"
        if obj == "str" and method == "upper": return f"strtoupper({call_args})"
        if obj == "str" and method == "lower": return f"strtolower({call_args})"
        if obj == "str" and method == "replace": return f"str_replace({call_args})"
        return f"${obj}->{method}({call_args})"
    def route_def(self, args):
        method, path, body = args[0], args[1], args[2]
        return f"header('Access-Control-Allow-Origin: *'); header('Access-Control-Allow-Headers: Content-Type'); if (isset($_SERVER['REQUEST_METHOD']) && $_SERVER['REQUEST_METHOD'] === '{method}' && parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) === {path}) {body}"
    def fn_def(self, args):
        fn_name = str(args[0])
        params = [f"${p}" for p in args[1:-1] if p is not None]
        params_str = ", ".join(params)
        body = args[-1]
        return f"function {fn_name}({params_str}) {body}"
    def fn_call(self, args):
        fn_name = str(args[0])
        call_args = ", ".join([str(a) for a in args[1:] if a is not None])
        return f"{fn_name}({call_args})"
    def start(self, args):
        statements = "\n    ".join([str(s) for s in args if s is not None])
        return f"<?php\n{statements}\n?>"

# --- 4. Live Dev Server ---
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
            query_params = urllib.parse.parse_qs(parsed.query)
            
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

# --- 5. PHASE 0.2 TOOLING ---
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
    mamba_config = f'{{\n  "name": "{project_name}",\n  "version": "0.1.0",\n  "main": "main.mb"\n}}\n'
    
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

def run_tests(filename):
    print(f"🧪 Running Mamba Test Suite: '{filename}'...\n")
    build_and_run(filename, target="cpp")

# --- 6. PRODUCTION BUILD TOOLCHAIN (`mamba build`) ---
def mamba_build(filename, target="cpp", release=True):
    print("🔨 Building Mamba Application...")
    with open(GRAMMAR_PATH, 'r') as g_file: grammar = g_file.read()
    parser = Lark(grammar, parser='lalr')
    code = resolve_imports(filename)
    tree = parser.parse(code)
    
    os.makedirs('dist', exist_ok=True)

    if target == "cpp":
        generator = CppGenerator()
        cpp_code = generator.transform(tree)
        cpp_file = "dist/output_temp.cpp"
        binary_file = "dist/mamba_app"
        with open(cpp_file, "w") as f: f.write(cpp_code)
        
        opt_flag = "-O3" if release else "-O0"
        mode_str = "Release (-O3)" if release else "Debug (-O0)"
        
        print(f"⚡ Target: Native C++ ({mode_str})")
        
        compile_cmd = f"clang++ {opt_flag} -std=c++17 {cpp_file} -lsqlite3 -o {binary_file}"
        res = subprocess.run(compile_cmd, shell=True)
        
        if os.path.exists(cpp_file):
            os.remove(cpp_file)
            
        if res.returncode == 0:
            mamba_manifest = {
                "name": "Mamba App",
                "version": "0.1.0",
                "target": "cpp",
                "binary": "mamba_app"
            }
            with open("dist/mamba.json", "w") as f:
                json.dump(mamba_manifest, f, indent=2)
                
            file_size_kb = os.path.getsize(binary_file) / 1024
            print(f"📦 Output Directory: dist/")
            print(f"   └── dist/mamba_app ({file_size_kb:.1f} KB)")
            print(f"   └── dist/mamba.json")
            print(f"✨ Build Complete! Run with: ./dist/mamba_app")
        else:
            print("❌ C++ Compilation Failed!")

    elif target == "php":
        php_code = PhpGenerator().transform(tree)
        php_file = "dist/app.php"
        with open(php_file, "w") as f: f.write(php_code)
        
        mamba_manifest = {
            "name": "Mamba App",
            "version": "0.1.0",
            "target": "php",
            "main": "app.php"
        }
        with open("dist/mamba.json", "w") as f:
            json.dump(mamba_manifest, f, indent=2)

        print(f"🌐 Target: PHP Web Application")
        print(f"📦 Output Directory: dist/")
        print(f"   └── dist/app.php")
        print(f"   └── dist/mamba.json")
        print(f"✨ Build Complete!")

# --- 7. Execution Driver ---
def build_and_run(filename, target="cpp", release=False):
    mamba_build(filename, target, release)
    print("🚀 Running Application:\n---------------------------------")
    if target == "cpp":
        subprocess.run("./dist/mamba_app", shell=True)
    elif target == "php" and shutil.which("php"):
        subprocess.run("php dist/app.php", shell=True)

if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage:")
            print("  ./mamba <script.mb> [--target cpp|php] [--release]")
            print("  ./mamba build <script.mb> [--target cpp|php] [--release]")
            print("  ./mamba serve <script.mb>")
            print("  ./mamba init <project_name>")
            print("  ./mamba fmt <script.mb>")
            print("  ./mamba test <script.mb>")
        elif sys.argv[1] == "build":
            script = "examples/sqlite_app.mb"
            target = "cpp"
            release = "--release" in sys.argv or "-r" in sys.argv or True
            
            if "--target" in sys.argv:
                t_idx = sys.argv.index("--target") + 1
                if t_idx < len(sys.argv):
                    target = sys.argv[t_idx]
                    
            for arg in sys.argv[2:]:
                if not arg.startswith("-"):
                    script = arg
                    break
                    
            mamba_build(script, target, release)
        elif sys.argv[1] == "init":
            proj = sys.argv[2] if len(sys.argv) > 2 else "my_mamba_app"
            init_project(proj)
        elif sys.argv[1] == "fmt":
            script = sys.argv[2] if len(sys.argv) > 2 else "examples/phase_01.mb"
            format_code(script)
        elif sys.argv[1] == "test":
            script = sys.argv[2] if len(sys.argv) > 2 else "examples/test_suite.mb"
            run_tests(script)
        elif sys.argv[1] == "serve":
            script_file = sys.argv[2] if len(sys.argv) > 2 else "examples/web.mb"
            start_mamba_server(script_file)
        else:
            file = sys.argv[1]
            target = "cpp"
            release = "--release" in sys.argv or "-r" in sys.argv
            
            if "--target" in sys.argv:
                t_idx = sys.argv.index("--target") + 1
                if t_idx < len(sys.argv):
                    target = sys.argv[t_idx]
                    
            build_and_run(file, target, release)
    except KeyboardInterrupt:
        print("\n🛑 Execution stopped.")
        sys.exit(0)