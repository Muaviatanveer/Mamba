# 🐍 Mamba Programming Language

[![Release](https://img.shields.io/github/v/release/Muaviatanveer/Mamba?color=00e676&label=Mamba%20v0.2.0)](https://github.com/Muaviatanveer/Mamba/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **One Mamba Source → Multiple Execution Targets.**  
> A multi-target programming language offering the syntax simplicity of Python, the deployment ease of PHP, and the native performance of C++.

---

### 📦 Latest Release (v0.2.0)
Download pre-built release binaries and the VS Code / Cursor Extension (`mamba-extension-v0.2.0.zip`) directly from [GitHub Releases](https://github.com/Muaviatanveer/Mamba/releases/latest).

---

## 🚀 Key Highlights in Mamba 0.2.0
* **Parameterized SQL Safety:** `db.query("INSERT INTO users VALUES (?, ?)", [name, role])` using native SQLite3 prepared statements (`sqlite3_prepare_v2`).
* **Ergonomic Collections:** `arr.push()`, `arr.contains()`, `arr.join()`, `map.has()`, `map.remove()`.
* **Multi-Threaded C++ Web Engine:** POSIX socket web server with `std::thread` worker pool (3.7x faster POST database throughput at 9,072 req/s!).
* **CORS Support:** Native `Access-Control-Allow-Origin: *` headers for React/Vue SPA frontends.
* **Modular Compiler Architecture:** Cleanly decoupled compiler core (`compiler/`).

---

## 📊 Benchmark Summary (macOS Localhost, 20,000 Requests)

| Language / Server | 200 Concurrency | 500 Concurrency | 1,000 Concurrency | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Raw C++ (`clang++ -O3`)** | **36,365 req/s** | **31,215 req/s** | **23,499 req/s** | 0 Failures |
| **Rust (`rustc -O`)** | **31,601 req/s** | **26,537 req/s** | **24,383 req/s** | 0 Failures |
| 🐍 **Mamba Native (`-O3`)** | **27,522 req/s** | **24,943 req/s** | **23,267 req/s** | **0 Failures** |
| **Python (`http.server`)** | **23,024 req/s** | **22,713 req/s** | **21,956 req/s** | 0 Failures |
| **PHP (`cli-server`)** | **16,161 req/s** | **16,294 req/s** | **15,589 req/s** | 0 Failures |

* **Zero-Failure Reliability:** **0 failed requests out of 150,000 requests** under 1,000 concurrent sockets.
* **Throughput:** Mamba achieved **99% of raw C++ speed** at 1,000 concurrency.

---

## 🛠 Quick Start

### 1. Installation
```bash
git clone https://github.com/Muaviatanveer/Mamba.git
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

### 3. Build & Run
```bash
../mamba build main.mb --release
PORT=3000 ./dist/mamba_app
```

## 💻 CLI Commands

| Command | Description |
| :--- | :--- |
| `./mamba <file.mb>` | Compiles and executes code in debug mode. |
| `./mamba build <file.mb> --release` | Compiles an optimized release binary to `dist/`. |
| `./mamba serve <file.mb>` | Launches live development server. |
| `./mamba init <project_name>` | Scaffolds new project structure. |
| `./mamba fmt <file.mb>` | Formats code automatically. |
| `./mamba test <file.mb>` | Runs built-in test suite assertions. |

## 📜 License
MIT License