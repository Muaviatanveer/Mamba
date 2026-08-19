# Getting Started

Mamba is a multi-target programming language designed to combine readable syntax with native compilation and built-in web development capabilities.

## 1. Introduction

### What is Mamba?

Mamba is a multi-target programming language designed to combine readable syntax with native compilation and built-in web development capabilities.

### Why Mamba?

```text
Python-like readability
        +
Native C++ performance
        +
Built-in Web primitives
        +
Built-in tooling
        ↓
      MAMBA
```

### Design Philosophy

* One source → multiple targets
* Simple syntax
* Native execution
* Web development as a first-class capability
* Minimal deployment footprint

### Architecture

```text
Mamba Source
     │
     ▼
  Compiler
   /    \
  ▼      ▼
C++20   PHP
  │
clang++
  │
  ▼
Native Binary
```

---

## 2. Installation

Requirements:
- macOS/Linux
- Python 3.9+
- clang++
- SQLite

### Step 1: Clone the Repository

```bash
git clone https://github.com/Muaviatanveer/Mamba.git
cd Mamba
```

### Step 2: Setup Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install lark
chmod +x mamba
```

### Step 3: Verify Installation

```bash
./mamba --help
```

---

## 3. Your First Mamba Program

Create a file named `hello.mb`:

```mamba
print("Hello, Mamba!")
```

Run it using the Mamba compiler:

```bash
./mamba hello.mb
```

Output:
```text
Hello, Mamba!
```
