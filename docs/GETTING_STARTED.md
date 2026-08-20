# 🏁 Getting Started with Mamba & Mamba Cloud
(v0.3.0)

Learn how to build, compile, and deploy a REST API to Mamba Cloud in under 5
minutes.

Step 1: Scaffold Your Application

```bash
./mamba init my_mamba_api
cd my_mamba_api
```

This generates a clean project layout:

```text
my_mamba_api/
├── main.mb
├── helpers.mb
├── mamba.json
└── .gitignore
```

Step 2: Write Your Code (main.mb)

```mamba
# Initialize Embedded SQLite database
let res = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")

# GET Endpoint
route GET "/api/status" {
    return json.stringify({
        "status": "online",
        "engine": "Mamba Native C++"
    })
}

# POST Endpoint (Protected Parameterized Query)
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

Step 3: Run Unit Tests

```bash
../mamba test test_app.mb
```

Step 4: Deploy to Mamba Cloud Runtime

Deploy your application directly using Mamba Cloud:

```bash
../mamba deploy 8081
```

Expected Output:

```text
✨ DEPLOYMENT SUCCESSFUL!
   ➜ Type: MAMBA
   ➜ Local Port: http://localhost:8081
   ➜ Official Domain: http://my_mamba_api.mambacloud.app:8000
```

Step 5: Route via Domain Gateway

Launch the Mamba Cloud Reverse Proxy to enable custom domain routing:

```bash
../mamba proxy 8000
```

Test your API using the custom subdomain:

```bash
curl -X POST http://my_mamba_api.mamba.local:8000/api/items -d '{"name": "Mamba Compiler"}'
```

Step 6 (Optional): Git Push Auto-Deployment

Set up bare-metal Git deployment:

```bash
../mamba git-init my_mamba_api_repo
git remote add mamba_cloud ../mamba_cloud_repos/my_mamba_api_repo.git
git push mamba_cloud main
```

Mamba Cloud will intercept the push, compile your C++ binary, and swap the
processes automatically with zero downtime! 