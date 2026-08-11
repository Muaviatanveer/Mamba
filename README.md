# 🐍 Mamba Programming Language

[![Release](https://img.shields.io/github/v/release/Muaviatanveer/Mamba?color=00e676&label=Latest%20Release)](https://github.com/Muaviatanveer/Mamba/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **One Mamba Source → Multiple Execution Targets.**  
> A multi-target programming language offering the syntax simplicity of Python, the deployment ease of PHP, and the native performance of C++.

---

### 📦 Latest Release (v0.1.0)
Download pre-built release binaries and the VS Code / Cursor Extension (`mamba-extension-v0.1.0.zip`) directly from [GitHub Releases](https://github.com/Muaviatanveer/Mamba/releases/latest).

---

## 🚀 Key Highlights

- **Zero Friction Syntax** — Clean braces `{}`, explicit `let` / `fn` keywords, and zero indentation bugs.
- **Multi-Target Compilation**
  - **C++ Target** (`--target cpp`) — Compiles to an **~80 KB standalone C++ binary** embedding a zero-dependency POSIX socket HTTP server.
  - **PHP Target** (`--target php`) — Transpiles to deployment-ready PHP web scripts.
  - **Dev Server** (`mamba serve`) — Live development web server.
- **Embedded SQLite Database** — Native SQLite linking (`-lsqlite3`) compiled directly into your binary.
- **Native Web & Testing Syntax** — First-class `route` and `test` keywords built into the core language.

---

## 📊 Benchmark Summary (20,000 Requests, Concurrency 100)

In local Mac benchmark tests (macOS, `ab -n 20000 -c 100`):

| Language / Server | Requests / Sec | Latency (mean) | Binary Size / Footprint |
| :--- | :---: | :---: | :---: |
| Raw C++ (`clang++ -O3`) | **35,838 req/s** | 0.028 ms | 75 KB |
| 🐍 **Mamba Native** (`clang++ -O3`) | **29,019 req/s** | **0.034 ms** | **80 KB** |
| Rust (`rustc -O`) | 28,500 req/s | 0.035 ms | 320 KB |
| Python (`http.server`) | 15,072 req/s | 0.066 ms | Python Runtime |
| PHP (`cli-server`) | 16,161 req/s | 0.061 ms | PHP Runtime |

- **Extreme Stress Reliability** — 0 failed requests out of 150,000 Mamba requests under 1,000 concurrent socket connections.
- **Throughput** — Mamba's native C++ target achieved 99% of the throughput of the hand-written C++ server in 1,000-concurrency stress testing (23,267 req/s vs 23,499 req/s).

---

## 🛠 Quick Start

### 1. Installation

Clone the repository and set up the virtual environment:

```bash
git clone https://github.com/mamba-lang/mamba.git
cd Mamba
python3 -m venv venv
source venv/bin/activate
pip install lark
chmod +x mamba
```

### 2. Scaffold a New Project

```bash
./mamba init my_app
cd my_app
```

### 3. Write Your API (`main.mb`)

```mamba
let db_status = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS users (name TEXT, role TEXT)")

route POST "/api/users" {
    let payload = json.parse(req.body())
    let name = payload["name"]
    let role = payload["role"]

    db.query("INSERT INTO users VALUES ('" + name + "', '" + role + "')")

    return json.stringify({
        "status": "saved",
        "name": name
    })
}
```

### 4. Build Production Executable

```bash
../mamba build main.mb --release
```

Output generated in `dist/`:

```
dist/
├── mamba_app   (80.1 KB Standalone Native Executable)
└── mamba.json
```

### 5. Execute Production Server

```bash
PORT=3000 ./dist/mamba_app
```

Test your endpoint:

```bash
curl -X POST http://localhost:3000/api/users -d '{"name": "Muavia", "role": "AI Engineer"}'
```

---

## 💻 CLI Commands

| Command | Description |
| :--- | :--- |
| `./mamba <file.mb>` | Compiles and executes code in debug mode. |
| `./mamba build <file.mb> --release` | Compiles an optimized release binary to `dist/`. |
| `./mamba build <file.mb> --target php` | Transpiles Mamba code to a PHP backend. |
| `./mamba serve <file.mb>` | Launches live development server. |
| `./mamba init <project_name>` | Scaffolds a new project structure. |
| `./mamba fmt <file.mb>` | Formats code automatically. |
| `./mamba test <file.mb>` | Runs built-in test suite assertions. |

---

## 📜 License

MIT License