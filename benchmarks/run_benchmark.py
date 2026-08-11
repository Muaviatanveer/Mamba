import subprocess
import time
import re
import os

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

print("==========================================================")
print("  🏆 MAMBA MULTI-LANGUAGE BENCHMARK SUITE")
print("==========================================================")

# 1. Compile Mamba Release
print("🔨 Building Mamba Release Binary...")
subprocess.run("./mamba build benchmarks/mamba_bench.mb --release", shell=True)
os.rename("dist/mamba_app", "benchmarks/mamba_app")

# 2. Compile Raw C++ (-O3)
print("🔨 Building Raw C++ Binary (-O3)...")
subprocess.run("clang++ -O3 -std=c++17 benchmarks/cpp_bench.cpp -o benchmarks/cpp_app", shell=True)

# 3. Compile Rust (-O) if rustc exists
has_rust = subprocess.run("which rustc", shell=True).returncode == 0
if has_rust:
    print("🔨 Building Rust Binary (-O)...")
    subprocess.run("rustc -O benchmarks/rust_bench.rs -o benchmarks/rust_app", shell=True)

# Define Servers
servers = [
    ("Mamba (Native C++ -O3)", "PORT=3000 ./benchmarks/mamba_app", "http://localhost:3000/api/user"),
    ("Python (http.server)", "python3 benchmarks/python_bench.py", "http://localhost:3001/api/user"),
    ("Raw C++ (clang++ -O3)", "./benchmarks/cpp_app", "http://localhost:3002/api/user")
]

if has_rust:
    servers.append(("Rust (rustc -O)", "./benchmarks/rust_app", "http://localhost:3003/api/user"))

results = []

for name, start_cmd, url in servers:
    print(f"\n🚀 Launching {name}...")
    proc = subprocess.Popen(start_cmd, shell=True)
    time.sleep(1.5)  # Allow server to start
    
    print(f"⚡ Running Benchmark: ab -n 20000 -c 100 {url}")
    ab_res = subprocess.run(f"ab -n 20000 -c 100 {url}", shell=True, capture_output=True, text=True)
    
    # Terminate server
    proc.terminate()
    proc.wait()
    
    # Parse Requests Per Second
    match = re.search(r"Requests per second:\s+([\d.]+)", ab_res.stdout)
    req_per_sec = float(match.group(1)) if match else 0.0
    
    # Parse Latency
    lat_match = re.search(r"Time per request:\s+([\d.]+)\s+\[ms\]\s+\(mean, across", ab_res.stdout)
    latency_ms = float(lat_match.group(1)) if lat_match else 0.0
    
    results.append((name, req_per_sec, latency_ms))

# Sort Leaderboard by Requests Per Second
results.sort(key=lambda x: x[1], reverse=True)

print("\n==========================================================================")
print("  🏆 OFFICIAL BENCHMARK LEADERBOARD (20,000 Requests, Concurrency 100)")
print("==========================================================================")
print(f"{'Rank':<5} | {'Language / Server':<25} | {'Requests / Sec':<18} | {'Latency (mean)':<15}")
print("--------------------------------------------------------------------------")

for i, (name, rps, lat) in enumerate(results, 1):
    print(f"{i:<5} | {name:<25} | {rps:>12.2f} req/s  | {lat:>10.4f} ms")

print("==========================================================================")