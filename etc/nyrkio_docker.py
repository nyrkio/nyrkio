#!/usr/bin/env python3
"""Start and stop the Nyrkiö Docker stack with Docker Compose"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_docker():
    """Check if Docker is available"""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        subprocess.run(["docker", "compose", "version"], capture_output=True, check=True)
        return True
    except:
        return False


def is_stack_running():
    """Check if the Docker stack is running"""
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.dev.yml", "ps", "--quiet"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        return bool(result.stdout.strip())
    except:
        return False


def start_stack():
    """Start the full Docker stack"""
    root_dir = Path(__file__).parent

    # Check if .env.backend exists
    env_file = root_dir / ".env.backend"
    if not env_file.exists():
        print("Error: .env.backend not found. Run install_backend.py first.")
        sys.exit(1)

    # Check Docker
    if not check_docker():
        print("Error: Docker or Docker Compose is not available.")
        print("Please install Docker and try again.")
        sys.exit(1)

    # Check if already running
    if is_stack_running():
        print("Docker stack is already running")
        return

    # Set IMAGE_TAG
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=root_dir
        )
        image_tag = result.stdout.strip()
    except:
        image_tag = "dev"

    os.environ["IMAGE_TAG"] = image_tag

    print("Starting Nyrkiö full stack...")
    print("Backend API will be available at: http://localhost:8000")
    print("Webhooks service will be available at: http://localhost:8080")
    print("Nginx proxy will be available at: http://localhost:80")
    print()

    # Start docker compose
    subprocess.run([
        "docker", "compose",
        "-f", "docker-compose.dev.yml",
        "up", "--build"
    ], cwd=root_dir)


def stop_stack():
    """Stop the Docker stack"""
    root_dir = Path(__file__).parent

    # Check Docker
    if not check_docker():
        print("Error: Docker or Docker Compose is not available.")
        sys.exit(1)

    # Check if running
    if not is_stack_running():
        print("Docker stack is not running")
        return

    print("Stopping Nyrkiö Docker stack...")
    subprocess.run([
        "docker", "compose",
        "-f", "docker-compose.dev.yml",
        "down"
    ], cwd=root_dir)
    print("Docker stack stopped successfully")


def status_stack():
    """Check Docker stack status"""
    if not check_docker():
        print("Error: Docker or Docker Compose is not available.")
        sys.exit(1)

    if is_stack_running():
        print("Docker stack is running")
        print()
        print("Services:")
        print("  Backend API: http://localhost:8000")
        print("  Webhooks: http://localhost:8080")
        print("  Nginx proxy: http://localhost:80")
        print("  MongoDB: localhost:27017")
        print()

        # Show running containers
        subprocess.run([
            "docker", "compose",
            "-f", "docker-compose.dev.yml",
            "ps"
        ], cwd=Path(__file__).parent)
    else:
        print("Docker stack is not running")


def main():
    parser = argparse.ArgumentParser(
        description="Start and stop the Nyrkiö Docker stack with Docker Compose",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'status'],
        help='Command to execute'
    )

    args = parser.parse_args()

    if args.command == 'start':
        start_stack()
    elif args.command == 'stop':
        stop_stack()
    elif args.command == 'restart':
        stop_stack()
        print()
        start_stack()
    elif args.command == 'status':
        status_stack()


if __name__ == "__main__":
    main()
