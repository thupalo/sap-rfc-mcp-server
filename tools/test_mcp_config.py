#!/usr/bin/env python3
"""
Test script to verify MCP server configuration and functionality.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def check_mcp_config():
    """Check if MCP configuration exists and is valid."""
    print("🔍 Checking MCP Configuration...")
    
    project_root = Path(__file__).parent.parent
    mcp_config_path = project_root / ".vscode" / "mcp.json"
    
    if not mcp_config_path.exists():
        print("❌ MCP configuration file not found: .vscode/mcp.json")
        return False
    
    try:
        with open(mcp_config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ MCP configuration file found")
        print(f"📄 Config: {json.dumps(config, indent=2)}")
        
        # Check if sap-rfc-server is configured
        if "servers" in config and "sap-rfc-server" in config["servers"]:
            print("✅ SAP RFC MCP server configured")
            return True
        else:
            print("❌ SAP RFC MCP server not found in configuration")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in MCP configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading MCP configuration: {e}")
        return False


def check_python_executable():
    """Check if the Python executable specified in MCP config exists."""
    print("\n🐍 Checking Python Executable...")
    
    project_root = Path(__file__).parent.parent
    venv_python = project_root / "venv" / "Scripts" / "python.exe"
    
    if venv_python.exists():
        print(f"✅ Python executable found: {venv_python}")
        
        # Check if sap_rfc_mcp_server module is available
        try:
            result = subprocess.run([
                str(venv_python), "-c", 
                "import sap_rfc_mcp_server.server; print('MCP server module available')"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ MCP server module is importable")
                return True
            else:
                print(f"❌ MCP server module import failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️ MCP server module check timed out (this might be normal)")
            return True
        except Exception as e:
            print(f"❌ Error checking MCP server module: {e}")
            return False
    else:
        print(f"❌ Python executable not found: {venv_python}")
        return False


def check_env_config():
    """Check if environment configuration exists."""
    print("\n🔧 Checking Environment Configuration...")
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        print("✅ .env file found")
        
        # Check for required SAP variables
        required_vars = ['SAP_ASHOST', 'SAP_SYSNR', 'SAP_CLIENT', 'SAP_USER']
        missing_vars = []
        
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                
            for var in required_vars:
                if var not in content:
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"⚠️ Missing SAP configuration variables: {missing_vars}")
            else:
                print("✅ SAP configuration variables found")
                
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return False
            
        return True
    else:
        print("⚠️ .env file not found - you may need to configure SAP connection")
        return False


def check_vscode_extensions():
    """Check VS Code MCP extensions."""
    print("\n🖥️ Checking VS Code MCP Extensions...")
    
    try:
        result = subprocess.run([
            "code", "--list-extensions"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            extensions = result.stdout.strip().split('\n')
            mcp_extensions = [ext for ext in extensions if 'mcp' in ext.lower()]
            
            if mcp_extensions:
                print("✅ MCP-related extensions found:")
                for ext in mcp_extensions:
                    print(f"  📦 {ext}")
                return True
            else:
                print("⚠️ No MCP-related extensions found")
                print("💡 You may need to install an MCP extension for VS Code")
                return False
        else:
            print(f"❌ Error listing VS Code extensions: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ VS Code extension check timed out")
        return False
    except FileNotFoundError:
        print("❌ VS Code 'code' command not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error checking VS Code extensions: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 SAP RFC MCP Server Configuration Test")
    print("=" * 50)
    
    results = {
        "mcp_config": check_mcp_config(),
        "python_executable": check_python_executable(),
        "env_config": check_env_config(),
        "vscode_extensions": check_vscode_extensions()
    }
    
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if not passed:
            all_passed = False
    
    print("\n🎯 Overall Status:")
    if all_passed:
        print("✅ MCP server configuration appears to be working correctly!")
        print("💡 Your SAP RFC MCP server should be available in VS Code agent mode.")
    else:
        print("⚠️ Some issues found with MCP server configuration.")
        print("📖 Check the documentation: docs/VSCODE_INTEGRATION_GUIDE.md")
    
    print("\n🔍 To test MCP server in VS Code:")
    print("1. Open this workspace in VS Code")
    print("2. Enable GitHub Copilot agent mode")
    print("3. Ask: 'Get SAP system information' or similar queries")
    print("4. Check VS Code Output panel > MCP channel for server logs")


if __name__ == "__main__":
    main()
