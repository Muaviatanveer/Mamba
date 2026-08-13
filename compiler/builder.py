import os
import shutil
import subprocess
import json
from lark import Lark
from compiler.preprocessor import resolve_imports
from compiler.targets.cpp import CppGenerator
from compiler.targets.php import PhpGenerator

COMPILER_DIR = os.path.dirname(os.path.abspath(__file__))
GRAMMAR_PATH = os.path.join(COMPILER_DIR, 'grammar.lark')

def mamba_build(filename, target="cpp", release=True):
    print("🔨 Building Mamba Application...")
    with open(GRAMMAR_PATH, 'r') as g_file: grammar = g_file.read()
    parser = Lark(grammar, parser='lalr')
    code = resolve_imports(filename)
    tree = parser.parse(code)
    
    os.makedirs('dist', exist_ok=True)

    if target == "cpp":
        generator = CppGenerator()
        cpp_code = generator.transform(tree)
        cpp_file = "dist/output_temp.cpp"
        binary_file = "dist/mamba_app"
        with open(cpp_file, "w") as f: f.write(cpp_code)
        
        opt_flag = "-O3" if release else "-O0"
        mode_str = "Release (-O3)" if release else "Debug (-O0)"
        
        print(f"⚡ Target: Native C++ ({mode_str})")
        
        compile_cmd = f"clang++ {opt_flag} -std=c++17 {cpp_file} -lsqlite3 -o {binary_file}"
        res = subprocess.run(compile_cmd, shell=True)
        
        if os.path.exists(cpp_file):
            os.remove(cpp_file)
            
        if res.returncode == 0:
            mamba_manifest = {
                "name": "Mamba App",
                "version": "0.2.0",
                "target": "cpp",
                "binary": "mamba_app"
            }
            with open("dist/mamba.json", "w") as f:
                json.dump(mamba_manifest, f, indent=2)
                
            file_size_kb = os.path.getsize(binary_file) / 1024
            print(f"📦 Output Directory: dist/")
            print(f"   └── dist/mamba_app ({file_size_kb:.1f} KB)")
            print(f"   └── dist/mamba.json")
            print(f"✨ Build Complete! Run with: ./dist/mamba_app")
        else:
            print("❌ C++ Compilation Failed!")

    elif target == "php":
        php_code = PhpGenerator().transform(tree)
        php_file = "dist/app.php"
        with open(php_file, "w") as f: f.write(php_code)
        
        mamba_manifest = {
            "name": "Mamba App",
            "version": "0.2.0",
            "target": "php",
            "main": "app.php"
        }
        with open("dist/mamba.json", "w") as f:
            json.dump(mamba_manifest, f, indent=2)

        print(f"🌐 Target: PHP Web Application")
        print(f"📦 Output Directory: dist/")
        print(f"   └── dist/app.php")
        print(f"   └── dist/mamba.json")
        print(f"✨ Build Complete!")

def build_and_run(filename, target="cpp", release=False):
    mamba_build(filename, target, release)
    print("🚀 Running Application:\n---------------------------------")
    if target == "cpp":
        subprocess.run("./dist/mamba_app", shell=True)
    elif target == "php" and shutil.which("php"):
        subprocess.run("php dist/app.php", shell=True)

def run_tests(filename):
    print(f"🧪 Running Mamba Test Suite: '{filename}'...\n")
    build_and_run(filename, target="cpp")