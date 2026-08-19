# Standard Library

Mamba comes with a robust standard library exposing system, network, and data parsing utilities natively.

## Environment (`env`)

Access environment variables provided to the Mamba process.

### `env.get()`
```mamba
let port = env.get("PORT")
```
**Signature:** `env.get(name)`
**Returns:** String representing the environment variable value, or empty if not found.

---

## JSON (`json`)

Native parsing and stringification of JSON data.

### `json.stringify()`
```mamba
let user = { "name": "Alex", "age": 25 }
let payload = json.stringify(user)
```
**Signature:** `json.stringify(map)`
**Returns:** JSON string representation of the HashMap.

### `json.parse()`
```mamba
let user_map = json.parse(payload)
```
**Signature:** `json.parse(str)`
**Returns:** HashMap representing the parsed JSON data.

---

## File System (`file`)

Read and write text files synchronously.

### `file.read()`
```mamba
let content = file.read("hello.txt")
```
**Signature:** `file.read(path)`
**Returns:** String content of the file.

### `file.write()`
```mamba
file.write("hello.txt", "Hello Mamba")
```
**Signature:** `file.write(path, data)`
**Returns:** Nothing.

---

## HTTP Client (`http`)

Execute network requests natively.

### `http.get()`
```mamba
let response = http.get("https://example.com")
print(response)
```
**Signature:** `http.get(url)`
**Returns:** String response body.

---

## String (`str`)

Operations for working with string literals.

### `str.upper()` & `str.lower()`
```mamba
let name = "Mamba"
print(str.upper(name))  # "MAMBA"
```
**Signature:** `str.upper(string)` / `str.lower(string)`

### `str.replace()`
```mamba
let modified = str.replace("Hello World", "World", "Mamba")
```
**Signature:** `str.replace(string, old, new)`
**Returns:** Modified string.
