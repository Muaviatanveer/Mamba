import sys
from compiler.builder import build_and_run, mamba_build, run_tests
from compiler.tooling import init_project, format_code
from compiler.dev_server import start_mamba_server

def main():
    try:
        if len(sys.argv) < 2:
            print("Usage:")
            print("  ./mamba <script.mb> [--target cpp|php] [--release]")
            print("  ./mamba build <script.mb> [--target cpp|php] [--release]")
            print("  ./mamba serve <script.mb>")
            print("  ./mamba init <project_name>")
            print("  ./mamba fmt <script.mb>")
            print("  ./mamba test <script.mb>")
        elif sys.argv[1] == "build":
            script = "examples/sqlite_app.mb"
            target = "cpp"
            release = "--release" in sys.argv or "-r" in sys.argv or True
            
            if "--target" in sys.argv:
                t_idx = sys.argv.index("--target") + 1
                if t_idx < len(sys.argv):
                    target = sys.argv[t_idx]
                    
            for arg in sys.argv[2:]:
                if not arg.startswith("-"):
                    script = arg
                    break
                    
            mamba_build(script, target, release)
        elif sys.argv[1] == "init":
            proj = sys.argv[2] if len(sys.argv) > 2 else "my_mamba_app"
            init_project(proj)
        elif sys.argv[1] == "fmt":
            script = sys.argv[2] if len(sys.argv) > 2 else "examples/phase_01.mb"
            format_code(script)
        elif sys.argv[1] == "test":
            script = sys.argv[2] if len(sys.argv) > 2 else "examples/test_suite.mb"
            run_tests(script)
        elif sys.argv[1] == "serve":
            script_file = sys.argv[2] if len(sys.argv) > 2 else "examples/web.mb"
            start_mamba_server(script_file)
        else:
            file = sys.argv[1]
            target = "cpp"
            release = "--release" in sys.argv or "-r" in sys.argv
            
            if "--target" in sys.argv:
                t_idx = sys.argv.index("--target") + 1
                if t_idx < len(sys.argv):
                    target = sys.argv[t_idx]
                    
            build_and_run(file, target, release)
    except KeyboardInterrupt:
        print("\n🛑 Execution stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()