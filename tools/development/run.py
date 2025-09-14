
#!/usr/bin/env python3
"""
Cross-platform runner for SignalHire agent in WSL environment.
Automatically detects and uses Windows Python if available.
"""

import os
import sys
import subprocess
from pathlib import Path

# Windows Python paths in WSL
WINDOWS_PYTHON = "/mnt/c/Python312/python.exe"
WINDOWS_PIP = "/mnt/c/Python312/Scripts/pip.exe"

def get_python_cmd():
    """Get the best available Python command."""
    if os.path.exists(WINDOWS_PYTHON):
        return WINDOWS_PYTHON
    elif os.path.exists("/usr/bin/python3"):
        return "/usr/bin/python3"
    else:
        return "python3"

def install_missing_packages(missing_packages):
    """Install missing packages using appropriate pip."""
    if os.path.exists(WINDOWS_PIP):
        pip_cmd = WINDOWS_PIP
    else:
        pip_cmd = "pip3"
    
    print(f"Installing missing packages: {', '.join(missing_packages)}")
    try:
        # Try regular pip first
        result = subprocess.run([pip_cmd, "install"] + missing_packages, 
                               timeout=300, check=False)
        if result.returncode != 0:
            # If regular pip fails, try with sudo (for Linux systems)
            print("Regular pip failed, trying with sudo...")
            result = subprocess.run(["sudo", pip_cmd, "install"] + missing_packages, 
                                   timeout=300, check=True)
        return True
    except subprocess.TimeoutExpired:
        print("❌ Package installation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Package installation failed: {e}")
        return False

def check_and_install_dependencies():
    """Check if required dependencies are available and install if missing."""
    python_cmd = get_python_cmd()
    required_packages = ["pandas", "httpx", "pydantic", "fastapi", "email-validator", "structlog", "click", "python-dotenv", "uvicorn", "pydantic-settings"]
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
        if install_missing_packages(missing_packages):
            print("✅ All dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install dependencies")
            return False
    
    print("✅ All dependencies are available")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <script.py> [args...]")
        sys.exit(1)
    
    if not check_and_install_dependencies():
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
