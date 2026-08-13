# 🐍 Mamba 0.2.0 Language Specification

Mamba is a multi-target, compiled programming language designed for building high-performance microservices, web APIs, and portable applications.

---

## 1. Architectural Philosophy
Mamba decouples source syntax from execution backends (**"One Mamba Source → Multiple Execution Targets"**):

1. **C++ Native Target (`--target cpp`):** Compiles Mamba code to C++20 and invokes `clang++` (`-O3`) to produce a standalone machine-code executable (`dist/mamba_app`) embedding a zero-dependency POSIX socket HTTP server with a `std::thread` worker pool.
2. **PHP Web Target (`--target php`):** Transpiles Mamba code into deployment-ready PHP scripts (`dist/app.php`).
3. **Development Server (`mamba serve`):** In-memory dev server with dynamic route reflection and automatic port fallback.

---

## 2. Syntax & Grammar

### 2.1 Variables
Variables are declared using the explicit `let` keyword.

```mamba
let app_name = "Mamba API"
let port = 8000
```

### 2.2 Automatic String Interpolation

Any string literal enclosed in double quotes automatically evaluates `{variable}` expressions:

```mamba
let user = "Muavia"
print("Welcome, {user}!")
```

### 2.3 Comments

Supports both hash (`#`) and double-slash (`//`) line comments.

---

## 3. Collections & Ergonomic Methods

### 3.1 Lists / Arrays

```mamba
let fruits = ["Apple", "Banana"]

arr.push(fruits, "Cherry")          # Appends item
let joined = arr.join(fruits, " | ") # Joins into string
if arr.contains(fruits, "Banana") { # Checks existence
    print("Contains Banana!")
}
```

### 3.2 HashMaps / Dictionaries

```mamba
let user = {
    "name": "Muavia",
    "role": "AI Engineer"
}

if map.has(user, "name") {          # Checks key existence
    print(user["name"])
}
map.remove(user, "role")           # Removes key
```

---

## 4. Functions & Control Flow

```mamba
fn add(a, b) {
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

---

## 5. Exception Handling

```mamba
try {
    let content = file.read("data.txt")
} catch (err) {
    print("Failed to read file")
}
```

---

## 6. Web Routing Engine

Web endpoints are first-class language keywords built into Mamba:

```mamba
route GET "/api/search" {
    let q = req.query("q")
    return json.stringify({ "search": q })
}

route POST "/api/users" {
    let payload = json.parse(req.body())
    let name = payload["name"]
    let role = payload["role"]
    
    # Safe Parameterized SQL Query
    db.query("INSERT INTO users (name, role) VALUES (?, ?)", [name, role])
    
    return json.stringify({ "status": "created", "name": name })
}
```

---

## 7. Embedded Database Engine (db)

Mamba natively links SQLite (`-lsqlite3`) at compile time and supports prepared statement parameter binding:

```mamba
let conn = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS users (name TEXT, role TEXT)")
db.query("INSERT INTO users (name, role) VALUES (?, ?)", ["Muavia", "AI Engineer"])
```

---

## 8. Standard Library Reference

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
| **`str`**  | `str.len(s)`                    | Returns string length.              |
| **`arr`**  | `arr.push(a, val)`              | Appends item to array.              |
| **`arr`**  | `arr.contains(a, val)`          | Checks if item exists in array.     |
| **`arr`**  | `arr.join(a, sep)`              | Formats array into string.          |
| **`map`**  | `map.has(m, key)`               | Checks if key exists in HashMap.    |
| **`map`**  | `map.remove(m, key)`            | Removes key from HashMap.           |

---

## 9. Native Testing Syntax

```mamba
test "Verify Addition" {
    assert(add(10, 20) == 30)
}
```