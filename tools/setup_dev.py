#!/usr/bin/env python3
"""
Setup script for SAP RFC MCP Server development environment.

This script helps set up the development environment for the SAP RFC MCP Server.
It handles:
- Virtual environment creation
- Dependency installation
- Configuration file setup
- Development tools setup
"""

import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(command, check=True, capture_output=False):
    """Run a command and handle errors."""
    print(f"Running: {command}")
    result = subprocess.run(
        command, shell=True, check=check, capture_output=capture_output, text=True
    )
    if capture_output:
        return result.stdout.strip()
    return result.returncode == 0


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("[ERROR] Python 3.9 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False

    print(f"[OK] Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_sapnwrfc_prerequisites():
    """Check SAP NetWeaver RFC SDK prerequisites."""
    print("\n[PREREQUISITE] Checking SAP NetWeaver RFC SDK...")
    print("=" * 50)

    issues_found = []
    checks_passed = 0
    total_checks = 5  # Reduced checks for prerequisites

    # Check 1: SAPNWRFC_HOME environment variable
    print("[1] Checking SAPNWRFC_HOME environment variable...")
    total_checks += 1

    sapnwrfc_home = os.environ.get("SAPNWRFC_HOME")
    if sapnwrfc_home:
        print(f"[OK] SAPNWRFC_HOME found: {sapnwrfc_home}")
        checks_passed += 1

        # Verify the path exists
        if Path(sapnwrfc_home).exists():
            print(f"[OK] Directory exists: {sapnwrfc_home}")
        else:
            print(f"[ERROR] Directory does not exist: {sapnwrfc_home}")
            issues_found.append("SAPNWRFC_HOME points to non-existent directory")
            return False
    else:
        print("[ERROR] SAPNWRFC_HOME environment variable not set")
        issues_found.append("SAPNWRFC_HOME environment variable missing")
        print("\n[TIP] Download and install SAP NetWeaver RFC SDK:")
        print("1. Go to SAP Support Portal (support.sap.com)")
        print("2. Download 'SAP NetWeaver RFC SDK' for your platform")
        print("3. Extract to a folder (e.g., C:\\SAPNWRFC_750)")
        print("4. Set SAPNWRFC_HOME environment variable to point to that folder")
        print("5. Add %SAPNWRFC_HOME%\\lib to your PATH")
        return False

    # Check 2: Required folder structure
    print(f"\n[2] Checking required folder structure...")

    expected_folders = ["bin", "lib", "include"]
    sapnwrfc_path = Path(sapnwrfc_home)
    missing_folders = []

    for folder in expected_folders:
        folder_path = sapnwrfc_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"[OK] {folder:8} folder found")
        else:
            print(f"[ERROR] {folder:8} folder missing")
            missing_folders.append(folder)

    if not missing_folders:
        checks_passed += 1
    else:
        issues_found.append(f"Missing folders: {', '.join(missing_folders)}")
        return False

    # Check 3: Critical library files
    print(f"\n[3] Checking critical library files...")

    critical_files = [
        "lib/sapnwrfc.dll",
        "lib/icudt50.dll",
        "lib/icuin50.dll",
        "lib/icuuc50.dll",
    ]

    missing_files = []

    for file_path in critical_files:
        full_path = sapnwrfc_path / file_path
        if full_path.exists() and full_path.is_file():
            print(f"[OK] {file_path}")
        else:
            print(f"[ERROR] {file_path} missing")
            missing_files.append(file_path)

    if not missing_files:
        checks_passed += 1
    else:
        issues_found.append(f"Missing critical files: {', '.join(missing_files)}")
        return False

    # Check 4: PATH environment variable
    print(f"\n[4] Checking PATH environment variable...")

    path_env = os.environ.get("PATH", "")
    lib_path = str(sapnwrfc_path / "lib")

    if lib_path.lower() in path_env.lower():
        print(f"[OK] SAP NetWeaver RFC lib directory found in PATH")
        checks_passed += 1
    else:
        print(f"[WARNING] SAP NetWeaver RFC lib directory not in PATH")
        print(f"[TIP] Add to PATH: {lib_path}")
        issues_found.append("SAP NetWeaver RFC lib directory not in PATH")
        return False

    # Check 5: Try to import pyrfc (if possible)
    print(f"\n[5] Checking Python pyrfc module...")

    try:
        import pyrfc

        print(f"[OK] pyrfc module imported successfully")
        print(f"[INFO] pyrfc version: {pyrfc.__version__}")
        checks_passed += 1
    except ImportError:
        print(
            f"[INFO] pyrfc module not yet installed (will be installed with dependencies)"
        )
        checks_passed += 1  # This is OK during setup
    except Exception as e:
        print(f"[ERROR] Error testing pyrfc: {e}")
        issues_found.append(f"pyrfc module error: {e}")
        return False

    if checks_passed >= 4:  # Allow for pyrfc not being installed yet
        print(f"\n[SUCCESS] SAP NetWeaver RFC SDK prerequisites satisfied!")
        return True
    else:
        print(f"\n[ERROR] SAP NetWeaver RFC SDK prerequisites not met!")
        return False


def setup_virtual_environment():
    """Set up virtual environment."""
    print("\n[PACKAGE] Setting up virtual environment...")

    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"

    if venv_path.exists():
        print(f"[OK] Virtual environment already exists at: {venv_path}")
        return True

    # Create virtual environment
    if not run_command(f'python -m venv "{venv_path}"'):
        print("[ERROR] Failed to create virtual environment")
        return False

    print(f"[OK] Virtual environment created at: {venv_path}")
    return True


def install_dependencies():
    """Install project dependencies."""
    print("\n[EMOJI] Installing dependencies...")

    project_root = Path(__file__).parent.parent
    venv_python = project_root / "venv" / "Scripts" / "python.exe"

    if not venv_python.exists():
        print(f"[ERROR] Python executable not found at: {venv_python}")
        return False

    # Install in development mode
    if not run_command(f'"{venv_python}" -m pip install -e "."'):
        print("[ERROR] Failed to install project in development mode")
        return False

    print("[OK] Dependencies installed successfully")
    return True


def setup_configuration():
    """Set up configuration files."""
    print("\n[GEAR]  Setting up configuration...")

    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    if env_file.exists():
        print(f"[OK] Configuration file already exists: {env_file}")
        return True

    # Create sample .env file
    env_content = """# SAP RFC MCP Server Configuration
# Copy this file to .env and fill in your SAP connection details

# SAP Connection Parameters
SAP_HOST=your.sap.server.com
SAP_SYSNR=00
SAP_CLIENT=100
SAP_USER=your_username
SAP_PASSWORD=your_password

# Optional Parameters
SAP_LANG=EN
SAP_TRACE=0

# MCP Server Settings
MCP_HOST=127.0.0.1
MCP_PORT=8000

# Security Settings (optional)
ENABLE_ENCRYPTION=false
"""

    with open(env_file, "w") as f:
        f.write(env_content)

    print(f"[OK] Sample configuration created: {env_file}")
    print("   Please edit this file with your SAP connection details")
    return True


def setup_vs_code():
    """Set up VS Code configuration."""
    print("\n[CONFIG] Setting up VS Code configuration...")

    project_root = Path(__file__).parent.parent
    vscode_dir = project_root / ".vscode"

    if vscode_dir.exists():
        print(f"[OK] VS Code configuration already exists: {vscode_dir}")
        return True

    # Create .vscode directory
    vscode_dir.mkdir(exist_ok=True)

    # Create settings.json
    settings = {
        "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
        "python.terminal.activateEnvironment": True,
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": True,
        "python.formatting.provider": "black",
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            "**/venv": True,
            "**/.env": True,
        },
    }

    with open(vscode_dir / "settings.json", "w") as f:
        import json

        json.dump(settings, f, indent=4)

    print(f"[OK] VS Code settings created: {vscode_dir / 'settings.json'}")
    return True


def verify_installation():
    """Verify the installation."""
    print("\n[SEARCH] Verifying installation...")

    project_root = Path(__file__).parent.parent
    venv_python = project_root / "venv" / "Scripts" / "python.exe"

    # Test import
    test_command = f'"{venv_python}" -c "from sap_rfc_mcp_server import SAPRFCManager; print(\'[OK] Import successful\')"'

    if not run_command(test_command, check=False):
        print("[ERROR] Import test failed")
        return False

    print("[OK] Installation verification successful")
    return True


def main():
    """Main setup function."""
    print("[LAUNCH] SAP RFC MCP Server Development Environment Setup")
    print("=" * 60)

    # Check prerequisites
    if not check_python_version():
        sys.exit(1)

    if not check_sapnwrfc_prerequisites():
        print("\n[ERROR] SAP NetWeaver RFC SDK prerequisites not met!")
        print("[TIP] Please install and configure SAP NetWeaver RFC SDK first.")
        print("For detailed checking, run: python tools/check_sapnwrfc_sdk.py")
        sys.exit(1)

    # Setup steps
    steps = [
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up configuration", setup_configuration),
        ("Setting up VS Code", setup_vs_code),
        ("Verifying installation", verify_installation),
    ]

    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_func():
            print(f"[ERROR] Failed: {step_name}")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("[SUCCESS] Development environment setup completed successfully!")
    print("\n[LIST] Next steps:")
    print("1. Edit .env file with your SAP connection details")
    print("2. Open the project in VS Code")
    print("3. Select the Python interpreter from ./venv/Scripts/python.exe")
    print("4. Test the connection with: python -m sap_rfc_mcp_server.server")
    print("\n[TIP] Quick commands:")
    print("   Activate venv:     .\\venv\\Scripts\\Activate.ps1")
    print("   Start STDIO:       python -m sap_rfc_mcp_server.server")
    print(
        "   Start HTTP:        python -m sap_rfc_mcp_server.http_server 127.0.0.1 8000"
    )
    print("   Port management:   python tools/port_manager.py --help")
    print("   Check SDK:         python tools/check_sapnwrfc_sdk.py")
    print("   Config check:      python tools/check_config.py")


if __name__ == "__main__":
    main()
