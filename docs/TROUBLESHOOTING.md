# SAP RFC MCP Server - Troubleshooting Guide

This guide provides comprehensive solutions for common issues encountered when setting up and using the SAP RFC MCP server.

## 🔧 Quick Diagnostics

### Run Diagnostic Tools

```bash
# Check prerequisites
python tools/check_prerequisites.py

# Comprehensive verification
python tools/verify_mcp_integration.py --comprehensive

# Quick configuration test
python tools/test_mcp_config.py
```

## 🚨 Common Issues and Solutions

### ❌ **MCP Server Not Starting**

#### Symptoms:
- No output in VS Code MCP channel
- Server startup errors in terminal
- Module import failures

#### Solutions:

1. **Check Python Environment**
   ```bash
   # Verify virtual environment
   ./venv/Scripts/python.exe --version
   
   # Test module import
   ./venv/Scripts/python.exe -c "import sap_rfc_mcp_server"
   ```

2. **Reinstall Dependencies**
   ```bash
   # Recreate virtual environment
   rmdir /s venv  # Windows
   python -m venv venv
   ./venv/Scripts/activate
   pip install -e .
   ```

3. **Check MCP Configuration**
   ```bash
   # Validate configuration
   python -c "import json; print(json.load(open('.vscode/mcp.json')))"
   ```

### ❌ **VS Code Not Recognizing MCP Server**

#### Symptoms:
- MCP tools not available in Copilot
- No MCP output in VS Code
- Extension not loading

#### Solutions:

1. **Verify VS Code Version**
   ```bash
   code --version
   # Should be 1.95+ for native MCP support
   ```

2. **Check Extension Installation**
   ```bash
   # List MCP extensions
   code --list-extensions | grep mcp
   
   # Install if missing
   code --install-extension automatalabs.copilot-mcp
   ```

3. **Restart VS Code**
   - Close all VS Code windows
   - Reopen workspace
   - Check Output panel > MCP channel

4. **Verify Workspace Configuration**
   ```json
   // .vscode/mcp.json should exist and be valid
   {
     "servers": {
       "sap-rfc-server": {
         "command": "./venv/Scripts/python.exe",
         "args": ["-m", "sap_rfc_mcp_server.server"],
         "cwd": "./",
         "env": {
           "SAP_RFC_MCP_CONFIG": "./.env"
         }
       }
     }
   }
   ```

### ❌ **SAP Connection Issues**

#### Symptoms:
- SAP connection timeouts
- Authentication errors
- RFC access denied

#### Solutions:

1. **Test Direct Connection**
   ```bash
   # Test SAP connectivity
   python tools/test_direct_sap.py
   
   # Check credentials
   python -m sap_rfc_mcp_server.sap_security_manager info
   ```

2. **Network Connectivity**
   ```bash
   # Test hostname resolution
   ping your-sap-hostname
   
   # Test SAP port (usually 3300 + system number)
   telnet your-sap-hostname 3300
   ```

3. **SAP User Permissions**
   - Verify RFC execution permissions
   - Check user is not locked
   - Ensure client allows RFC connections

4. **Configuration Validation**
   ```env
   # .env file should contain:
   SAP_ASHOST=your-hostname
   SAP_SYSNR=00
   SAP_CLIENT=100
   SAP_USER=your-username
   SAP_PASSWD=your-password
   SAP_LANG=EN
   ```

### ❌ **pyrfc Installation Issues**

#### Symptoms:
- "pyrfc module not found"
- SAP NetWeaver RFC SDK errors
- C++ compilation errors

#### Solutions:

1. **Install SAP NetWeaver RFC SDK**
   - Download from SAP Service Marketplace
   - Extract to appropriate directory
   - Set environment variables

2. **Windows Setup**
   ```cmd
   # Set environment variables
   set SAPNWRFC_HOME=C:\nwrfcsdk
   set PATH=%PATH%;%SAPNWRFC_HOME%\lib
   
   # Install pyrfc
   pip install pyrfc
   ```

3. **Linux Setup**
   ```bash
   # Set environment variables
   export SAPNWRFC_HOME=/usr/local/sap/nwrfcsdk
   export LD_LIBRARY_PATH=$SAPNWRFC_HOME/lib:$LD_LIBRARY_PATH
   
   # Install pyrfc
   pip install pyrfc
   ```

4. **Verify Installation**
   ```bash
   python tools/check_sapnwrfc_sdk.py
   ```

### ❌ **Port Conflicts**

#### Symptoms:
- "Port already in use" errors
- HTTP server startup failures
- Multiple server instances

#### Solutions:

1. **Check Port Usage**
   ```bash
   # Check if port is in use
   python tools/port_manager.py --check 8000
   
   # Find available port
   python tools/port_manager.py --suggest
   ```

2. **Kill Existing Processes**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <process_id> /F
   
   # Linux/macOS
   lsof -i :8000
   kill -9 <process_id>
   ```

3. **Use Different Port**
   ```bash
   # Start on different port
   ./tools/start_sap_mcp_server.ps1 -Port 8080
   ```

### ❌ **Performance Issues**

#### Symptoms:
- Slow response times
- Memory usage
- Connection timeouts

#### Solutions:

1. **Enable Caching**
   ```env
   # Add to .env
   SAP_CACHE_ENABLED=true
   SAP_CACHE_TTL=3600
   ```

2. **Optimize Connection Pool**
   ```env
   # Add to .env
   SAP_POOL_SIZE=5
   SAP_CONNECTION_TIMEOUT=30
   ```

3. **Monitor Performance**
   ```bash
   # Check cache statistics
   python -c "
   from sap_rfc_mcp_server.metadata_cache import MetadataCache
   cache = MetadataCache()
   print(cache.get_statistics())
   "
   ```

### ❌ **GitHub Copilot Integration Issues**

#### Symptoms:
- Copilot doesn't see SAP tools
- No SAP context in responses
- Agent mode not working

#### Solutions:

1. **Verify Copilot Subscription**
   - Ensure GitHub Copilot is active
   - Check Copilot extension is enabled

2. **Enable Agent Mode**
   - Open Command Palette (`Ctrl+Shift+P`)
   - Type "Copilot: Enable Agent Mode"
   - Restart VS Code

3. **Check MCP Integration**
   ```bash
   # Verify MCP tools are listed
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python -m sap_rfc_mcp_server.server
   ```

## 🔍 Advanced Troubleshooting

### Enable Debug Logging

#### MCP Server Debug Mode
```json
{
  "servers": {
    "sap-rfc-server": {
      "command": "./venv/Scripts/python.exe",
      "args": ["-m", "sap_rfc_mcp_server.server", "--debug"],
      "cwd": "./",
      "env": {
        "SAP_RFC_MCP_CONFIG": "./.env",
        "MCP_DEBUG": "1"
      }
    }
  }
}
```

#### SAP RFC Tracing
```env
# Add to .env file
SAP_TRACE=1
RFC_TRACE=1
PYRFC_TRACE=1
```

#### Python Logging
```bash
# Run with verbose logging
python -m sap_rfc_mcp_server.server --log-level DEBUG
```

### Environment Diagnosis

#### System Information
```bash
# Get comprehensive system info
python tools/diagnose_setup.py --system-info
```

#### Check Dependencies
```bash
# List all installed packages
./venv/Scripts/pip list

# Check specific packages
./venv/Scripts/pip show pyrfc mcp fastapi
```

#### Test Network Connectivity
```bash
# Test SAP connectivity
python -c "
import socket
s = socket.socket()
try:
    s.connect(('your-sap-host', 3300))
    print('SAP port accessible')
except:
    print('SAP port not accessible')
s.close()
"
```

### Manual MCP Protocol Testing

#### Test MCP Communication
```bash
# Send MCP initialization
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python -m sap_rfc_mcp_server.server

# List available tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python -m sap_rfc_mcp_server.server

# Call a tool
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"rfc_system_info","arguments":{}}}' | python -m sap_rfc_mcp_server.server
```

### File Permission Issues

#### Windows Permissions
```cmd
# Check file permissions
icacls .vscode\mcp.json
icacls .env

# Fix permissions if needed
icacls .vscode\mcp.json /grant %USERNAME%:F
```

#### Linux/macOS Permissions
```bash
# Check permissions
ls -la .vscode/mcp.json
ls -la .env

# Fix permissions
chmod 600 .env
chmod 644 .vscode/mcp.json
```

## 📊 Health Check Script

Create and run this comprehensive health check:

```bash
# Create health check script
cat > health_check.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import sys
import json
from pathlib import Path

def run_check(name, command):
    print(f"🔧 {name}...")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {name}: OK")
            return True
        else:
            print(f"❌ {name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

# Run health checks
checks = [
    ("Python", [sys.executable, "--version"]),
    ("MCP Config", ["python", "-c", "import json; json.load(open('.vscode/mcp.json'))"]),
    ("SAP Module", ["python", "-c", "import sap_rfc_mcp_server"]),
    ("MCP Server", ["python", "-c", "from sap_rfc_mcp_server import server"]),
]

passed = 0
for name, command in checks:
    if run_check(name, command):
        passed += 1

print(f"\n🎯 Health Check: {passed}/{len(checks)} passed")
EOF

python health_check.py
```

## 🆘 Getting Help

### Collect Diagnostic Information

Before reporting issues, collect this information:

```bash
# Run comprehensive diagnostics
python tools/verify_mcp_integration.py --comprehensive > diagnostic_report.txt

# Add system information
python -c "
import platform, sys
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Architecture: {platform.machine()}')
" >> diagnostic_report.txt

# Add VS Code information
code --version >> diagnostic_report.txt

# Add extension information
code --list-extensions --show-versions | grep mcp >> diagnostic_report.txt
```

### Report Issues

When reporting issues, include:

1. **Diagnostic Report**: Output from verification script
2. **Error Messages**: Complete error messages and stack traces
3. **Configuration**: Sanitized configuration files (remove passwords)
4. **Steps to Reproduce**: Detailed steps that led to the issue
5. **Environment**: OS, Python version, VS Code version

### Community Resources

- **GitHub Issues**: [Report bugs](https://github.com/thupalo/sap-rfc-mcp-server/issues)
- **Discussions**: [Ask questions](https://github.com/thupalo/sap-rfc-mcp-server/discussions)
- **Documentation**: [Complete guides](docs/)

## 📝 Known Issues and Workarounds

### Issue: VS Code MCP Extension Not Loading
**Workaround**: Use VS Code Insiders with latest MCP support

### Issue: pyrfc Installation on ARM Macs
**Workaround**: Use x86_64 Python environment with Rosetta

### Issue: Corporate Proxy Issues
**Workaround**: Configure pip and git proxy settings

```bash
# Configure pip proxy
pip config set global.proxy http://proxy:port

# Configure git proxy
git config --global http.proxy http://proxy:port
```

### Issue: SAP GUI Required Error
**Workaround**: Use direct RFC connections instead of GUI-based auth

## 🔄 Recovery Procedures

### Complete Reset
```bash
# Backup configuration
cp .env .env.backup
cp .vscode/mcp.json .vscode/mcp.json.backup

# Clean environment
rm -rf venv
rm -rf __pycache__
rm -rf *.egg-info

# Reinstall
python -m venv venv
./venv/Scripts/activate
pip install -e .
python tools/setup_dev.py

# Restore configuration
cp .env.backup .env
```

### Configuration Recovery
```bash
# Regenerate MCP configuration
python tools/setup_dev.py --force-config

# Regenerate SAP configuration
python -m sap_rfc_mcp_server.sap_security_manager setup
```
