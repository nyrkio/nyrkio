#!/usr/bin/env python3
"""Start and stop the Nyrkiö backend server"""

import argparse
import os
import subprocess
import sys
import signal
import time
from pathlib import Path


def load_env_vars():
    """Load environment variables from .env.backend"""
    env_file = Path(__file__).parent / ".env.backend"
    env_vars = os.environ.copy()

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
    return env_vars


def get_pid_file():
    """Get the path to the PID file"""
    return Path(__file__).parent / ".backend.pid"


def is_backend_running():
    """Check if backend is running"""
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


def check_uvicorn():
    """Check if uvicorn is available and return the command to use"""
    import shutil

    # First check if we're in a Poetry environment
    backend_dir = Path(__file__).parent / "backend"
    if (backend_dir / "pyproject.toml").exists() and shutil.which("poetry"):
        # Check if poetry environment has uvicorn installed
        try:
            result = subprocess.run(
                ["poetry", "run", "python", "-c", "import uvicorn"],
                cwd=backend_dir,
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return ["poetry", "run", "uvicorn"], backend_dir
        except:
            pass

    # Check if uvicorn is in system Python
    if shutil.which("uvicorn"):
        # Need to add parent directory to PYTHONPATH for imports to work
        return ["uvicorn"], Path(__file__).parent

    # Check if python -m uvicorn works
    try:
        result = subprocess.run(
            ["python3", "-m", "uvicorn", "--version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return ["python3", "-m", "uvicorn"], Path(__file__).parent
    except:
        pass

    return None, None


def start_backend():
    """Start the backend server"""
    running, pid = is_backend_running()

    if running:
        print(f"Backend is already running (PID: {pid})")
        return

    # Check for uvicorn
    uvicorn_cmd, working_dir = check_uvicorn()

    if not uvicorn_cmd:
        print("Error: uvicorn is not installed.")
        print()
        print("Please install dependencies using one of:")
        print("  1. poetry install (in backend directory)")
        print("  2. pip install uvicorn fastapi")
        print("  3. python3 install_backend.py --local-only")
        sys.exit(1)

    # Load environment variables
    env_vars = load_env_vars()
    api_port = env_vars.get('API_PORT', '8001')

    # Add parent directory to PYTHONPATH if using system uvicorn
    if uvicorn_cmd[0] != "poetry":
        parent_dir = str(Path(__file__).parent.absolute())
        env_vars['PYTHONPATH'] = parent_dir + os.pathsep + env_vars.get('PYTHONPATH', '')

    print(f"Starting Nyrkiö backend on port {api_port}...")
    print(f"Using: {' '.join(uvicorn_cmd)}")
    print(f"API will be available at: http://localhost:{api_port}")
    print(f"OpenAPI docs at: http://localhost:{api_port}/docs")
    print()

    # Build uvicorn command
    cmd = uvicorn_cmd + [
        "backend.api.api:app",
        "--host", "0.0.0.0",
        "--port", api_port,
        "--reload"
    ]

    # Start uvicorn in background
    process = subprocess.Popen(
        cmd,
        cwd=working_dir,
        env=env_vars,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setpgrp if sys.platform != 'win32' else None
    )

    # Save PID
    pid_file = get_pid_file()
    with open(pid_file, 'w') as f:
        f.write(str(process.pid))

    print(f"Backend started with PID: {process.pid}")
    print(f"To stop: python3 backend_init.py stop")
    print(f"To view logs: tail -f backend/uvicorn.log (if configured)")


def stop_backend():
    """Stop the backend server"""
    running, pid = is_backend_running()

    if not running:
        print("Backend is not running")
        return

    print(f"Stopping backend (PID: {pid})...")

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
        print("Backend stopped successfully")

    except Exception as e:
        print(f"Error stopping backend: {e}")
        # Clean up PID file anyway
        get_pid_file().unlink(missing_ok=True)


def status_backend():
    """Check backend status"""
    running, pid = is_backend_running()

    if running:
        env_vars = load_env_vars()
        api_port = env_vars.get('API_PORT', '8001')
        print(f"Backend is running (PID: {pid})")
        print(f"API available at: http://localhost:{api_port}")
        print(f"OpenAPI docs at: http://localhost:{api_port}/docs")
    else:
        print("Backend is not running")


def main():
    parser = argparse.ArgumentParser(
        description="Start and stop the Nyrkiö backend server",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'status'],
        help='Command to execute'
    )

    args = parser.parse_args()

    if args.command == 'start':
        start_backend()
    elif args.command == 'stop':
        stop_backend()
    elif args.command == 'restart':
        stop_backend()
        time.sleep(1)
        start_backend()
    elif args.command == 'status':
        status_backend()


if __name__ == "__main__":
    main()
