
#!/usr/bin/env python3
"""
Cross-platform runner for SignalHire agent with WSL-first behavior.

Changes:
- Prefer WSL Python (`/usr/bin/python3`) when running under WSL or when
  `FORCE_WSL_PYTHON=1` (default).
- Skip auto-install of dependencies unless `RUNPY_AUTO_INSTALL=1` is set.
- When running pytest (`-m pytest` or `pytest`), skip heavy dependency checks.
"""

import os
import sys
import subprocess
from pathlib import Path

# Windows Python paths in WSL
WINDOWS_PYTHON = "/mnt/c/Python312/python.exe"
WINDOWS_PIP = "/mnt/c/Python312/Scripts/pip.exe"

# Env toggles
AUTO_INSTALL = os.getenv("RUNPY_AUTO_INSTALL", "0") == "1"
FORCE_WSL_PYTHON = os.getenv("FORCE_WSL_PYTHON", "1") == "1"


def is_wsl() -> bool:
    try:
        with open("/proc/sys/kernel/osrelease", "r", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False

def get_python_cmd() -> str:
    """Get the best available Python command.

    Preference:
    1) WSL Python if in WSL or FORCE_WSL_PYTHON
    2) Windows Python if available
    3) Fallback to `python3`
    """
    if (FORCE_WSL_PYTHON or is_wsl()) and os.path.exists("/usr/bin/python3"):
        return "/usr/bin/python3"
    if os.path.exists(WINDOWS_PYTHON):
        return WINDOWS_PYTHON
    return "python3"

def install_missing_packages(missing_packages):
    """Install missing packages using appropriate pip.

    Disabled by default. Enable with RUNPY_AUTO_INSTALL=1.
    """
    if not AUTO_INSTALL:
        print("Skipping auto-install (set RUNPY_AUTO_INSTALL=1 to enable).")
        return False

    if os.path.exists(WINDOWS_PIP):
        pip_cmd = WINDOWS_PIP
    else:
        pip_cmd = "pip3"

    print(f"Installing missing packages: {', '.join(missing_packages)}")
    try:
        # Try regular pip first
        result = subprocess.run([pip_cmd, "install"] + missing_packages, timeout=300, check=False)
        if result.returncode != 0:
            print("Regular pip failed, trying with sudo...")
            result = subprocess.run(["sudo", pip_cmd, "install"] + missing_packages, timeout=300, check=True)

        # Browser automation removed; skip Playwright install

        return True
    except subprocess.TimeoutExpired:
        print("❌ Package installation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Package installation failed: {e}")
        return False


def install_node_dependencies():
    """Install Node.js dependencies like Stagehand (optional)."""
    if not AUTO_INSTALL:
        print("Skipping Node.js dependency installation (RUNPY_AUTO_INSTALL=1 to enable).")
        return True
    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  npm not available - skipping Node.js dependencies")
        return True
    
    # Check if Stagehand is already installed
    try:
        result = subprocess.run(["npm", "list", "@browserbasehq/stagehand"], 
                               capture_output=True, timeout=10)
        if result.returncode == 0:
            print("✅ Stagehand already available")
            return True
    except Exception:
        pass
    
    # Install Stagehand
    print("Installing Stagehand browser automation...")
    try:
        result = subprocess.run(["npm", "install", "@browserbasehq/stagehand"], 
                               timeout=180, check=True)
        print("✅ Stagehand installed successfully")
        return True
    except subprocess.TimeoutExpired:
        print("❌ Stagehand installation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Stagehand installation failed: {e}")
        return False

def is_pytest_invocation(argv: list[str]) -> bool:
    if not argv:
        return False
    # Match forms: `-m pytest`, `pytest`, `py.test`
    if "-m" in argv:
        try:
            idx = argv.index("-m")
            if idx + 1 < len(argv) and argv[idx + 1] == "pytest":
                return True
        except ValueError:
            pass
    if any(arg.endswith("pytest") or arg.endswith("py.test") or arg == "pytest" for arg in argv):
        return True
    return False


def check_and_install_dependencies(argv: list[str]):
    """Check if required dependencies are available and install if missing.

    For pytest runs, skip heavy dependency checks to allow unit tests to run
    without full stack installed.
    """
    python_cmd = get_python_cmd()
    running_pytest = is_pytest_invocation(argv)

    if running_pytest:
        required_packages = []  # let pytest fail if actually missing
    else:
        required_packages = [
            "pandas",
            "httpx",
            "pydantic",
            "fastapi",
            "email-validator",
            "structlog",
            "click",
            "python-dotenv",
            "uvicorn",
            "pydantic-settings",
        ]
    missing_packages = []
    
    print(f"Using Python: {python_cmd}")
    
    for package in required_packages:
        try:
            # Special handling for packages with different import names
            if package == "email-validator":
                import_name = "email_validator"
            elif package == "python-dotenv":
                import_name = "dotenv"
            else:
                import_name = package
            
            result = subprocess.run([python_cmd, "-c", f"import {import_name}"], 
                                   capture_output=True, check=True, timeout=5)
            print(f"✅ {package} available")
        except subprocess.CalledProcessError:
            print(f"❌ {package} missing")
            missing_packages.append(package)
        except subprocess.TimeoutExpired:
            print(f"⏰ {package} check timed out, assuming missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        if not install_missing_packages(missing_packages):
            print("❌ Auto-install disabled or failed. Install manually: 'pip install -e .[dev]'")
            return False
    
    print("✅ All Python dependencies are available")
    
    # Install Node.js dependencies
    # Browser automation removed; skip Node.js dependencies
    
    print("✅ All dependencies are available")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <script.py> [args...]")
        sys.exit(1)
    
    if not check_and_install_dependencies(sys.argv[1:]):
        print("❌ Could not ensure all dependencies are available")
        sys.exit(1)
    
    # Run the specified script with Windows Python
    python_cmd = get_python_cmd()
    script_args = sys.argv[1:]
    
    try:
        print(f"Running: {python_cmd} {' '.join(script_args)}")
        result = subprocess.run([python_cmd] + script_args, timeout=300)  # 5 minute timeout
        sys.exit(result.returncode)
    except subprocess.TimeoutExpired:
        print("❌ Script execution timed out after 5 minutes")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Script execution interrupted by user")
        sys.exit(1)
