# 🐍 Mamba 0.3.0 Language Specification

Mamba is a multi-target, compiled programming language offering a Python-like developer experience mapped to high-performance C++20 and PHP backends.

---

## 1. Syntax Basics

### Variables & Strings
Variables are declared using the explicit `let` keyword. String interpolation is automatic.
```mamba
let app_name = "Mamba API"
let port = 8000
print("Starting {app_name} on {port}...")
```

### Comments
```mamba
# This is a comment
// This is also a comment
```

## 2. Ergonomic Collections

### Lists / Arrays
Arrays come with built-in ergonomic standard functions.
```mamba
let fruits = ["Apple", "Banana"]
arr.push(fruits, "Cherry")          # Appends item
let joined = arr.join(fruits, " | ") # Returns "Apple | Banana | Cherry"
if arr.contains(fruits, "Banana") { 
    print("Found Banana!") 
}
```

### HashMaps / Dictionaries
Dictionaries support key checks and dynamic JSON serialization.
```mamba
let user = {
    "name": "Muavia",
    "role": "AI Engineer"
}
if map.has(user, "name") {          
    print(user["name"])
}
map.remove(user, "role")           
```

## 3. Control Flow & Exceptions

### Functions & Logic
```mamba
fn calculate(a, b) {
    return a + b
}

if score >= 50 {
    print("Passed")
} else {
    print("Failed")
}

let i = 0
while i < 5 {
    let i = i + 1
}
```

### Try / Catch Exception Handling
```mamba
try {
    let content = file.read("data.txt")
} catch (err) {
    print("Handled Exception!")
}
```

## 4. Web Routing Engine & Context

Web endpoints are first-class language keywords. The `req` object parses request contexts natively.

```mamba
route POST "/api/users" {
    let auth = req.header("Authorization")
    let search = req.query("q")
    
    let payload = json.parse(req.body())
    let user_name = payload["name"]
    
    return json.stringify({ "status": "created", "name": user_name })
}
```

Note: All Mamba routes return native `Access-Control-Allow-Origin: *` CORS headers.

## 5. Embedded Database Engine (`db`)

Mamba natively links SQLite (`-lsqlite3`) and supports secure Prepared Statement Parameter Binding to prevent SQL injection.

```mamba
let conn = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS users (name TEXT, role TEXT)")

# Safe Parameterized SQL
db.query("INSERT INTO users (name, role) VALUES (?, ?)", ["Muavia", "AI Engineer"])
```

## 6. Standard Library Reference

| Module     | Method                          | Description                         |
| :--------- | :------------------------------ | :---------------------------------- |
| **`env`**  | `env.get("PORT")`               | Reads system environment variables. |
| **`json`** | `json.stringify(map)`           | Converts HashMap to JSON string.    |
| **`json`** | `json.parse(str)`               | Converts JSON string to HashMap.    |
| **`file`** | `file.read("path")`             | Reads text file.                    |
| **`file`** | `file.write("path", "data")`    | Writes text file.                   |
| **`http`** | `http.get("url")`               | Fetches external HTTP resource.     |
| **`db`**   | `db.open("path")`               | Opens embedded SQLite database.     |
| **`db`**   | `db.query("SQL", [params])`     | Executes parameterized SQL query.   |
| **`str`**  | `str.upper(s)` / `str.lower(s)` | String case conversion.             |
| **`str`**  | `str.replace(s, old, new)`      | Substring replacement.              |
| **`arr`**  | `arr.push(a, val)`              | Appends item to array.              |
| **`arr`**  | `arr.contains(a, val)`          | Checks if item exists in array.     |
| **`arr`**  | `arr.join(a, sep)`              | Formats array into string.          |
| **`map`**  | `map.has(m, key)`               | Checks if key exists in HashMap.    |
| **`map`**  | `map.remove(m, key)`            | Removes key from HashMap.           |

## 7. Native Testing & Modules

```mamba
import "helpers.mb"

test "Verify Addition" {
    assert(add(10, 20) == 30)
}
```