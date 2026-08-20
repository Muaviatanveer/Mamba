<p align="center">
  <img src="extension/logo.png" alt="Mamba Logo" width="200"/>
</p>

# 🐍 Mamba Programming Language & Cloud Ecosystem
[![Release](https://img.shields.io/github/v/release/Muaviatanveer/Mamba?color=00e676&label=Mamba%20v0.3.0)](https://github.com/Muaviatanveer/Mamba/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **One Mamba Source → Multiple Execution Targets → Live Global URL.**  
> A multi-target programming language offering the syntax simplicity of Python, the native performance of C++, and a built-in zero-config deployment PaaS.
> 
> 🌐 **Official Website:** [mamba-website.mambacloud.app](https://mamba-website.mambacloud.app)

---

## 🚀 Key Highlights (v0.3.0)

### 1. The Language & Compiler
* **Zero Friction Syntax:** Clean braces `{}`, explicit `let` / `fn` keywords, zero indentation bugs.
* **Native C++ Compilation:** Compiles to a **~80 KB standalone C++ binary** (`-O3` optimized) embedding a zero-dependency POSIX socket HTTP server.
* **Multi-Target:** Transpile to Native C++20 or PHP web scripts.
* **Embedded SQLite Database:** Native SQLite linking (`-lsqlite3`) with **Parameterized SQL Safe Queries**.

### 2. Mamba Cloud PaaS (New in v0.3.0)
* **Self-Hosted Deployment Engine:** Mamba includes its own mini-Vercel/Heroku PaaS engine.
* **`git push` to Deploy:** Push code to the Mamba Bare Git Server to auto-trigger native compilation and deployment in 3 seconds.
* **Multi-Language Support:** Auto-detects and deploys Mamba C++, Python, and Node.js applications.
* **Gateway Router & Virtual Hosts:** Built-in Reverse Proxy serving custom subdomains (e.g., `http://my-app.mambacloud.app:8000`).
* **Global Edge Bridges:** Expose local deployments to the global internet instantly via Cloudflare/Serveo.

---

## 📊 Benchmark Summary (macOS Localhost, 50,000 Requests)

In local Mac stress tests at 1,000 concurrent socket connections:

| Language / Server | Requests / Sec | Max Latency | Failures |
| :--- | :---: | :---: | :---: |
| **Raw C++ (`clang++ -O3`)** | **28,552 req/s** | 1088 ms | 0 |
| 🐍 **Mamba Native (`clang++ -O3`)** | **19,811 req/s** | **2024 ms** | **0** |
| **Rust (`rustc -O`)** | **21,868 req/s** | 2025 ms | 0 |
| **PHP (`cli-server`)** | **15,982 req/s** | 2028 ms | 0 |
| **Python (`http.server`)** | **15,007 req/s** | 2023 ms | 0 |

* **Extreme Stress Reliability:** **0 failed requests out of 150,000 Mamba requests**. Mamba maintained absolute thread-pool stability under heavy SQLite/JSON load.

---

## 🛠 Quick Start: From Code to Cloud

### 1. Installation
```bash
git clone https://github.com/Muaviatanveer/Mamba.git
cd Mamba
python3 -m venv venv
source venv/bin/activate
pip install lark
chmod +x mamba
```

### 2. Scaffold & Write Your App
```bash
./mamba init my_api
cd my_api
```

```mamba
# main.mb
let res = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS users (name TEXT, role TEXT)")

route POST "/api/users" {
    let payload = json.parse(req.body())
    db.query("INSERT INTO users (name, role) VALUES (?, ?)", [payload["name"], payload["role"]])
    return json.stringify({ "status": "saved" })
}
```

### 3. Build & Deploy via Mamba Cloud
```bash
../mamba deploy 8081
```

### 4. Route via Custom Domain Gateway
```bash
../mamba proxy 8000
```
Open `http://my-api.mamba.local:8000/api/users` to view your live deployment!

## 💻 CLI Commands

| Command                             | Description                                                       |
| :---------------------------------- | :---------------------------------------------------------------- |
| `./mamba build <file.mb> --release` | Compiles optimized native C++ binary to `dist/`.                  |
| `./mamba deploy [port] [--live]`    | Deploys app to Mamba Cloud Runtime (optional global edge bridge). |
| `./mamba proxy [port]`              | Launches Domain Gateway Router (`*.mamba.local`).                 |
| `./mamba git-init <app>`            | Creates Bare Git Repo for `git push` auto-deploys.                |
| `./mamba status`                    | Lists active deployments, domains, and PIDs.                      |
| `./mamba logs`                      | Streams active application logs.                                  |
| `./mamba stop`                      | Kills active deployment processes.                                |
| `./mamba test <file.mb>`            | Runs built-in test suite assertions.                              |

## 📜 License

MIT License