# 🔬 Mamba 0.3.0 Reproducible Benchmark Report

This report documents reproducible performance benchmarks for Mamba 0.3.0
averaged across multiple test runs.

📋 System Environment Specs

  - macOS Version: 15.5
  - Hardware Model: MacBookPro18,2 (Apple Silicon M1/M2 Max)
  - C++ Compiler: Apple clang version 17.0.0
  - Rust Compiler: rustc 1.97.1
  - Python Engine: 3.9.6
  - PHP Engine: PHP 8.5.9 (cli)
  - Benchmark Tool: ApacheBench 2.3

📊 1. Mean Throughput (3 Runs per Tier @ 50,000 Requests)

Each server utilized a native thread pool to process massive concurrent loads
accessing a JSON endpoint.

| Server / Language        | 200 Concurrency     | 500 Concurrency     | 1,000 Concurrency   | Total Failures     |
| :----------------------- | :-----------------: | :-----------------: | :-----------------: | :----------------: |
| **Raw C++ (-O3)**        | 32,639.18 req/s     | 30,679.72 req/s     | 26,051.49 req/s     | 0 (100% Solid)     |
| 🐍 **Mamba Native (-O3)** | **24,847.13 req/s** | **22,967.68 req/s** | **19,865.67 req/s** | **0 (100% Solid)** |
| **Rust (rustc -O)**      | 27,799.48 req/s     | 23,889.48 req/s     | 22,993.26 req/s     | 0 (100% Solid)     |
| **PHP (cli-server)**     | 16,526.86 req/s     | 16,689.46 req/s     | 15,806.76 req/s     | 0 (100% Solid)     |
| **Python (http.server)** | 15,208.81 req/s     | 15,465.24 req/s     | 15,358.34 req/s     | 0 (100% Solid)     |

🔥 2. 5-Way Extreme Stress Benchmark (150,000 Requests per Server)

| Server                   | Concurrency | Throughput (req/s) | Status         | Max Latency |
| :----------------------- | :---------: | :----------------: | :------------: | :---------: |
| **Mamba Native (-O3)**   | 200         | 25,907.46 req/s    | 0 (100% Solid) | 159 ms      |
| **Mamba Native (-O3)**   | 500         | 23,480.93 req/s    | 0 (100% Solid) | 2072 ms     |
| **Mamba Native (-O3)**   | 1000        | 19,811.15 req/s    | 0 (100% Solid) | 2024 ms     |
| **Raw C++ (-O3)**        | 200         | 38,054.88 req/s    | 0 (100% Solid) | 1058 ms     |
| **Raw C++ (-O3)**        | 500         | 32,973.87 req/s    | 0 (100% Solid) | 1112 ms     |
| **Raw C++ (-O3)**        | 1000        | 28,552.03 req/s    | 0 (100% Solid) | 1088 ms     |
| **Rust (rustc -O)**      | 200         | 31,736.54 req/s    | 0 (100% Solid) | 85 ms       |
| **Rust (rustc -O)**      | 500         | 26,524.75 req/s    | 0 (100% Solid) | 1065 ms     |
| **Rust (rustc -O)**      | 1000        | 21,868.88 req/s    | 0 (100% Solid) | 2025 ms     |
| **Python (http.server)** | 200         | 15,049.04 req/s    | 0 (100% Solid) | 2017 ms     |
| **Python (http.server)** | 500         | 14,949.55 req/s    | 0 (100% Solid) | 2062 ms     |
| **Python (http.server)** | 1000        | 15,007.83 req/s    | 0 (100% Solid) | 2023 ms     |
| **PHP (cli-server)**     | 200         | 15,919.52 req/s    | 0 (100% Solid) | 2051 ms     |
| **PHP (cli-server)**     | 500         | 15,950.67 req/s    | 0 (100% Solid) | 2132 ms     |
| **PHP (cli-server)**     | 1000        | 15,982.06 req/s    | 0 (100% Solid) | 2028 ms     |

💡 Verified Claims for Mamba 0.3.0

1.  0 Failures Across Stress Load: Mamba maintained zero failed requests
    under 1,000 concurrent socket connections across a total payload of 450,000
    test requests.
2.  24% - 32% Faster Than Scripting Runtimes: At 1,000 concurrency, Mamba
    outperformed Python by 31.9% and PHP by 24.0%.
3.  Multi-Threaded Worker Pool Engine: Mamba's POSIX C++ engine utilizes a
    std::thread pool matching hardware thread concurrency, allowing simultaneous
    processing of JSON serialization and SQLite std::mutex operations.
4.  Zero-Dependency Release Executable: Compiled C++ binary is ~80 KB - 100 KB
    with embedded POSIX HTTP server and SQLite prepared statement driver. 