from lark import Transformer

class CppGenerator(Transformer):
    def __init__(self):
        super().__init__()
        self.has_routes = False
        self.route_code_list = []
        self.non_route_code_list = []

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
    def print_stmt(self, args): return f"mamba_print({args[0]});"
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
    
    def list(self, args):
        items = ", ".join([f"std::string({a})" for a in args if a is not None])
        return f"std::vector<std::string>{{{items}}}"

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
        if obj == "req" and method == "body": return "mamba_req_body()"
        if obj == "req" and method == "query": return f"mamba_req_query({call_args})"
        if obj == "req" and method == "header": return f"mamba_req_header({call_args})"
        if obj == "db" and method == "open": return f"mamba_db_open({call_args})"
        
        if obj == "db" and method == "query":
            parsed_args = [str(a) for a in args[2:] if a is not None]
            if len(parsed_args) > 1:
                return f"mamba_db_query_params({parsed_args[0]}, {parsed_args[1]})"
            return f"mamba_db_query({call_args})"
            
        if obj == "str" and method == "upper": return f"mamba_str_upper({call_args})"
        if obj == "str" and method == "lower": return f"mamba_str_lower({call_args})"
        if obj == "str" and method == "replace": return f"mamba_str_replace({call_args})"
        if obj == "str" and method == "len": return f"mamba_str_len({call_args})"
        
        if obj == "arr" and method == "push": return f"mamba_arr_push({call_args})"
        if obj == "arr" and method == "contains": return f"mamba_arr_contains({call_args})"
        if obj == "arr" and method == "join": return f"mamba_arr_join({call_args})"
        if obj == "arr" and method == "len": return f"mamba_arr_len({call_args})"
        if obj == "map" and method == "has": return f"mamba_map_has({call_args})"
        if obj == "map" and method == "remove": return f"mamba_map_remove({call_args})"

        return f"{obj}.{method}({call_args})"

    def route_def(self, args):
        self.has_routes = True
        method, path, body = args[0], args[1], args[2]
        code = f"""
        if (mamba_req.method == "{method}" && mamba_req.path == {path}) {{
            try {{
                auto mamba_route_handler = [&]() {{ {body} return std::string(""); }};
                std::string body_html = mamba_route_handler();
                std::string content_type = "text/html";
                if (!body_html.empty() && (body_html[0] == '{{' || body_html[0] == '[')) {{
                    content_type = "application/json";
                }}
                std::string resp = "HTTP/1.1 200 OK\\r\\nAccess-Control-Allow-Origin: *\\r\\nAccess-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\\r\\nAccess-Control-Allow-Headers: Content-Type, Authorization\\r\\nContent-Type: " + content_type + "\\r\\nContent-Length: " + std::to_string(body_html.length()) + "\\r\\n\\r\\n" + body_html;
                write(client_fd, resp.c_str(), resp.length());
            }} catch (const std::exception& e) {{
                std::string err_resp = "HTTP/1.1 500 Internal Server Error\\r\\nAccess-Control-Allow-Origin: *\\r\\nContent-Type: application/json\\r\\nContent-Length: 25\\r\\n\\r\\n{{\\"error\\":\\"server_error\\"}}";
                write(client_fd, err_resp.c_str(), err_resp.length());
            }}
            close(client_fd);
            return;
        }}
        """
        self.route_code_list.append(code)
        return ""

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
        non_route_list = []
        for child in args:
            s_str = str(child).strip()
            if s_str and not s_str.startswith("// Mamba Route:"):
                non_route_list.append(s_str)

        global_declarations = "\n".join([s for s in non_route_list if s])
        route_statements = "\n        ".join([s for s in self.route_code_list if s])

        if self.has_routes:
            server_main = f"""
void start_native_cpp_server(int default_port, std::function<void(int)> route_handler) {{
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
    
    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {{
        std::cerr << "Failed to bind to port " << port << std::endl;
        return;
    }}
    
    listen(server_fd, 4096); 
    
    int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 8;
    for (int i = 0; i < num_threads * 2; ++i) {{
        std::thread([route_handler]() {{
            while (true) {{
                int client_fd;
                {{
                    std::unique_lock<std::mutex> lock(mamba_queue_mutex);
                    mamba_queue_cond.wait(lock, []{{ return !mamba_client_queue.empty(); }});
                    client_fd = mamba_client_queue.front();
                    mamba_client_queue.pop();
                }}
                route_handler(client_fd);
            }}
        }}).detach();
    }}
    
    std::cout << "==================================================" << std::endl;
    std::cout << "  ⚡ Multi-Threaded Native C++ Mamba Server on http://localhost:" << port << std::endl;
    std::cout << "  🧵 Active C++ Worker Threads: " << (num_threads * 2) << std::endl;
    std::cout << "==================================================" << std::endl;
    
    while (true) {{
        int client_fd = accept(server_fd, NULL, NULL);
        if (client_fd < 0) continue;
        
        {{
            std::lock_guard<std::mutex> lock(mamba_queue_mutex);
            mamba_client_queue.push(client_fd);
        }}
        mamba_queue_cond.notify_one();
    }}
}}

int main() {{
    {global_declarations}

    auto mamba_router = [&](int client_fd) {{
        char buffer[4096] = {{0}};
        ssize_t bytes_read = read(client_fd, buffer, 4095);
        if (bytes_read <= 0) {{ close(client_fd); return; }}
        
        std::string raw_req(buffer, bytes_read);
        std::stringstream ss(raw_req);
        
        std::string method, full_url, http_ver;
        if (!(ss >> method >> full_url >> http_ver)) {{
            std::string bad_req = "HTTP/1.1 400 Bad Request\\r\\nContent-Length: 15\\r\\n\\r\\n400 Bad Request";
            write(client_fd, bad_req.c_str(), bad_req.length());
            close(client_fd);
            return;
        }}
        
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
            if (mamba_req.method == "OPTIONS") {{
                std::string cors_ok = "HTTP/1.1 204 No Content\\r\\nAccess-Control-Allow-Origin: *\\r\\nAccess-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\\r\\nAccess-Control-Allow-Headers: Content-Type, Authorization\\r\\nContent-Length: 0\\r\\n\\r\\n";
                write(client_fd, cors_ok.c_str(), cors_ok.length());
                close(client_fd);
                return;
            }}

            {route_statements}
            
            std::string not_found = "HTTP/1.1 404 Not Found\\r\\nAccess-Control-Allow-Origin: *\\r\\nContent-Type: text/plain\\r\\nContent-Length: 23\\r\\n\\r\\n404 - Mamba Not Found";
            write(client_fd, not_found.c_str(), not_found.length());
            close(client_fd);
        }} else {{
            close(client_fd);
        }}
    }};

    start_native_cpp_server(8000, mamba_router);
    return 0;
}}
"""
        else:
            server_main = f"""
int main() {{
    {global_declarations}
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
#include <thread>
#include <mutex>
#include <queue>
#include <condition_variable>
#include <functional>
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

std::queue<int> mamba_client_queue;
std::mutex mamba_queue_mutex;
std::condition_variable mamba_queue_cond;

std::string mamba_req_body() {{ return mamba_req.body; }}
std::string mamba_req_query(const std::string& key) {{
    if (mamba_req.query.count(key)) return mamba_req.query[key]; return "";
}}
std::string mamba_req_header(const std::string& key) {{
    if (mamba_req.headers.count(key)) return mamba_req.headers[key]; return "";
}}

sqlite3* mamba_global_db = nullptr;
std::mutex mamba_db_mutex;

std::string mamba_db_open(const std::string& db_path) {{
    std::lock_guard<std::mutex> lock(mamba_db_mutex);
    if (sqlite3_open(db_path.c_str(), &mamba_global_db) == SQLITE_OK) return "db_ok";
    return "db_error";
}}

std::string mamba_db_query(const std::string& sql) {{
    std::lock_guard<std::mutex> lock(mamba_db_mutex);
    if (!mamba_global_db) return "db_not_open";
    char* err_msg = nullptr;
    if (sqlite3_exec(mamba_global_db, sql.c_str(), nullptr, nullptr, &err_msg) == SQLITE_OK) return "query_ok";
    std::string err = err_msg ? std::string(err_msg) : "query_error";
    sqlite3_free(err_msg);
    return err;
}}

std::string mamba_db_query_params(const std::string& sql, const std::vector<std::string>& params) {{
    std::lock_guard<std::mutex> lock(mamba_db_mutex);
    if (!mamba_global_db) return "db_not_open";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(mamba_global_db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {{
        return sqlite3_errmsg(mamba_global_db);
    }}
    for (size_t i = 0; i < params.size(); ++i) {{
        sqlite3_bind_text(stmt, static_cast<int>(i + 1), params[i].c_str(), -1, SQLITE_TRANSIENT);
    }}
    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    if (rc == SQLITE_DONE || rc == SQLITE_OK || rc == SQLITE_ROW) return "query_ok";
    return sqlite3_errmsg(mamba_global_db);
}}

int mamba_str_len(const std::string& str) {{ return str.length(); }}
int mamba_arr_len(const std::vector<std::string>& vec) {{ return vec.size(); }}

void mamba_arr_push(std::vector<std::string>& vec, const std::string& item) {{ vec.push_back(item); }}
bool mamba_arr_contains(const std::vector<std::string>& vec, const std::string& item) {{ return std::find(vec.begin(), vec.end(), item) != vec.end(); }}
std::string mamba_arr_join(const std::vector<std::string>& vec, const std::string& sep) {{
    std::string res = "";
    for (size_t i = 0; i < vec.size(); ++i) {{ if (i > 0) res += sep; res += vec[i]; }}
    return res;
}}

bool mamba_map_has(const std::map<std::string, std::string>& m, const std::string& key) {{ return m.count(key) > 0; }}
void mamba_map_remove(std::map<std::string, std::string>& m, const std::string& key) {{ m.erase(key); }}

std::string mamba_str_upper(std::string str) {{ std::transform(str.begin(), str.end(), str.begin(), ::toupper); return str; }}
std::string mamba_str_lower(std::string str) {{ std::transform(str.begin(), str.end(), str.begin(), ::tolower); return str; }}
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

std::string mamba_http_get(const std::string& url) {{ return "[C++ HTTP Get response for " + url + "]"; }}
std::string mamba_env_get(const std::string& key) {{ char* val = std::getenv(key.c_str()); return val ? std::string(val) : ""; }}

std::string mamba_json_stringify(const std::map<std::string, std::string>& m) {{
    std::string out = "{{";
    bool first = true;
    for (const auto& pair : m) {{
        if (!first) out += ", ";
        std::string k = pair.first;
        std::string v = pair.second;
        if (k.length() >= 2 && k[0] == '"' && k[k.length() - 1] == '"') k = k.substr(1, k.length() - 2);
        if (v.length() >= 2 && v[0] == '"' && v[v.length() - 1] == '"') v = v.substr(1, v.length() - 2);
        out += "\\"" + k + "\\": \\"" + v + "\\"";
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

template<typename T> void mamba_print(const T& val) {{ std::cout << val << std::endl; }}
void mamba_print(const std::map<std::string, std::string>& m) {{ std::cout << mamba_json_stringify(m) << std::endl; }}
void mamba_print(const std::vector<std::string>& vec) {{ std::cout << "[" << mamba_arr_join(vec, ", ") << "]" << std::endl; }}

{server_main}"""