# Tooling & CLI

Mamba provides a comprehensive CLI for project management, compilation, formatting, and testing.

## Project Scaffolding

Generate a new Mamba project with the standard directory structure.

```bash
./mamba init my-app
```

**Generated Structure:**
```text
my-app/
├── mamba.json
├── main.mb
├── helpers.mb
└── .gitignore
```

## Compilation

Mamba code is transpiled and compiled using the primary CLI executable.

### Development Run
Runs the application immediately without generating a standalone release binary.
```bash
./mamba app.mb
```

### Target: C++
Transpiles the Mamba source into standard C++20.
```bash
./mamba app.mb --target cpp
```

### Target: PHP
Transpiles the Mamba source into PHP scripts.
```bash
./mamba app.mb --target php
```

### Release Build
Compiles the application into a highly optimized (`-O3`) native C++ executable located in `dist/`.
```bash
./mamba build app.mb --release
```

## Code Formatting

Mamba includes a built-in code formatter to ensure style consistency.
```bash
./mamba fmt main.mb
```

## Testing

Define test assertions using the `test` block syntax natively within your `.mb` files.

```mamba
test "Addition Test" {
    assert(add(2, 3) == 5)
}
```

Run tests using the CLI:
```bash
./mamba test
```
