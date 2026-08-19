import sys
from compiler.builder import build_and_run, mamba_build, run_tests
from compiler.tooling import init_project, format_code
from compiler.dev_server import start_mamba_server
from compiler.cloud import deploy_app, check_status, show_logs, stop_deployment, init_git_repo, start_reverse_proxy

def main():
    try:
        if len(sys.argv) < 2:
            print("Usage:")
            print("  ./mamba <script.mb> [--target cpp|php] [--release]")
            print("  ./mamba build <script.mb> [--target cpp|php] [--release]")
            print("  ./mamba deploy [port] [--live]")
            print("  ./mamba proxy [port]")
            print("  ./mamba git-init <repo_name>")
            print("  ./mamba status")
            print("  ./mamba logs")
            print("  ./mamba stop")
        elif sys.argv[1] == "deploy":
            port = 8080
            live = "--live" in sys.argv or "--public" in sys.argv
            for arg in sys.argv[2:]:
                if arg.isdigit():
                    port = int(arg)
            deploy_app(port=port, live=live)
        elif sys.argv[1] == "proxy":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 9000
            start_reverse_proxy(proxy_port=port)
        elif sys.argv[1] == "git-init":
            repo_name = sys.argv[2] if len(sys.argv) > 2 else "my_app"
            init_git_repo(repo_name)
        elif sys.argv[1] == "status":
            check_status()
        elif sys.argv[1] == "logs":
            show_logs()
        elif sys.argv[1] == "stop":
            stop_deployment()
        elif sys.argv[1] == "build":
            script = "examples/master_app.mb"
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