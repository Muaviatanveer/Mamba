# 🐍 Mamba 0.3.0 Language Specification

Mamba is a multi-target, compiled programming language designed for building
high-performance microservices, web APIs, and portable applications.

1. Architectural Philosophy

Mamba decouples source syntax from execution backends ("One Mamba Source →
Multiple Execution Targets"):

1.  C++ Native Target (--target cpp): Compiles Mamba code to C++20 and invokes
    clang++ (-O3) to produce a standalone machine-code executable
    (dist/mamba_app) embedding a multi-threaded POSIX socket HTTP server
    (std::thread pool) and SQLite database driver.
2.  PHP Web Target (--target php): Transpiles Mamba code into deployment-ready
    PHP scripts (dist/app.php).
3.  Development Server (mamba serve): In-memory dev server with dynamic route
    reflection and automatic port fallback.

2. Syntax & Grammar

2.1 Variables

Variables are declared using the explicit let keyword.

```mamba
let app_name = "Mamba API"
let port = 8000
let is_active = 1
```

2.2 Automatic String Interpolation

Any string literal enclosed in double quotes automatically evaluates {variable}
expressions at runtime:

```mamba
let user = "Muavia"
let role = "AI Engineer"
print("User {user} is registered as {role}")
```

2.3 Comments

Mamba supports both hash (#) and double-slash (//) line comments:

```mamba
# This is a comment
// This is also a comment
```

3. Collections & Ergonomic Methods

3.1 Lists / Arrays

Ordered collections of items defined with brackets [...]:

```mamba
let fruits = ["Apple", "Banana"]

arr.push(fruits, "Cherry")          # Appends item
let joined = arr.join(fruits, " | ") # Returns "Apple | Banana | Cherry"
if arr.contains(fruits, "Banana") { # Returns 1 (True)
    print("Found Banana!")
}
```

3.2 HashMaps / Dictionaries

Key-value pairs defined with braces {...}:

```mamba
let user = {
    "name": "Muavia",
    "role": "AI Engineer",
    "temp": "delete_me"
}

if map.has(user, "name") {          # Checks key existence
    print(user["name"])
}
map.remove(user, "temp")           # Removes key from HashMap
```

4. Functions & Control Flow

4.1 Functions

Defined using fn and return values using return:

```mamba
fn add_tax(price, tax_rate) {
    return price + (price * tax_rate)
}

let total = add_tax(100, 0.15)
```

4.2 Conditionals (if / else)

Brace-delimited blocks without colon requirements:

```mamba
if score >= 50 {
    print("Status: Passed")
} else {
    print("Status: Failed")
}
```

4.3 Loops (while)

Condition-based iteration blocks:

```mamba
let count = 0
while count < 5 {
    print("Count: {count}")
    let count = count + 1
}
```

5. Exception Handling

Structured exception handling using try / catch:

```mamba
try {
    let content = file.read("data.txt")
    print(content)
} catch (err) {
    print("Handled Exception: File not found")
}
```

6. Web Routing Engine & Request Context

Web endpoints are first-class language keywords built into Mamba's core grammar.
All routes return native Access-Control-Allow-Origin: * CORS headers.

```mamba
route GET "/api/search" {
    let query_term = req.query("q")
    return json.stringify({ "status": "success", "search": query_term })
}

route POST "/api/users" {
    let auth_header = req.header("Authorization")
    let raw_payload = req.body()
    let payload = json.parse(raw_payload)
    
    let name = payload["name"]
    let role = payload["role"]
    
    # Safe Parameterized Query
    db.query("INSERT INTO users (name, role) VALUES (?, ?)", [name, role])
    
    return json.stringify({ "status": "created", "name": name })
}
```

Request Context API (req)

  - req.body() ➔ Returns raw incoming HTTP POST/PUT request body payload string.
  - req.query("key") ➔ Reads URL query string parameters (/api/search?q=mamba).
  - req.header("key") ➔ Reads HTTP request headers (Authorization).

7. Embedded Database Engine (db)

Mamba natively links SQLite (-lsqlite3) at compile time and supports safe
prepared statement parameter binding:

```mamba
let conn = db.open("app.db")
db.query("CREATE TABLE IF NOT EXISTS users (name TEXT, role TEXT)")

# Protected Parameterized SQL
db.query("INSERT INTO users (name, role) VALUES (?, ?)", ["Muavia", "AI Engineer"])
```

8. Standard Library API Reference

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
| **`str`**  | `str.upper(s)` / `str.lower(s)` | Converts string case.               |
| **`str`**  | `str.replace(s, old, new)`      | Replaces substring.                 |
| **`str`**  | `str.len(s)`                    | Returns string character count.     |
| **`arr`**  | `arr.push(a, val)`              | Appends item to array.              |
| **`arr`**  | `arr.contains(a, val)`          | Checks if item exists in array.     |
| **`arr`**  | `arr.join(a, sep)`              | Formats array into string.          |
| **`arr`**  | `arr.len(a)`                    | Returns array element count.        |
| **`map`**  | `map.has(m, key)`               | Checks if key exists in HashMap.    |
| **`map`**  | `map.remove(m, key)`            | Removes key from HashMap.           |

9. Native Testing Syntax

Native unit test suites defined directly in Mamba source code:

```mamba
import "helpers.mb"

test "Verify Addition Logic" {
    let result = add(10, 20)
    assert(result == 30)
}
```

10. Modular System (import)

Code reuse across multiple .mb files using recursive import resolving:

```mamba
import "helpers.mb"
```

