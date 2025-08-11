# SAP RFC MCP Server - Complete Setup and Verification Guide

This comprehensive guide will help you set up, verify, and troubleshoot the SAP RFC MCP server integration with VS Code.

## 📋 Prerequisites Checklist

### System Requirements

#### ✅ **Required Software**
- [ ] **Python 3.9+** - Check with: `python --version`
- [ ] **VS Code 1.95+** (November 2024 or later) - Check with: `code --version`
- [ ] **Git** (for repository management) - Check with: `git --version`
- [ ] **SAP NetWeaver RFC SDK** - Required for SAP connectivity

#### ✅ **VS Code Extensions**
- [ ] **GitHub Copilot** (for AI assistance) - Optional but recommended
- [ ] **MCP Extension** - One of the following:
  - `automatalabs.copilot-mcp` (Recommended)
  - `modelcontextprotocol.mcp` (Alternative)

#### ✅ **SAP System Access**
- [ ] **SAP System Credentials** (username/password)
- [ ] **SAP System Details** (hostname, system number, client)
- [ ] **RFC Access** enabled on your SAP user
- [ ] **Network Connectivity** to SAP system

### Quick Prerequisites Check

Run this command to verify basic requirements:

```bash
# Download and run the prerequisites checker
curl -o check_prerequisites.py https://raw.githubusercontent.com/thupalo/sap-rfc-mcp-server/main/tools/check_prerequisites.py
python check_prerequisites.py
```

## 🚀 Installation Steps

### Step 1: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/thupalo/sap-rfc-mcp-server.git
cd sap-rfc-mcp-server

# Run automated setup
python tools/setup_dev.py
```

### Step 2: Configure SAP Connection

```bash
# Interactive secure configuration (Recommended)
python -m sap_rfc_mcp_server.sap_security_manager setup

# Test SAP connection
python -m sap_rfc_mcp_server.sap_security_manager test
```

### Step 3: Install VS Code MCP Extension

```bash
# Install the MCP extension
code --install-extension automatalabs.copilot-mcp

# Verify installation
code --list-extensions | grep mcp
```

### Step 4: Verify MCP Configuration

```bash
# Run comprehensive configuration test
python tools/test_mcp_config.py

# Verify MCP server can start
python tools/verify_mcp_integration.py
```

## 🔧 Manual Configuration (If Automated Setup Fails)

### Create VS Code MCP Configuration

Create `.vscode/mcp.json` in your workspace:

```json
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

### Create SAP Configuration

Create `.env` file with your SAP details:

```env
# SAP Connection Parameters
SAP_ASHOST=your-sap-hostname
SAP_SYSNR=00
SAP_CLIENT=100
SAP_USER=your-username
SAP_PASSWD=your-password
SAP_LANG=EN

# Optional: Advanced Settings
SAP_SAPROUTER=your-saprouter
SAP_POOL_SIZE=10
SAP_TRACE=0
```

## 🧪 Verification and Testing

### Automated Verification

```bash
# Run the complete verification suite
python tools/verify_mcp_integration.py --comprehensive

# Test specific components
python tools/test_mcp_config.py
python tools/test_direct_sap.py
python tools/test_vscode_integration.py
```

### Manual Verification Steps

#### 1. VS Code Integration Test

1. **Open Workspace in VS Code**
   ```bash
   code .
   ```

2. **Check MCP Server Status**
   - Open Command Palette (`Ctrl+Shift+P`)
   - Type "Output" and select "Show Output"
   - Select "MCP" from the dropdown
   - Look for SAP RFC server startup messages

3. **Test with GitHub Copilot**
   - Enable Copilot agent mode
   - Ask: "Get SAP system information"
   - Ask: "Search for SAP functions containing 'TABLE'"
   - Ask: "Show metadata for RFC_READ_TABLE"

#### 2. Direct MCP Server Test

```bash
# Test MCP server directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python -m sap_rfc_mcp_server.server
```

Expected response should include SAP RFC tools like:
- `rfc_system_info`
- `get_rfc_functions`
- `get_function_metadata`
- `read_table`

#### 3. HTTP API Test

```bash
# Start HTTP server
python -m sap_rfc_mcp_server.http_server 127.0.0.1 8000

# Test API endpoints
curl http://localhost:8000/docs
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{"name": "rfc_system_info", "arguments": {}}'
```

## 🔍 Troubleshooting Guide

### Common Issues and Solutions

#### ❌ **MCP Server Not Starting**

**Symptoms:**
- No MCP output in VS Code
- Server startup errors
- Module import failures

**Solutions:**

1. **Check Python Environment**
   ```bash
   ./venv/Scripts/python.exe --version
   ./venv/Scripts/python.exe -c "import sap_rfc_mcp_server"
   ```

2. **Verify Dependencies**
   ```bash
   ./venv/Scripts/pip list | grep -E "(mcp|pyrfc)"
   ```

3. **Reinstall Dependencies**
   ```bash
   ./venv/Scripts/pip install -e .
   ```

#### ❌ **SAP Connection Issues**

**Symptoms:**
- SAP connection timeouts
- Authentication errors
- RFC access denied

**Solutions:**

1. **Test Direct SAP Connection**
   ```bash
   python tools/test_direct_sap.py
   ```

2. **Check SAP Credentials**
   ```bash
   python -m sap_rfc_mcp_server.sap_security_manager info
   ```

3. **Verify Network Connectivity**
   ```bash
   ping your-sap-hostname
   telnet your-sap-hostname 3300
   ```

#### ❌ **VS Code MCP Extension Issues**

**Symptoms:**
- MCP extension not loading
- No MCP commands available
- Extension errors

**Solutions:**

1. **Verify Extension Installation**
   ```bash
   code --list-extensions | grep mcp
   ```

2. **Check Extension Version**
   ```bash
   code --list-extensions --show-versions | grep mcp
   ```

3. **Reinstall Extension**
   ```bash
   code --uninstall-extension automatalabs.copilot-mcp
   code --install-extension automatalabs.copilot-mcp
   ```

4. **Check VS Code Version**
   ```bash
   code --version
   # Should be 1.95+ for native MCP support
   ```

### Advanced Troubleshooting

#### Enable Debug Logging

1. **MCP Server Debug Mode**
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

2. **SAP RFC Debug Logging**
   ```env
   # Add to .env file
   SAP_TRACE=1
   RFC_TRACE=1
   ```

#### Port Conflicts

```bash
# Check for port conflicts
python tools/port_manager.py --check 8000
python tools/port_manager.py --suggest
```

#### Permission Issues

```bash
# Windows: Run as Administrator if needed
# Check file permissions
ls -la .vscode/mcp.json
ls -la .env
```

## 📊 Verification Checklist

After completing setup, verify these items:

### ✅ **Configuration Files**
- [ ] `.vscode/mcp.json` exists and is valid JSON
- [ ] `.env` file exists with SAP credentials
- [ ] Virtual environment is activated
- [ ] All dependencies are installed

### ✅ **VS Code Integration**
- [ ] MCP extension is installed and enabled
- [ ] VS Code version 1.95+ is installed
- [ ] Workspace is opened in VS Code
- [ ] MCP output channel shows server startup

### ✅ **SAP Connectivity**
- [ ] SAP system is accessible from network
- [ ] SAP credentials are valid
- [ ] RFC access is enabled for user
- [ ] SAP connection test passes

### ✅ **MCP Server Functionality**
- [ ] MCP server starts without errors
- [ ] Tools are listed correctly
- [ ] SAP system info can be retrieved
- [ ] Function metadata can be accessed

### ✅ **End-to-End Testing**
- [ ] GitHub Copilot can access SAP tools
- [ ] SAP queries work in agent mode
- [ ] Error handling works correctly
- [ ] Performance is acceptable

## 🎯 Success Indicators

When everything is working correctly, you should see:

1. **VS Code Output (MCP Channel):**
   ```
   [MCP] SAP RFC MCP Server starting...
   [MCP] Connected to SAP system: <hostname>
   [MCP] Server ready with 8 tools available
   ```

2. **GitHub Copilot Integration:**
   - Copilot can answer SAP-related questions
   - SAP system information is accessible
   - Function metadata queries work

3. **Manual Testing:**
   ```bash
   # This should return SAP system info
   python tools/test_direct_sap.py
   ```

## 📚 Additional Resources

- **[Complete Setup Guide](docs/VSCODE_INTEGRATION_GUIDE.md)** - Detailed integration instructions
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[API Documentation](docs/API.md)** - MCP server API reference
- **[Security Guide](docs/SECURITY.md)** - Secure configuration best practices

## 🆘 Getting Help

If you encounter issues:

1. **Run Diagnostics:**
   ```bash
   python tools/diagnose_setup.py --full-report
   ```

2. **Check Logs:**
   - VS Code Output panel (MCP channel)
   - Terminal output when running tests
   - System event logs (if applicable)

3. **Report Issues:**
   - Include diagnostic report output
   - VS Code version and extension versions
   - Operating system and Python version
   - SAP system version (if known)

4. **Community Support:**
   - GitHub Issues: [Report a bug](https://github.com/thupalo/sap-rfc-mcp-server/issues)
   - Discussions: [Ask questions](https://github.com/thupalo/sap-rfc-mcp-server/discussions)
