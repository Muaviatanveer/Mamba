# ☁️ Mamba Cloud PaaS Architecture Guide

Mamba Cloud is a self-hosted, zero-config Platform-as-a-Service (PaaS) engine
integrated directly into the Mamba CLI (./mamba).

🎯 Architecture Overview

```text
                        DEVELOPER LAPTOP
                               │
                      `git push mamba_cloud main`
                               │
                               ▼
            ┌──────────────────────────────────────┐
            │     MAMBA CLOUD SERVER (VPS)         │
            ├──────────────────────────────────────┤
            │ 1. Git Bare Repository               │
            │    `mamba_cloud_repos/app_name.git`  │
            │    Intercepts push via hook          │
            │                                      │
            │ 2. Build Engine                      │
            │    Auto-detects Mamba, Node, Python  │
            │    Compiles C++ Release (-O3)        │
            │                                      │
            │ 3. Process Container Manager         │
            │    Runs app on isolated port (8081)  │
            │                                      │
            │ 4. Mamba Reverse Proxy Gateway       │
            │    Routes `http://app.mambacloud.app`│
            └──────────────────────────────────────┘
```

🛠️ CLI Cloud Commands

1. ./mamba deploy [port] [--live]

Compiles your code to a native C++ release binary, allocates an isolated process
port, launches the process container, and runs an HTTP health check:

```bash
./mamba deploy 8081
```

Adding --live or --public establishes an instant, zero-prompt global HTTPS edge
tunnel:

```bash
./mamba deploy 8081 --live
```

2. ./mamba proxy [port]

Launches the Mamba Cloud Reverse Proxy Router. It intercepts incoming HTTP
requests on port 8000 (or port 80) and inspects the Host header to route traffic
to the correct container port:

```bash
./mamba proxy 8000
```

Virtual Host Mapping:

  - http://my_api.mambacloud.app:8000 ➔ Routes to 127.0.0.1:8081
  - http://blog.mambacloud.app:8000 ➔ Routes to 127.0.0.1:8082

3. ./mamba git-init <app_name>

Creates a Bare Git Repository inside mamba_cloud_repos/<app_name>.git with an
automated post-receive build hook.

```bash
./mamba git-init my_app
```

Then add remote and push:

```bash
git remote add mamba_cloud mamba_cloud_repos/my_app.git
git push mamba_cloud main
```

Git will intercept the push, compile the C++ release binary, swap process PIDs,
and deploy the application with zero downtime!

4. Process Management Commands

  - ./mamba status ➔ Lists all active deployments, process PIDs, ports, and
    domains.
  - ./mamba logs [app_name] ➔ Streams live application logs from dist/logs/.
  - ./mamba stop [app_name] ➔ Terminates active deployment processes.

🌐 Multi-Language Detection Support

Mamba Cloud automatically detects the project stack in the pushed repository:

1.  Mamba Application: Detects main.mb or mamba.json ➔ Runs ./mamba build
    --release.
2.  Node.js Application: Detects package.json ➔ Runs npm install ➔ Starts npm
    start.
3.  Python Application: Detects requirements.txt / app.py ➔ Installs
    requirements ➔ Starts python3 app.py. 