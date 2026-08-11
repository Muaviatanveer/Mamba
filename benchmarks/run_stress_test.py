import subprocess
import time
import re
import os
import shutil

print("==========================================================")
print("  🔥 MAMBA 5-WAY EXTREME STRESS BENCHMARK SUITE")
print("==========================================================")
print("  Testing: Mamba, C++, Rust, PHP, & Python")
print("  Load: 50,000 Requests @ 200, 500 & 1,000 Concurrency")
print("==========================================================")

# Raise file descriptor limits
subprocess.run("ulimit -n 4096", shell=True)

# 1. Compile Mamba Release
print("🔨 Building Mamba Release Binary (-O3)...")
subprocess.run("./mamba build benchmarks/mamba_bench.mb --release", shell=True)
if os.path.exists("dist/mamba_app"):
    if os.path.exists("benchmarks/mamba_app"):
        os.remove("benchmarks/mamba_app")
    os.rename("dist/mamba_app", "benchmarks/mamba_app")

# 2. Compile Raw C++ (-O3)
print("🔨 Building Raw C++ Binary (-O3)...")
subprocess.run("clang++ -O3 -std=c++17 benchmarks/cpp_bench.cpp -o benchmarks/cpp_app", shell=True)

# 3. Check Rust
has_rust = shutil.which("rustc") is not None
if has_rust:
    print("🔨 Building Rust Binary (-O)...")
    subprocess.run("rustc -O benchmarks/rust_bench.rs -o benchmarks/rust_app", shell=True)
else:
    print("💡 Rust ('rustc') not found on PATH. (Install via 'brew install rust' to include)")

# 4. Check PHP
has_php = shutil.which("php") is not None
if has_php:
    print("🌐 PHP CLI found. Including PHP in stress test...")
else:
    print("💡 PHP ('php') not found on PATH. (Install via 'brew install php' to include)")

servers = [
    ("Mamba Native (-O3)", "PORT=3000 ./benchmarks/mamba_app", "http://localhost:3000/api/user"),
    ("Raw C++ (-O3)", "./benchmarks/cpp_app", "http://localhost:3002/api/user"),
    ("Python (http.server)", "python3 benchmarks/python_bench.py", "http://localhost:3001/api/user")
]

if has_rust:
    servers.append(("Rust (rustc -O)", "./benchmarks/rust_app", "http://localhost:3003/api/user"))

if has_php:
    servers.append(("PHP (cli-server)", "php -S 0.0.0.0:3004 benchmarks/php_bench.php", "http://localhost:3004/api/user"))

concurrency_levels = [200, 500, 1000]
total_requests = 50000

results = {}

for name, start_cmd, url in servers:
    print(f"\n🚀 Launching {name} for Stress Test...")
    proc = subprocess.Popen(start_cmd, shell=True)
    time.sleep(1.5)
    
    results[name] = {}
    
    for c in concurrency_levels:
        print(f"🔥 Firing Load: {total_requests:,} requests @ {c} concurrency...")
        ab_res = subprocess.run(f"ab -n {total_requests} -c {c} {url}", shell=True, capture_output=True, text=True)
        
        # Parse RPS
        rps_match = re.search(r"Requests per second:\s+([\d.]+)", ab_res.stdout)
        rps = float(rps_match.group(1)) if rps_match else 0.0
        
        # Parse Failed Requests
        failed_match = re.search(r"Failed requests:\s+(\d+)", ab_res.stdout)
        failed = int(failed_match.group(1)) if failed_match else 0
        
        # Parse Max Latency
        max_lat_match = re.search(r"100%\s+(\d+)\s+\(longest request\)", ab_res.stdout)
        max_lat = int(max_lat_match.group(1)) if max_lat_match else 0
        
        results[name][c] = (rps, failed, max_lat)
        time.sleep(0.5)
        
    proc.terminate()
    proc.wait()

# Print Stress Test Report
print("\n==========================================================================================")
print("  🔥 5-WAY EXTREME STRESS BENCHMARK REPORT (50,000 Requests Per Tier)")
print("==========================================================================================")
print(f"{'Server':<22} | {'Concurrency':<12} | {'Throughput (req/s)':<20} | {'Status':<16} | {'Max Latency'}")
print("------------------------------------------------------------------------------------------")

for name in results:
    for c in concurrency_levels:
        rps, failed, max_lat = results[name][c]
        status_str = "0 (100% Solid)" if failed == 0 else f"⚠️ {failed} Failed"
        print(f"{name:<22} | {c:<12} | {rps:>14.2f} req/s   | {status_str:<16} | {max_lat} ms")
    print("------------------------------------------------------------------------------------------")