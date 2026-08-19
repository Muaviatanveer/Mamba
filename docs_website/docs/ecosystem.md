# Ecosystem & Community

Mamba is more than a compiler; it is an ecosystem.

## VS Code & Cursor Extension

To write Mamba code efficiently, we provide a specialized language extension for Visual Studio Code and Cursor.

### Features
- Native `.mb` file syntax highlighting.
- Code snippets and auto-completion.
- Integrated CLI commands.
- Official Black Mamba logo branding.

### Installation
Download the `mamba-extension-v0.2.0.zip` asset from the Mamba GitHub releases page and install it directly via the IDE Extensions panel.

## Benchmarks

Mamba consistently outperforms dynamic scripting runtimes in heavily threaded environments due to its native compilation architecture.

**Mean Throughput (macOS 15.5, Apple Clang 17)**
*(1,000 Concurrent Sockets | 50,000 Requests)*

| Server / Language | Requests / Sec | Failures |
| :--- | :---: | :---: |
| **Raw C++ (-O3)** | ~26,051 req/s | 0 |
| **🐍 Mamba Native (-O3)** | **~19,865 req/s** | **0** |
| **Rust (rustc -O)** | ~22,993 req/s | 0 |
| **PHP (cli-server)** | ~15,806 req/s | 0 |
| **Python (http.server)**| ~15,358 req/s | 0 |

## Roadmap

**Mamba 0.1**
- [x] Multi-target compiler
- [x] Native web server
- [x] PHP target
- [x] Tooling

**Mamba 0.2**
- [x] Prepared SQL
- [x] Collections (Arrays, HashMaps)
- [x] Thread pool scaling
- [x] CORS Handling

**Mamba 0.3**
- [x] Git integration (push-to-deploy)
- [x] Mamba Cloud PaaS
- [x] Reverse Proxy Gateway
- [x] Global Edge Bridges

**Mamba 0.4+**
- [ ] Package manager
- [ ] Official LSP Server
- [ ] Debugger
- [ ] More execution targets

## Contributing

1. **Fork** the repository.
2. **Branch** off `main` for your feature.
3. **Implement** your changes.
4. **Test** using `./mamba test`.
5. **Submit a PR**.
