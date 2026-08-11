# 🐍 Mamba 0.1 Language Specification

Mamba is a multi-target, compiled programming language designed for building high-performance microservices, web APIs, and portable applications.

---

## 1. Architectural Philosophy

Mamba decouples source syntax from execution backends — **"One Mamba Source → Multiple Execution Targets."**

| Target | Flag | Description |
| :--- | :--- | :--- |
| **C++ Native** | `--target cpp` | Compiles Mamba code to C++20 and invokes `clang++` (`-O3`) to produce a standalone machine-code executable (`dist/mamba_app`) embedding a zero-dependency POSIX socket HTTP server. |
| **PHP Web** | `--target php` | Transpiles Mamba code into deployment-ready PHP scripts (`dist/app.php`). |
| **Development Server** | `mamba serve` | In-memory dev server with dynamic route reflection and automatic port fallback. |

---

## 2. Syntax & Grammar

### 2.1 Variables

Variables are declared using the explicit `let` keyword. Variable reassignment uses `=`.

```mamba
let app_name = "Mamba API"
let port = 8000
let is_active = 1
```

### 2.2 Automatic String Interpolation

Any string literal enclosed in double quotes automatically evaluates `{variable}` expressions:

```mamba
let user = "Muavia"
print("Welcome, {user}!")
```

### 2.3 Comments

Mamba supports both hash (`#`) and double-slash (`//`) line comments:

```mamba
# This is a comment
// This is also a comment
```

---

## 3. Collections

### 3.1 Lists / Arrays

Ordered collections of items defined with brackets `[...]`:

```mamba
let fruits = ["Apple", "Banana", "Cherry"]
print(fruits[0])
```

### 3.2 HashMaps / Dictionaries

Key-value pairs defined with braces `{...}`:

```mamba
let user = {
    "name": "Muavia",
    "role": "AI Engineer"
}

print(user["name"])
```

---

## 4. Functions

Functions are defined using `fn` and return values using `return`:

```mamba
fn add_tax(price, tax_rate) {
    return price + (price * tax_rate)
}

let total = add_tax(100, 0.15)
```

---

## 5. Control Flow

### 5.1 Conditionals (`if` / `else`)

Brace-delimited conditional blocks without requiring parenthetical colons:

```mamba
if score >= 50 {
    print("Status: Passed")
} else {
    print("Status: Failed")
}
```

### 5.2 Loops (`while`)

Condition-based iteration blocks:

```mamba
let count = 0
while count < 5 {
    print("Count: {count}")
    let count = count + 1
}
```

---

## 6. Exception Handling

Structured exception handling using `try` / `catch`:

```mamba
try {
    let content = file.read("data.txt")
    print(content)
} catch (err) {
    print("Failed to read file")
}
```

---

## 7. Web Routing Engine

Web endpoints are first-class language keywords built into Mamba's core grammar:

```mamba
route GET "/api/health" {
    return json.stringify({ "status": "ok" })
}

route POST "/api/users" {
    let payload = json.parse(req.body())
    let user_name = payload["name"]
    return json.stringify({ "status": "created", "name": user_name })
}
```

### 7.1 Request Context Helpers

Inside route handlers, `req` provides inspection method calls:

| Method | Description |
| :--- | :--- |
| `req.body()` | Returns raw incoming HTTP request body string. |
| `req.query("key")` | Reads URL query string parameters (`/api/search?q=mamba`). |
| `req.header("key")` | Reads HTTP request headers (`Authorization`). |

---

## 8. Embedded Database Engine (`db`)

Mamba natively links SQLite (`-lsqlite3`) at compile time for zero-setup database storage:

```mamba
let conn = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS users (name TEXT, role TEXT)")
db.query("INSERT INTO users VALUES ('Muavia', 'AI Engineer')")
```

---

## 9. Standard Library Reference

| Module | Method | Description |
| :--- | :--- | :--- |
| **`env`** | `env.get("PORT")` | Reads system environment variables. |
| **`json`** | `json.stringify(map)` | Converts HashMap to JSON string. |
| **`json`** | `json.parse(str)` | Converts JSON string to HashMap. |
| **`file`** | `file.read("path")` | Reads text file. |
| **`file`** | `file.write("path", "data")` | Writes text file. |
| **`http`** | `http.get("url")` | Fetches external HTTP resource. |
| **`db`** | `db.open("path")` | Opens embedded SQLite database. |
| **`db`** | `db.query("SQL")` | Executes SQL statement. |
| **`str`** | `str.upper(s)` | Converts string to uppercase. |
| **`str`** | `str.lower(s)` | Converts string to lowercase. |
| **`str`** | `str.replace(s, old, new)` | Replaces substring. |

---

## 10. Native Testing Syntax

Native unit test suites defined directly in Mamba source code:

```mamba
test "Addition Test" {
    let result = 10 + 20
    assert(result == 30)
}
```

---

## 11. Modular System (`import`)

Code reuse across multiple `.mb` files using recursive import resolving:

```mamba
import "helpers.mb"
```