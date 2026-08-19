# 🏁 Getting Started with Mamba Cloud (v0.3.0)

Learn how to build, compile, and deploy a REST API to your own Mamba Cloud PaaS in under 5 minutes.

---

## Step 1: Scaffold Your Application

```bash
./mamba init my_api
cd my_api
```

## Step 2: Write Your Code (`main.mb`)

```mamba
let res = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")

# POST Endpoint (Safe Parameterized Query)
route POST "/api/items" {
    let payload = json.parse(req.body())
    let item_name = payload["name"]
    
    db.query("INSERT INTO items (name) VALUES (?)", [item_name])
    
    return json.stringify({
        "status": "created",
        "item": item_name
    })
}
```

## Step 3: Deploy to Mamba Cloud Runtime

Mamba Cloud will automatically compile your code to a native C++ binary and deploy the process container.

```bash
../mamba deploy 8081
```

Expected Output:
```text
✨ DEPLOYMENT SUCCESSFUL!
   ➜ Type: MAMBA
   ➜ Local Port: http://localhost:8081
   ➜ Custom Domain: http://my_api.mamba.local:8000
```

## Step 4: Route via Domain Gateway

Launch the Mamba Cloud Reverse Proxy to enable custom domain routing:

```bash
../mamba proxy 8000
```

Test your deployed API using the Virtual Host domain!

```bash
curl -X POST http://my_api.mamba.local:8000/api/items -d '{"name": "Mamba Compiler"}'
```

## Step 5 (Optional): Git Push Auto-Deployment

Set up your own bare-metal deployment server:

```bash
../mamba git-init my_api_repo
git remote add mamba_cloud ../mamba_cloud_repos/my_api_repo.git
git push mamba_cloud main
```

Mamba Cloud will intercept the push, compile your C++ binary, and swap the processes automatically with zero downtime!