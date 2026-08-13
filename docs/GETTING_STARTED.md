# 🏁 Getting Started with Mamba 0.2.0

Learn how to build, test, and deploy a REST API in Mamba in under 5 minutes.

Step 1: Scaffold Your Application

```bash
./mamba init my_mamba_api
cd my_mamba_api
```

Step 2: Write Your Application (main.mb)

```mamba
# Initialize SQLite database
let res = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")

# GET Endpoint
route GET "/api/status" {
    return json.stringify({
        "status": "online",
        "engine": "Mamba Native C++"
    })
}

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

Step 3: Run Unit Tests

```bash
../mamba test test_app.mb
```

Step 4: Build Release Binary

```bash
../mamba build main.mb --release
```

Output generated in dist/:

```text
dist/
├── mamba_app   (80.1 KB Standalone Native Executable)
└── mamba.json
```

Step 5: Execute Standalone Binary

```bash
PORT=3000 ./dist/mamba_app
```

Test your API:

```bash
curl -X POST http://localhost:3000/api/items -d '{"name": "Mamba Compiler"}'
```