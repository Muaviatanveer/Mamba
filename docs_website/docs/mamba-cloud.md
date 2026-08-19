# Mamba Cloud (PaaS)

Mamba 0.3.0 transforms the compiler into a complete Developer-to-Deployment Ecosystem via Mamba Cloud.

## Instant Deployment

The Mamba Cloud engine allows you to deploy applications instantly to a local runtime environment.

```bash
./mamba deploy 8080
```

*This command automatically compiles the native C++ binary, daemonizes it, and maps it to the given port.*

## Multi-Language Detection
Mamba Cloud does not only run `.mb` files. It auto-detects and deploys:
- **Mamba Native C++**
- **Node.js** (`package.json`)
- **Python** (`app.py` or `requirements.txt`)

## The Reverse Proxy Gateway

Mamba Cloud includes a built-in routing gateway to manage active deployments using custom Virtual Hosts (`.mamba.local`).

Start the gateway:
```bash
./mamba proxy 8000
```
This enables zero-config local domains (e.g., `http://my-api.mamba.local:8000`).

## Bare Git Auto-Deploy Server

You can configure a Git repository to automatically deploy code directly via `git push`.

1. Initialize the deployment server:
   ```bash
   ./mamba git-init my_api
   ```
2. Add the remote and push:
   ```bash
   git remote add mamba_cloud ../mamba_cloud_repos/my_api.git
   git push mamba_cloud main
   ```

*Upon push, Mamba intercepts the hook, natively compiles the C++ codebase, and orchestrates a zero-downtime swap of the running processes.*

## Global Edge Bridges

Instantly expose your local deployments to the global internet via integrated tunneling (e.g., Cloudflare).

```bash
./mamba deploy 8081 --public
```
