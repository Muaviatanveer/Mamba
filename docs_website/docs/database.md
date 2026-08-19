# Database Integration

Mamba natively links SQLite (`-lsqlite3`) into your compiled binaries. This eliminates the need for separate database server processes for embedded data tasks.

## Opening a Database

Initialize a connection using the `db.open()` command. This creates the `.db` file if it does not exist.

```mamba
let conn = db.open("app.db")
```

## Parameterized Queries (Safe SQL)

Always use parameterized queries (`?`) to prevent SQL injection. Mamba securely binds parameters natively.

### Creating Tables
```mamba
db.query("CREATE TABLE IF NOT EXISTS users (name TEXT, role TEXT)")
```

### Inserting Data
Provide parameters as a Mamba array in the second argument.
```mamba
db.query(
    "INSERT INTO users (name, role) VALUES (?, ?)",
    ["Alex", "Admin"]
)
```

### Selecting Data
`db.query` on a `SELECT` statement returns a JSON-compatible string array of results.
```mamba
let users = db.query("SELECT * FROM users")
print(users)
```

## Web + Database Example

This is a hero example demonstrating a fully functional SQLite-backed API in Mamba.

```mamba
db.open("users.db")

db.query("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")

route POST "/api/users" {
    let body = req.body()
    let user = json.parse(body)

    db.query(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        [user["name"], user["email"]]
    )

    return json.stringify({
        "status": "created"
    })
}
```

**Architecture Flow:**
```text
React / Client
      ↓ (HTTP POST)
Mamba Web Route
      ↓
JSON Parse Payload
      ↓
Prepared Statement Binding
      ↓
SQLite Engine
```
