# Language Basics

This section covers the core language syntax of Mamba.

## 1. Comments

Mamba supports both hash and double-slash comments.

```mamba
# This is a comment
// This is also a comment
```

## 2. Variables

Variables are declared using the explicit `let` keyword. String interpolation is automatic in double-quoted strings.

```mamba
let name = "Muavia"
let age = 20
let active = true

print("Name: {name}, Age: {age}")
```

Variables can hold Strings, Numbers, Booleans, Arrays, and HashMaps.

## 3. Data Types

### String
```mamba
let name = "Alex"
```

### Number
```mamba
let age = 25
let price = 99.5
```

### Boolean
```mamba
let active = true
```

### Array
```mamba
let fruits = ["Apple", "Banana", "Cherry"]
```

### HashMap
```mamba
let user = {
    "name": "Alex",
    "age": 25
}
```

Access hash map elements via indexing:
```mamba
print(user["name"])
```

## 4. Operators

Mamba supports the standard suite of programming operators.

**Arithmetic**
`+` `-` `*` `/` `%`

**Comparison**
`==` `!=` `>` `<` `>=` `<=`

**Logical**
`&&` `||` `!`

**Assignment**
`=`

## 5. Control Flow

### If / Else
```mamba
if age >= 18 {
    print("Adult")
} else {
    print("Minor")
}
```

### While Loop
```mamba
let x = 0
while x < 10 {
    x = x + 1
}
```

## 6. Functions

Functions are defined using the `fn` keyword.

```mamba
fn add(a, b) {
    return a + b
}

let result = add(5, 10)
```

## 7. Error Handling

Mamba uses `try` / `catch` blocks for elegant exception management.

```mamba
try {
    let data = file.read("data.txt")
} catch (err) {
    print(err)
}
```

## 8. Modules & Imports

Mamba supports importing other `.mb` files to split up your project.

```mamba
import "helpers.mb"
```

Example structure:
```text
my-app/
├── main.mb
├── helpers.mb
└── utils.mb
```
