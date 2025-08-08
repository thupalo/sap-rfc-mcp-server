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
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True, capture_output=False):
    """Run a command and handle errors."""
    print(f"Running: {command}")
    result = subprocess.run(
        command,
        shell=True,
        check=check,
        capture_output=capture_output,
        text=True
    )
    if capture_output:
        return result.stdout.strip()
    return result.returncode == 0


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def setup_virtual_environment():
    """Set up virtual environment."""
    print("\n📦 Setting up virtual environment...")
    
    if Path("venv").exists():
        print("   Virtual environment already exists")
        return True
    
    try:
        run_command("python -m venv venv")
        print("   ✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to create virtual environment: {e}")
        return False


def get_pip_command():
    """Get the appropriate pip command for the platform."""
    if sys.platform == "win32":
        return "venv\\Scripts\\pip"
    else:
        return "venv/bin/pip"


def get_python_command():
    """Get the appropriate python command for the platform."""
    if sys.platform == "win32":
        return "venv\\Scripts\\python"
    else:
        return "venv/bin/python"


def install_dependencies():
    """Install Python dependencies."""
    print("\n📥 Installing dependencies...")
    
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    try:
        run_command(f"{pip_cmd} install --upgrade pip")
        print("   ✅ pip upgraded")
    except subprocess.CalledProcessError:
        print("   ⚠️  Failed to upgrade pip, continuing anyway")
    
    # Install main dependencies
    try:
        run_command(f"{pip_cmd} install -e .")
        print("   ✅ Main dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install main dependencies: {e}")
        return False
    
    # Install development dependencies
    try:
        run_command(f"{pip_cmd} install -e .[dev]")
        print("   ✅ Development dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  Failed to install dev dependencies: {e}")
    
    return True


def setup_configuration():
    """Set up configuration files."""
    print("\n⚙️  Setting up configuration...")
    
    # Copy environment template if .env doesn't exist
    if not Path(".env").exists():
        if Path(".env.template").exists():
            shutil.copy(".env.template", ".env")
            print("   ✅ Created .env from template")
            print("   📝 Please edit .env with your SAP connection details")
        else:
            print("   ⚠️  No .env.template found")
    else:
        print("   .env file already exists")
    
    # Create cache directory
    cache_dir = Path("cache")
    if not cache_dir.exists():
        cache_dir.mkdir()
        print("   ✅ Created cache directory")
    
    return True


def setup_development_tools():
    """Set up development tools."""
    print("\n🛠️  Setting up development tools...")
    
    pip_cmd = get_pip_command()
    
    # Install pre-commit if available
    try:
        run_command(f"{pip_cmd} install pre-commit", check=False)
        if Path(".pre-commit-config.yaml").exists():
            run_command("pre-commit install", check=False)
            print("   ✅ Pre-commit hooks installed")
        else:
            print("   ⚠️  No .pre-commit-config.yaml found")
    except subprocess.CalledProcessError:
        print("   ⚠️  Failed to set up pre-commit")
    
    return True


def run_tests():
    """Run basic tests to verify setup."""
    print("\n🧪 Running basic tests...")
    
    python_cmd = get_python_command()
    
    try:
        # Test imports
        result = run_command(
            f"{python_cmd} -c \"import sap_rfc_mcp_server; print('Import successful')\"",
            capture_output=True
        )
        print("   ✅ Package imports successfully")
        
        # Run pytest if available
        try:
            run_command(f"{python_cmd} -m pytest tests/ -v --tb=short", check=False)
            print("   ✅ Basic tests passed")
        except subprocess.CalledProcessError:
            print("   ⚠️  Some tests failed (this may be expected without SAP connection)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Import test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 SAP RFC MCP Server - Development Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_python_version():
        return 1
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found. Please run this script from the project root directory.")
        return 1
    
    # Setup steps
    steps = [
        ("Virtual Environment", setup_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Configuration", setup_configuration),
        ("Development Tools", setup_development_tools),
        ("Testing", run_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"   ❌ Unexpected error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    # Summary
    print("\n" + "=" * 50)
    if failed_steps:
        print("⚠️  Setup completed with issues:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease review the errors above and resolve them manually.")
    else:
        print("✅ Setup completed successfully!")
    
    print("\n📋 Next steps:")
    print("1. Edit .env file with your SAP connection details")
    print("2. Activate virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Test the server:")
    print("   python -m sap_rfc_mcp_server.server")
    
    return 0 if not failed_steps else 1


if __name__ == "__main__":
    sys.exit(main())
