#!/usr/bin/env python3
"""
Prerequisites Checker for SAP RFC MCP Server
This script checks if all prerequisites are met before installation.
"""

import json
import platform
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple


class PrerequisitesChecker:
    """Check prerequisites for SAP RFC MCP Server installation."""
    
    def __init__(self):
        self.results = {}
        self.recommendations = []
        
    def log_info(self, message: str):
        """Log info message."""
        print(f"ℹ️  {message}")
        
    def log_success(self, message: str):
        """Log success message."""
        print(f"✅ {message}")
        
    def log_warning(self, message: str):
        """Log warning message."""
        print(f"⚠️  {message}")
        
    def log_error(self, message: str):
        """Log error message."""
        print(f"❌ {message}")
    
    def run_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr."""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except FileNotFoundError:
            return False, "", "Command not found"
        except Exception as e:
            return False, "", str(e)
    
    def check_python_version(self) -> bool:
        """Check Python version."""
        self.log_info("Checking Python version...")
        
        version = sys.version_info
        if version >= (3, 9):
            self.log_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
            return True
        else:
            self.log_error(f"Python {version.major}.{version.minor}.{version.micro} - Requires 3.9+")
            self.recommendations.append("Install Python 3.9 or higher from https://python.org")
            return False
    
    def check_pip(self) -> bool:
        """Check if pip is available."""
        self.log_info("Checking pip...")
        
        success, stdout, stderr = self.run_command([sys.executable, "-m", "pip", "--version"])
        if success:
            version = stdout.strip()
            self.log_success(f"pip available: {version}")
            return True
        else:
            self.log_error("pip not available")
            self.recommendations.append("Install pip: python -m ensurepip --upgrade")
            return False
    
    def check_git(self) -> bool:
        """Check if Git is available."""
        self.log_info("Checking Git...")
        
        success, stdout, stderr = self.run_command(["git", "--version"])
        if success:
            version = stdout.strip()
            self.log_success(f"Git available: {version}")
            return True
        else:
            self.log_error("Git not found")
            self.recommendations.append("Install Git from https://git-scm.com")
            return False
    
    def check_vs_code(self) -> bool:
        """Check VS Code availability and version."""
        self.log_info("Checking VS Code...")
        
        commands = ["code", "code-insiders"]
        
        for cmd in commands:
            success, stdout, stderr = self.run_command([cmd, "--version"])
            if success:
                lines = stdout.strip().split('\n')
                if lines:
                    version = lines[0]
                    self.log_success(f"VS Code found: {version}")
                    
                    # Check if version is 1.95+
                    try:
                        version_parts = version.split('.')
                        major = int(version_parts[0])
                        minor = int(version_parts[1])
                        
                        if major > 1 or (major == 1 and minor >= 95):
                            self.log_success("VS Code version supports native MCP ✓")
                            return True
                        else:
                            self.log_warning(f"VS Code {version} - MCP requires 1.95+")
                            self.recommendations.append("Update VS Code to version 1.95 or later")
                            return False
                    except (ValueError, IndexError):
                        self.log_warning("Could not parse VS Code version")
                        return True
        
        self.log_error("VS Code not found in PATH")
        self.recommendations.append("Install VS Code from https://code.visualstudio.com")
        return False
    
    def check_network_connectivity(self) -> bool:
        """Check network connectivity for downloading packages."""
        self.log_info("Checking network connectivity...")
        
        test_urls = [
            "https://pypi.org/simple/",
            "https://github.com",
            "https://registry.npmjs.org"
        ]
        
        connected = False
        for url in test_urls:
            try:
                response = urllib.request.urlopen(url, timeout=10)
                if response.status == 200:
                    connected = True
                    break
            except Exception:
                continue
        
        if connected:
            self.log_success("Network connectivity available ✓")
            return True
        else:
            self.log_error("Network connectivity issues detected")
            self.recommendations.append("Check internet connection and proxy settings")
            return False
    
    def check_disk_space(self) -> bool:
        """Check available disk space."""
        self.log_info("Checking disk space...")
        
        try:
            if platform.system() == "Windows":
                import shutil
                free_bytes = shutil.disk_usage(".").free
            else:
                import os
                statvfs = os.statvfs(".")
                free_bytes = statvfs.f_frsize * statvfs.f_bavail
            
            free_gb = free_bytes / (1024**3)
            
            if free_gb >= 2.0:
                self.log_success(f"Disk space: {free_gb:.1f} GB available ✓")
                return True
            else:
                self.log_warning(f"Disk space: {free_gb:.1f} GB - may need more space")
                self.recommendations.append("Ensure at least 2GB free disk space")
                return False
                
        except Exception as e:
            self.log_warning(f"Could not check disk space: {e}")
            return True
    
    def check_sap_rfc_sdk_availability(self) -> bool:
        """Check if SAP NetWeaver RFC SDK is likely available."""
        self.log_info("Checking SAP NetWeaver RFC SDK...")
        
        # Try to import pyrfc to see if SDK is available
        success, stdout, stderr = self.run_command([
            sys.executable, "-c", "import pyrfc; print('SAP RFC SDK available')"
        ])
        
        if success:
            self.log_success("SAP NetWeaver RFC SDK is available ✓")
            return True
        else:
            self.log_error("SAP NetWeaver RFC SDK not found")
            self.recommendations.extend([
                "Download SAP NetWeaver RFC SDK from SAP Service Marketplace",
                "Install pyrfc: pip install pyrfc",
                "See: https://sap.github.io/PyRFC/install.html"
            ])
            return False
    
    def check_vs_code_extensions(self) -> bool:
        """Check if MCP extension is available."""
        self.log_info("Checking VS Code MCP extensions...")
        
        commands = ["code", "code-insiders"]
        
        for cmd in commands:
            success, stdout, stderr = self.run_command([cmd, "--list-extensions"])
            if success:
                extensions = stdout.lower()
                if "mcp" in extensions:
                    self.log_success("MCP extension found ✓")
                    return True
                else:
                    self.log_warning("MCP extension not installed")
                    self.recommendations.append("Install MCP extension: code --install-extension automatalabs.copilot-mcp")
                    return False
        
        self.log_warning("Could not check VS Code extensions")
        return False
    
    def check_environment_permissions(self) -> bool:
        """Check file system permissions."""
        self.log_info("Checking permissions...")
        
        try:
            # Test if we can create files in current directory
            test_file = Path("._test_permissions")
            test_file.write_text("test")
            test_file.unlink()
            
            self.log_success("File system permissions ✓")
            return True
            
        except PermissionError:
            self.log_error("Insufficient file system permissions")
            self.recommendations.append("Run with appropriate permissions or change directory")
            return False
        except Exception as e:
            self.log_warning(f"Could not test permissions: {e}")
            return True
    
    def generate_installation_command(self) -> str:
        """Generate installation command based on OS."""
        if platform.system() == "Windows":
            return """
# Windows Installation Commands:
git clone https://github.com/thupalo/sap-rfc-mcp-server.git
cd sap-rfc-mcp-server
python -m venv venv
venv\\Scripts\\activate
pip install -e .
python tools/setup_dev.py
"""
        else:
            return """
# Linux/macOS Installation Commands:
git clone https://github.com/thupalo/sap-rfc-mcp-server.git
cd sap-rfc-mcp-server
python -m venv venv
source venv/bin/activate
pip install -e .
python tools/setup_dev.py
"""
    
    def run_all_checks(self) -> Dict[str, bool]:
        """Run all prerequisite checks."""
        print("🔍 SAP RFC MCP Server - Prerequisites Check")
        print("=" * 50)
        
        checks = [
            ("Python Version", self.check_python_version),
            ("pip", self.check_pip),
            ("Git", self.check_git),
            ("VS Code", self.check_vs_code),
            ("Network Connectivity", self.check_network_connectivity),
            ("Disk Space", self.check_disk_space),
            ("File Permissions", self.check_environment_permissions),
            ("SAP RFC SDK", self.check_sap_rfc_sdk_availability),
            ("VS Code MCP Extension", self.check_vs_code_extensions)
        ]
        
        for check_name, check_func in checks:
            print(f"\n🔧 {check_name}")
            print("-" * 30)
            try:
                result = check_func()
                self.results[check_name.lower().replace(" ", "_")] = result
            except Exception as e:
                self.log_error(f"Unexpected error: {e}")
                self.results[check_name.lower().replace(" ", "_")] = False
        
        return self.results
    
    def generate_report(self):
        """Generate final report."""
        print(f"\n📊 Prerequisites Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)
        
        # Critical requirements
        critical_checks = ['python_version', 'pip', 'git', 'vs_code']
        critical_passed = all(self.results.get(check, False) for check in critical_checks)
        
        # Optional but recommended
        optional_checks = ['sap_rfc_sdk', 'vs_code_mcp_extension']
        optional_passed = all(self.results.get(check, False) for check in optional_checks)
        
        for check, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            importance = "🔥 CRITICAL" if check in critical_checks else "⭐ RECOMMENDED"
            print(f"{check.replace('_', ' ').title()}: {status} ({importance})")
        
        print(f"\n🎯 Score: {passed}/{total} checks passed")
        
        # Overall status
        if critical_passed and optional_passed:
            print(f"\n✅ Status: READY TO INSTALL")
            print("All prerequisites are met. You can proceed with installation.")
        elif critical_passed:
            print(f"\n⚠️  Status: READY TO INSTALL (with limitations)")
            print("Critical prerequisites are met. Some features may require additional setup.")
        else:
            print(f"\n❌ Status: NOT READY")
            print("Please address critical prerequisites before installation.")
        
        # Recommendations
        if self.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Installation command
        if critical_passed:
            print(f"\n🚀 Next Steps:")
            print(self.generate_installation_command())
            
        # Additional resources
        print(f"\n📚 Additional Resources:")
        print("   • Complete Setup Guide: docs/COMPLETE_SETUP_GUIDE.md")
        print("   • VS Code Integration: docs/VSCODE_INTEGRATION_GUIDE.md")
        print("   • Troubleshooting: docs/TROUBLESHOOTING.md")


def main():
    """Main function."""
    checker = PrerequisitesChecker()
    checker.run_all_checks()
    checker.generate_report()


if __name__ == "__main__":
    main()
