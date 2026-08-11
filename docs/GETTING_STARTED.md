# 🏁 Getting Started with Mamba

Learn how to build, test, and deploy a REST API in Mamba in under 5 minutes.

---

## Step 1: Scaffold Your Application

```bash
./mamba init my_mamba_api
cd my_mamba_api
```

This creates a clean project directory:

```
my_mamba_api/
├── main.mb
├── helpers.mb
├── mamba.json
└── .gitignore
```

---

## Step 2: Write Your Application (`main.mb`)

Open `main.mb` and paste the following code:

```mamba
# Initialize SQLite database
let res = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")

# GET Endpoint: System status
route GET "/api/status" {
    return json.stringify({
        "status": "online",
        "engine": "Mamba Native C++"
    })
}

# POST Endpoint: Create Item
route POST "/api/items" {
    let payload = json.parse(req.body())
    let item_name = payload["name"]

    db.query("INSERT INTO items (name) VALUES ('" + item_name + "')")

    return json.stringify({
        "status": "created",
        "item": item_name
    })
}
```

---

## Step 3: Run Unit Tests

Add a unit test in `test_app.mb`:

```mamba
fn add(a, b) {
    return a + b
}

test "Verify Addition" {
    assert(add(10, 20) == 30)
}
```

Run tests:

```bash
../mamba test test_app.mb
```

Output:

```
✓ PASS: Verify Addition
```

---

## Step 4: Build Release Binary

Compile your application into a native release executable:

```bash
../mamba build main.mb --release
```

Output:

```
🔨 Building Mamba Application...
⚡ Target: Native C++ (Release -O3)
📦 Output Directory: dist/
   └── dist/mamba_app (80.1 KB)
   └── dist/mamba.json
✨ Build Complete!
```

---

## Step 5: Execute Standalone Binary

Launch your production server:

```bash
PORT=3000 ./dist/mamba_app
```

Test your API from another terminal window:

```bash
curl -X POST http://localhost:3000/api/items -d '{"name": "Mamba Compiler"}'
```

Response:

```json
{"item": "Mamba Compiler", "status": "created"}
```

🎉 You have successfully deployed a native C++ web microservice written in Mamba!