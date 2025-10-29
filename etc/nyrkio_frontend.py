#!/usr/bin/env python3
"""Start and stop the Nyrkiö frontend server"""

import argparse
import os
import subprocess
import sys
import signal
import time
import shutil
from pathlib import Path


def get_pid_file():
    """Get the path to the PID file"""
    return Path(__file__).parent / ".frontend.pid"


def is_frontend_running():
    """Check if frontend is running"""
    pid_file = get_pid_file()
    if not pid_file.exists():
        return False, None

    try:
        with open(pid_file) as f:
            pid = int(f.read().strip())

        # Check if process is actually running
        os.kill(pid, 0)
        return True, pid
    except (ValueError, ProcessLookupError, OSError):
        # PID file exists but process is not running
        pid_file.unlink(missing_ok=True)
        return False, None


def check_npm():
    """Check if npm is available"""
    return shutil.which("npm") is not None


def check_node_modules():
    """Check if node_modules exists"""
    frontend_dir = Path(__file__).parent / "frontend"
    node_modules = frontend_dir / "node_modules"
    return node_modules.exists()


def install_dependencies():
    """Install npm dependencies"""
    frontend_dir = Path(__file__).parent / "frontend"

    print("Installing frontend dependencies...")
    print("This may take a few minutes...")
    print()

    try:
        subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            check=True
        )
        print()
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def start_frontend(mode="local", port=5173):
    """Start the frontend server

    Args:
        mode: 'local' for local backend (uses vite.config.test.js) or
              'production' for production backend (uses vite.config.js)
        port: Port to run the frontend server on (default: 5173)
    """
    running, pid = is_frontend_running()

    if running:
        print(f"Frontend is already running (PID: {pid})")
        return

    # Check for npm
    if not check_npm():
        print("Error: npm is not installed.")
        print()
        print("Please install Node.js and npm:")
        print("  https://nodejs.org/")
        sys.exit(1)

    frontend_dir = Path(__file__).parent / "frontend"

    # Check for node_modules
    if not check_node_modules():
        print("Node modules not found. Installing dependencies...")
        if not install_dependencies():
            sys.exit(1)

    # Determine which config file to use
    if mode == "local":
        config_file = "vite.config.test.js"
        backend_info = "local backend (http://localhost:8001)"
    else:
        config_file = "vite.config.js"
        backend_info = "production backend (https://nyrk.io)"

    print(f"Starting Nyrkiö frontend in {mode} mode...")
    print(f"Using config: {config_file}")
    print(f"API proxy: {backend_info}")
    print(f"Frontend will be available at: http://localhost:{port}")
    print()

    # Build npm command
    env = os.environ.copy()
    env['VITE_CONFIG'] = config_file

    cmd = [
        "npm", "run", "dev",
        "--",
        "--config", config_file,
        "--port", str(port),
        "--host", "0.0.0.0"
    ]

    # Start npm in background
    process = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setpgrp if sys.platform != 'win32' else None
    )

    # Save PID
    pid_file = get_pid_file()
    with open(pid_file, 'w') as f:
        f.write(str(process.pid))

    print(f"Frontend started with PID: {process.pid}")
    print(f"To stop: python3 frontend_init.py stop")
    print()
    print("Note: The frontend may take a few seconds to start.")
    print("      Check http://localhost:{} in your browser".format(port))


def stop_frontend():
    """Stop the frontend server"""
    running, pid = is_frontend_running()

    if not running:
        print("Frontend is not running")
        return

    print(f"Stopping frontend (PID: {pid})...")

    try:
        # Send SIGTERM to process group
        if sys.platform != 'win32':
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        else:
            os.kill(pid, signal.SIGTERM)

        # Wait for process to terminate
        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except ProcessLookupError:
                break

        # Force kill if still running
        try:
            os.kill(pid, 0)
            print("Process didn't terminate, forcing shutdown...")
            if sys.platform != 'win32':
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            else:
                os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

        # Remove PID file
        get_pid_file().unlink(missing_ok=True)
        print("Frontend stopped successfully")

    except Exception as e:
        print(f"Error stopping frontend: {e}")
        # Clean up PID file anyway
        get_pid_file().unlink(missing_ok=True)


def status_frontend():
    """Check frontend status"""
    running, pid = is_frontend_running()

    if running:
        print(f"Frontend is running (PID: {pid})")
        print(f"Frontend available at: http://localhost:5173")
    else:
        print("Frontend is not running")


def main():
    parser = argparse.ArgumentParser(
        description="Start and stop the Nyrkiö frontend server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Deployment Modes:
  local       - Use local backend at http://localhost:8001 (default)
                Uses vite.config.test.js
  production  - Use production backend at https://nyrk.io
                Uses vite.config.js

Examples:
  # Start with local backend (default)
  python3 frontend_init.py start

  # Start with production backend
  python3 frontend_init.py start --mode production

  # Start on custom port
  python3 frontend_init.py start --port 3000

  # Stop frontend
  python3 frontend_init.py stop

  # Check status
  python3 frontend_init.py status
        """
    )

    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'status', 'install'],
        help='Command to execute'
    )

    parser.add_argument(
        '--mode',
        choices=['local', 'production'],
        default='local',
        help='Deployment mode (default: local)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5173,
        help='Port to run frontend on (default: 5173)'
    )

    args = parser.parse_args()

    if args.command == 'start':
        start_frontend(mode=args.mode, port=args.port)
    elif args.command == 'stop':
        stop_frontend()
    elif args.command == 'restart':
        stop_frontend()
        time.sleep(1)
        start_frontend(mode=args.mode, port=args.port)
    elif args.command == 'status':
        status_frontend()
    elif args.command == 'install':
        if not check_npm():
            print("Error: npm is not installed.")
            sys.exit(1)
        install_dependencies()


if __name__ == "__main__":
    main()
