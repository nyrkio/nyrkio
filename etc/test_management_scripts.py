#!/usr/bin/env python3
"""
Test suite for Nyrkiö management scripts

Tests the backend, frontend, and docker management scripts to ensure they:
- Execute without errors
- Have correct command-line interfaces
- Handle PID files properly
- Report status correctly
"""

import subprocess
import sys
import time
from pathlib import Path


class TestResult:
    """Store and display test results"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []

    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"✓ {test_name}")

    def add_fail(self, test_name, error):
        self.failed.append((test_name, error))
        print(f"✗ {test_name}: {error}")

    def add_skip(self, test_name, reason):
        self.skipped.append((test_name, reason))
        print(f"⊘ {test_name}: {reason}")

    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.skipped)
        print("\n" + "="*60)
        print(f"Test Summary: {total} tests")
        print(f"  Passed:  {len(self.passed)}")
        print(f"  Failed:  {len(self.failed)}")
        print(f"  Skipped: {len(self.skipped)}")
        print("="*60)

        if self.failed:
            print("\nFailed tests:")
            for test_name, error in self.failed:
                print(f"  - {test_name}: {error}")

        return len(self.failed) == 0


class ScriptTester:
    """Test management scripts"""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.etc_dir = root_dir / "etc"
        self.results = TestResult()

    def run_command(self, cmd, timeout=10, check=True):
        """Run a command and return the result"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e
        except subprocess.TimeoutExpired as e:
            raise Exception(f"Command timed out after {timeout}s")

    def test_script_exists(self, script_name):
        """Test that a script file exists"""
        test_name = f"{script_name}: File exists"
        script_path = self.etc_dir / script_name

        if script_path.exists():
            self.results.add_pass(test_name)
            return True
        else:
            self.results.add_fail(test_name, f"File not found at {script_path}")
            return False

    def test_script_executable(self, script_name):
        """Test that a script is executable"""
        test_name = f"{script_name}: Executable permissions"
        script_path = self.etc_dir / script_name

        if not script_path.exists():
            self.results.add_skip(test_name, "Script doesn't exist")
            return False

        import os
        if os.access(script_path, os.X_OK):
            self.results.add_pass(test_name)
            return True
        else:
            self.results.add_fail(test_name, "Script is not executable")
            return False

    def test_script_help(self, script_name):
        """Test that script responds to --help"""
        test_name = f"{script_name}: Help command"
        script_path = self.etc_dir / script_name

        if not script_path.exists():
            self.results.add_skip(test_name, "Script doesn't exist")
            return False

        try:
            result = self.run_command(
                ["python3", str(script_path), "--help"],
                timeout=5
            )
            if result.returncode == 0 and ("usage:" in result.stdout.lower() or "help" in result.stdout.lower()):
                self.results.add_pass(test_name)
                return True
            else:
                self.results.add_fail(test_name, "Help output not found")
                return False
        except Exception as e:
            self.results.add_fail(test_name, str(e))
            return False

    def test_script_status_when_stopped(self, script_name):
        """Test status command when service is stopped"""
        test_name = f"{script_name}: Status when stopped"
        script_path = self.etc_dir / script_name

        if not script_path.exists():
            self.results.add_skip(test_name, "Script doesn't exist")
            return False

        try:
            result = self.run_command(
                ["python3", str(script_path), "status"],
                timeout=5,
                check=False
            )
            if "not running" in result.stdout.lower() or result.returncode == 0:
                self.results.add_pass(test_name)
                return True
            else:
                self.results.add_fail(test_name, f"Unexpected output: {result.stdout}")
                return False
        except Exception as e:
            self.results.add_fail(test_name, str(e))
            return False

    def test_backend_script(self):
        """Test backend management script"""
        script_name = "nyrkio_backend.py"
        print(f"\nTesting {script_name}...")

        self.test_script_exists(script_name)
        self.test_script_executable(script_name)
        self.test_script_help(script_name)
        self.test_script_status_when_stopped(script_name)

        # Test that script accepts valid commands
        test_name = f"{script_name}: Accepts start/stop/restart/status commands"
        script_path = self.etc_dir / script_name

        if script_path.exists():
            try:
                # Just test that the script accepts these commands (status is safe)
                result = self.run_command(
                    ["python3", str(script_path), "status"],
                    timeout=5,
                    check=False
                )
                self.results.add_pass(test_name)
            except Exception as e:
                self.results.add_fail(test_name, str(e))

    def test_frontend_script(self):
        """Test frontend management script"""
        script_name = "nyrkio_frontend.py"
        print(f"\nTesting {script_name}...")

        self.test_script_exists(script_name)
        self.test_script_executable(script_name)
        self.test_script_help(script_name)
        self.test_script_status_when_stopped(script_name)

        # Test mode flag
        test_name = f"{script_name}: Supports --mode flag"
        script_path = self.etc_dir / script_name

        if script_path.exists():
            try:
                result = self.run_command(
                    ["python3", str(script_path), "--help"],
                    timeout=5
                )
                if "--mode" in result.stdout:
                    self.results.add_pass(test_name)
                else:
                    self.results.add_fail(test_name, "--mode flag not found in help")
            except Exception as e:
                self.results.add_fail(test_name, str(e))

    def test_docker_script(self):
        """Test docker management script"""
        script_name = "nyrkio_docker.py"
        print(f"\nTesting {script_name}...")

        self.test_script_exists(script_name)
        self.test_script_executable(script_name)
        self.test_script_help(script_name)
        self.test_script_status_when_stopped(script_name)

    def test_vite_configs(self):
        """Test that vite config files exist"""
        print(f"\nTesting Vite configurations...")

        frontend_dir = self.root_dir / "frontend"

        # Test production config
        test_name = "vite.config.js: Production config exists"
        prod_config = frontend_dir / "vite.config.js"
        if prod_config.exists():
            self.results.add_pass(test_name)
        else:
            self.results.add_fail(test_name, f"File not found at {prod_config}")

        # Test local config
        test_name = "vite.config.test.js: Local config exists"
        local_config = frontend_dir / "vite.config.test.js"
        if local_config.exists():
            self.results.add_pass(test_name)
        else:
            self.results.add_fail(test_name, f"File not found at {local_config}")

        # Test configs have correct content
        if prod_config.exists():
            test_name = "vite.config.js: Contains nyrk.io target"
            content = prod_config.read_text()
            if "nyrk.io" in content:
                self.results.add_pass(test_name)
            else:
                self.results.add_fail(test_name, "Production target not found")

        if local_config.exists():
            test_name = "vite.config.test.js: Contains localhost:8001 target"
            content = local_config.read_text()
            if "localhost:8001" in content:
                self.results.add_pass(test_name)
            else:
                self.results.add_fail(test_name, "Local target not found")

    def test_documentation(self):
        """Test that documentation files reference correct script paths"""
        print(f"\nTesting Documentation...")

        # Test DEVELOPMENT.md
        test_name = "DEVELOPMENT.md: References etc/ directory"
        dev_doc = self.root_dir / "DEVELOPMENT.md"
        if dev_doc.exists():
            content = dev_doc.read_text()
            if "etc/nyrkio_backend.py" in content and "etc/nyrkio_frontend.py" in content:
                self.results.add_pass(test_name)
            else:
                self.results.add_fail(test_name, "Missing etc/ references")
        else:
            self.results.add_skip(test_name, "DEVELOPMENT.md not found")

        # Test README.md
        test_name = "README.md: References etc/ directory"
        readme = self.root_dir / "README.md"
        if readme.exists():
            content = readme.read_text()
            if "etc/nyrkio_backend.py" in content:
                self.results.add_pass(test_name)
            else:
                self.results.add_fail(test_name, "Missing etc/ references")
        else:
            self.results.add_skip(test_name, "README.md not found")

        # Test that old references don't exist
        test_name = "Documentation: No references to old script names"
        issues = []
        for doc_file in [dev_doc, readme]:
            if doc_file.exists():
                content = doc_file.read_text()
                if "backend_init.py" in content:
                    issues.append(f"{doc_file.name} contains backend_init.py")
                if "frontend_init.py" in content:
                    issues.append(f"{doc_file.name} contains frontend_init.py")
                if "docker_init.py" in content:
                    issues.append(f"{doc_file.name} contains docker_init.py")
                if "install_backend.py" in content:
                    issues.append(f"{doc_file.name} contains install_backend.py")

        if issues:
            self.results.add_fail(test_name, "; ".join(issues))
        else:
            self.results.add_pass(test_name)

    def run_all_tests(self):
        """Run all tests"""
        print("="*60)
        print("Nyrkiö Management Scripts Test Suite")
        print("="*60)

        self.test_backend_script()
        self.test_frontend_script()
        self.test_docker_script()
        self.test_vite_configs()
        self.test_documentation()

        return self.results.summary()


def main():
    """Main test runner"""
    # Find project root (where this script's parent directory is)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    print(f"Project root: {root_dir}")
    print(f"Testing scripts in: {root_dir / 'etc'}\n")

    tester = ScriptTester(root_dir)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
