#!/usr/bin/env python3
"""
Comprehensive MCP Integration Verification Script
This script performs thorough checks of the SAP RFC MCP server setup.
"""

import asyncio
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class MCPVerificationTool:
    """Comprehensive MCP integration verification tool."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.errors = []
        self.warnings = []
        
    def log_info(self, message: str):
        """Log info message."""
        print(f"ℹ️  {message}")
        
    def log_success(self, message: str):
        """Log success message."""
        print(f"✅ {message}")
        
    def log_warning(self, message: str):
        """Log warning message."""
        print(f"⚠️  {message}")
        self.warnings.append(message)
        
    def log_error(self, message: str):
        """Log error message."""
        print(f"❌ {message}")
        self.errors.append(message)
        
    def run_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr."""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=self.project_root
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", str(e)
    
    def check_system_requirements(self) -> bool:
        """Check system requirements."""
        self.log_info("Checking system requirements...")
        
        success = True
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 9):
            self.log_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            self.log_error(f"Python {python_version.major}.{python_version.minor} - Requires 3.9+")
            success = False
            
        # Check operating system
        os_name = platform.system()
        os_version = platform.release()
        self.log_success(f"Operating System: {os_name} {os_version}")
        
        # Check VS Code availability
        vs_code_commands = ["code", "code-insiders"]
        vs_code_found = False
        
        for cmd in vs_code_commands:
            success_cmd, stdout, stderr = self.run_command([cmd, "--version"])
            if success_cmd:
                lines = stdout.strip().split('\n')
                if lines:
                    version = lines[0]
                    self.log_success(f"VS Code found: {version}")
                    vs_code_found = True
                    break
                    
        if not vs_code_found:
            self.log_error("VS Code not found in PATH")
            success = False
            
        self.results['system_requirements'] = success
        return success
    
    def check_project_structure(self) -> bool:
        """Check project structure and files."""
        self.log_info("Checking project structure...")
        
        required_files = [
            ".vscode/mcp.json",
            "venv/Scripts/python.exe" if platform.system() == "Windows" else "venv/bin/python",
            "sap_rfc_mcp_server/server.py",
            "requirements.txt"
        ]
        
        optional_files = [
            ".env",
            "pyproject.toml",
            "CHANGELOG.md",
            "README.md"
        ]
        
        success = True
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log_success(f"Required file found: {file_path}")
            else:
                self.log_error(f"Required file missing: {file_path}")
                success = False
                
        for file_path in optional_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log_success(f"Optional file found: {file_path}")
            else:
                self.log_warning(f"Optional file missing: {file_path}")
                
        self.results['project_structure'] = success
        return success
    
    def check_mcp_configuration(self) -> bool:
        """Check MCP configuration file."""
        self.log_info("Checking MCP configuration...")
        
        mcp_config_path = self.project_root / ".vscode" / "mcp.json"
        
        if not mcp_config_path.exists():
            self.log_error("MCP configuration file not found: .vscode/mcp.json")
            self.results['mcp_configuration'] = False
            return False
            
        try:
            with open(mcp_config_path, 'r') as f:
                config = json.load(f)
                
            # Validate structure
            if "servers" not in config:
                self.log_error("MCP config missing 'servers' section")
                return False
                
            if "sap-rfc-server" not in config["servers"]:
                self.log_error("MCP config missing 'sap-rfc-server' definition")
                return False
                
            server_config = config["servers"]["sap-rfc-server"]
            required_keys = ["command", "args", "cwd"]
            
            for key in required_keys:
                if key not in server_config:
                    self.log_error(f"MCP server config missing '{key}'")
                    return False
                    
            self.log_success("MCP configuration is valid")
            
            # Check if command path exists
            command_path = Path(server_config["command"])
            if not command_path.is_absolute():
                command_path = self.project_root / command_path
                
            if command_path.exists():
                self.log_success(f"Python executable found: {command_path}")
            else:
                self.log_error(f"Python executable not found: {command_path}")
                return False
                
            self.results['mcp_configuration'] = True
            return True
            
        except json.JSONDecodeError as e:
            self.log_error(f"Invalid JSON in MCP configuration: {e}")
            self.results['mcp_configuration'] = False
            return False
        except Exception as e:
            self.log_error(f"Error reading MCP configuration: {e}")
            self.results['mcp_configuration'] = False
            return False
    
    def check_python_environment(self) -> bool:
        """Check Python virtual environment."""
        self.log_info("Checking Python environment...")
        
        # Determine Python executable path
        if platform.system() == "Windows":
            python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.project_root / "venv" / "bin" / "python"
            
        if not python_exe.exists():
            self.log_error(f"Virtual environment Python not found: {python_exe}")
            self.results['python_environment'] = False
            return False
            
        # Test Python version in venv
        success, stdout, stderr = self.run_command([str(python_exe), "--version"])
        if success:
            self.log_success(f"Virtual environment Python: {stdout.strip()}")
        else:
            self.log_error(f"Failed to get venv Python version: {stderr}")
            return False
            
        # Check if SAP RFC MCP server module is available
        success, stdout, stderr = self.run_command([
            str(python_exe), "-c", 
            "import sap_rfc_mcp_server.server; print('MCP server module available')"
        ])
        
        if success:
            self.log_success("SAP RFC MCP server module is importable")
        else:
            self.log_error(f"SAP RFC MCP server module import failed: {stderr}")
            return False
            
        # Check required dependencies
        required_packages = ["mcp", "pyrfc", "fastapi", "uvicorn"]
        
        success, stdout, stderr = self.run_command([str(python_exe), "-m", "pip", "list"])
        if success:
            installed_packages = stdout.lower()
            for package in required_packages:
                if package in installed_packages:
                    self.log_success(f"Required package found: {package}")
                else:
                    self.log_warning(f"Required package missing: {package}")
        else:
            self.log_warning("Could not check installed packages")
            
        self.results['python_environment'] = True
        return True
    
    def check_sap_configuration(self) -> bool:
        """Check SAP configuration."""
        self.log_info("Checking SAP configuration...")
        
        env_file = self.project_root / ".env"
        
        if not env_file.exists():
            self.log_warning(".env file not found - SAP connection may not work")
            self.results['sap_configuration'] = False
            return False
            
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                
            required_vars = ['SAP_ASHOST', 'SAP_SYSNR', 'SAP_CLIENT', 'SAP_USER']
            found_vars = []
            missing_vars = []
            
            for var in required_vars:
                if var in content and f"{var}=" in content:
                    found_vars.append(var)
                    self.log_success(f"SAP variable found: {var}")
                else:
                    missing_vars.append(var)
                    self.log_warning(f"SAP variable missing: {var}")
                    
            if missing_vars:
                self.log_warning(f"Missing SAP variables: {missing_vars}")
                self.results['sap_configuration'] = False
                return False
            else:
                self.log_success("All required SAP variables found")
                self.results['sap_configuration'] = True
                return True
                
        except Exception as e:
            self.log_error(f"Error reading .env file: {e}")
            self.results['sap_configuration'] = False
            return False
    
    def check_vs_code_extensions(self) -> bool:
        """Check VS Code MCP extensions."""
        self.log_info("Checking VS Code extensions...")
        
        vs_code_commands = ["code", "code-insiders"]
        
        for cmd in vs_code_commands:
            success, stdout, stderr = self.run_command([cmd, "--list-extensions"])
            if success:
                extensions = stdout.strip().split('\n')
                mcp_extensions = [ext for ext in extensions if 'mcp' in ext.lower()]
                
                if mcp_extensions:
                    self.log_success("MCP extensions found:")
                    for ext in mcp_extensions:
                        self.log_success(f"  📦 {ext}")
                    self.results['vs_code_extensions'] = True
                    return True
                else:
                    self.log_warning("No MCP extensions found")
                    break
            else:
                continue
                
        self.log_error("No MCP extensions found or VS Code not accessible")
        self.results['vs_code_extensions'] = False
        return False
    
    def test_mcp_server_startup(self) -> bool:
        """Test MCP server startup."""
        self.log_info("Testing MCP server startup...")
        
        # Determine Python executable path
        if platform.system() == "Windows":
            python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.project_root / "venv" / "bin" / "python"
            
        # Test if server can start (it will wait for input, so we'll timeout quickly)
        try:
            process = subprocess.Popen(
                [str(python_exe), "-m", "sap_rfc_mcp_server.server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=self.project_root,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Terminate the process
            process.terminate()
            
            try:
                stdout, stderr = process.communicate(timeout=5)
                
                # If it started without immediate errors, that's good
                if process.returncode != 0 and "asyncio.exceptions.CancelledError" not in stderr:
                    self.log_error(f"MCP server startup failed: {stderr}")
                    return False
                else:
                    self.log_success("MCP server can start successfully")
                    self.results['mcp_server_startup'] = True
                    return True
                    
            except subprocess.TimeoutExpired:
                process.kill()
                self.log_success("MCP server started (had to force kill)")
                self.results['mcp_server_startup'] = True
                return True
                
        except Exception as e:
            self.log_error(f"Error testing MCP server startup: {e}")
            self.results['mcp_server_startup'] = False
            return False
    
    def test_sap_connection(self) -> bool:
        """Test SAP connection if configured."""
        self.log_info("Testing SAP connection...")
        
        if not self.results.get('sap_configuration', False):
            self.log_warning("Skipping SAP connection test - configuration not available")
            self.results['sap_connection'] = False
            return False
            
        # Determine Python executable path
        if platform.system() == "Windows":
            python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.project_root / "venv" / "bin" / "python"
            
        # Test SAP connection using the security manager
        success, stdout, stderr = self.run_command([
            str(python_exe), "-m", "sap_rfc_mcp_server.sap_security_manager", "test"
        ], timeout=60)
        
        if success:
            self.log_success("SAP connection test passed")
            self.results['sap_connection'] = True
            return True
        else:
            self.log_error(f"SAP connection test failed: {stderr}")
            self.results['sap_connection'] = False
            return False
    
    def generate_setup_recommendations(self) -> List[str]:
        """Generate setup recommendations based on results."""
        recommendations = []
        
        if not self.results.get('system_requirements', False):
            recommendations.append("Install Python 3.9+ and VS Code 1.95+")
            
        if not self.results.get('mcp_configuration', False):
            recommendations.append("Run: python tools/setup_dev.py")
            
        if not self.results.get('python_environment', False):
            recommendations.append("Recreate virtual environment: python -m venv venv && ./venv/Scripts/pip install -e .")
            
        if not self.results.get('sap_configuration', False):
            recommendations.append("Configure SAP connection: python -m sap_rfc_mcp_server.sap_security_manager setup")
            
        if not self.results.get('vs_code_extensions', False):
            recommendations.append("Install MCP extension: code --install-extension automatalabs.copilot-mcp")
            
        if not self.results.get('sap_connection', False):
            recommendations.append("Verify SAP credentials and network connectivity")
            
        return recommendations
    
    def run_comprehensive_check(self) -> Dict:
        """Run all verification checks."""
        print("🔍 SAP RFC MCP Server - Comprehensive Verification")
        print("=" * 60)
        
        checks = [
            ("System Requirements", self.check_system_requirements),
            ("Project Structure", self.check_project_structure),
            ("MCP Configuration", self.check_mcp_configuration),
            ("Python Environment", self.check_python_environment),
            ("SAP Configuration", self.check_sap_configuration),
            ("VS Code Extensions", self.check_vs_code_extensions),
            ("MCP Server Startup", self.test_mcp_server_startup),
            ("SAP Connection", self.test_sap_connection)
        ]
        
        for check_name, check_func in checks:
            print(f"\n🔧 {check_name}")
            print("-" * 40)
            try:
                check_func()
            except Exception as e:
                self.log_error(f"Unexpected error in {check_name}: {e}")
                self.results[check_name.lower().replace(' ', '_')] = False
        
        # Generate summary
        print(f"\n📊 Verification Summary")
        print("=" * 60)
        
        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)
        
        for check, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{check.replace('_', ' ').title()}: {status}")
        
        print(f"\n🎯 Overall Score: {passed}/{total} checks passed")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        # Generate recommendations
        recommendations = self.generate_setup_recommendations()
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Final status
        critical_checks = ['system_requirements', 'mcp_configuration', 'python_environment']
        critical_passed = all(self.results.get(check, False) for check in critical_checks)
        
        if critical_passed and passed >= total * 0.7:
            print(f"\n✅ Setup Status: READY FOR USE")
            print("Your SAP RFC MCP server should work in VS Code!")
        elif critical_passed:
            print(f"\n⚠️  Setup Status: PARTIALLY READY")
            print("Basic functionality should work, but some features may be limited.")
        else:
            print(f"\n❌ Setup Status: NEEDS ATTENTION")
            print("Please address the critical issues before using the MCP server.")
        
        return self.results


def main():
    """Main verification function."""
    verifier = MCPVerificationTool()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--comprehensive":
        # Run comprehensive check
        results = verifier.run_comprehensive_check()
    else:
        # Run basic checks
        print("🔍 SAP RFC MCP Server - Quick Verification")
        print("=" * 50)
        print("Use --comprehensive for detailed checks")
        print()
        
        basic_checks = [
            verifier.check_system_requirements,
            verifier.check_mcp_configuration,
            verifier.check_python_environment,
            verifier.check_vs_code_extensions
        ]
        
        for check in basic_checks:
            check()
            
        passed = sum(1 for result in verifier.results.values() if result)
        total = len(verifier.results)
        print(f"\n🎯 Quick Check: {passed}/{total} passed")
        
        if passed < total:
            print("💡 Run with --comprehensive for detailed analysis")


if __name__ == "__main__":
    main()
