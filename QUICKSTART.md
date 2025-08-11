# [ROCKET] Quick Start Guide

Get up and running with the SAP RFC MCP Server in minutes!

## [CHECKLIST] Prerequisites

Before you begin, ensure you have:

- **Python 3.9 or higher** installed
- **SAP NetWeaver RFC SDK** installed and configured
- **Access to a SAP system** with RFC connectivity
- **Git** (optional, for cloning)

## [LIGHTNING] Fast Setup (Automated)

The quickest way to get started:

```bash
# 1. Clone or download the project
git clone https://github.com/thupalo/sap-rfc-mcp-server.git
cd sap-rfc-mcp-server

# 2. Run the automated setup script (includes SAP NetWeaver RFC SDK checking)
python tools/setup_dev.py

# 3. Configure your SAP connection (Security Manager - Recommended)
python -m sap_rfc_mcp_server.sap_security_manager setup

# Alternative: Quick .env configuration
# Edit the .env file with your SAP details
notepad .env  # Windows
nano .env     # Linux/Mac

# 4. Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 5. Test the installation
python examples/basic_usage.py
```

> [INFO] The automated setup now includes SAP NetWeaver RFC SDK validation!

## [WRENCH] Manual Setup

If you prefer to set up manually:

### 1. Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -e .
pip install -e ".[dev]"  # For development
```

### 3. Configure SAP Connection

**🔐 Option 1: Interactive Security Manager (Recommended)**

Use the secure interactive configuration tool:
```bash
# Secure interactive setup
python -m sap_rfc_mcp_server.sap_security_manager setup

# Test your connection
python -m sap_rfc_mcp_server.sap_security_manager test

# View configuration status
python -m sap_rfc_mcp_server.sap_security_manager info
```

The Security Manager supports multiple secure storage methods:
- **Environment Variables**: Direct system environment
- **.env Files**: File-based configuration
- **System Keyring**: OS credential manager
- **Encrypted Files**: Password-protected storage

**📄 Option 2: Manual .env Configuration**

Copy the environment template:
```bash
cp .env.template .env
```

Edit `.env` with your SAP connection details:
```env
SAP_ASHOST=your-sap-hostname
SAP_SYSNR=00
SAP_CLIENT=100
SAP_USER=your-username
SAP_PASSWD=your-password
SAP_LANG=EN
```

**🔄 Option 3: Migration Between Methods**

```bash
# Migrate from .env to more secure storage
python -m sap_rfc_mcp_server.sap_security_manager migrate
```

### 4. Test Connection

```bash
python examples/basic_usage.py
```

## [COMPASS] Usage Examples

### MCP Server (for AI Assistants)

```bash
# Start MCP server via stdio (for MCP client integration)
sap-rfc-mcp-server

# The server communicates via stdin/stdout using JSON-RPC protocol
# This is meant to be used by MCP clients (like Claude Desktop, VS Code, etc.)
# For interactive testing, use the HTTP server or PowerShell script instead

# Alternative: Use PowerShell script for stdio mode with better error handling
./tools/start_sap_mcp_server.ps1 -Mode stdio

# Alternative: Direct Python module call
python -m sap_rfc_mcp_server.server
```

### HTTP Server (for Web Applications)

```bash
# Start HTTP server (default port 8000)
sap-rfc-mcp-http-server

# Or use the PowerShell helper script with custom options
./tools/start_sap_mcp_server.ps1 -ServerAddress "127.0.0.1" -Port 8080

# Server available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Python API

```python
from sap_rfc_mcp_server import SAPRFCManager

# Initialize client
client = SAPRFCManager()

# Call RFC function - Note: use keyword arguments directly
result = client.call_rfc_function(
    "RFC_READ_TABLE",
    QUERY_TABLE="T001",
    ROWCOUNT=10
)

print(result)
```

## [SEARCH] Verify Installation

Run these commands to verify everything is working:

### 1. Import Test
```bash
python -c "import sap_rfc_mcp_server; print('[CHECKMARK] Import successful')"
```

### 2. Connection Test
```bash
python examples/basic_usage.py
```

### 3. Run Tests
```bash
pytest tests/ -v
```

## [SHIELD] Security Configuration Details

The SAP Security Manager provides multiple secure methods for storing your SAP credentials:

### Interactive Setup
```bash
# Launch interactive security setup
python -m sap_rfc_mcp_server.sap_security_manager setup
```

This will guide you through:
1. **Connection Method Selection**: Choose your preferred storage method
2. **Credential Input**: Secure entry of SAP connection details
3. **Method Configuration**: Setup method-specific options
4. **Connection Testing**: Validate your configuration with SAP system

### Available Storage Methods

#### 1. Environment Variables (Always Available)
- Direct system environment variables
- Highest security for production systems
- No additional dependencies required

#### 2. .env Files (Simple File-Based)
- Plain text file configuration
- Good for development environments
- Requires `python-dotenv` package

#### 3. System Keyring (OS Credential Manager)
- Uses operating system's credential store
- Windows Credential Manager / macOS Keychain / Linux Secret Service
- Requires `keyring` package

#### 4. Encrypted Files (Password-Protected)
- AES-256 encrypted credential storage
- Password-protected access
- Requires `cryptography` package

### Security Commands

```bash
# Check current configuration status
python -m sap_rfc_mcp_server.sap_security_manager info

# Test SAP connection with validation
python -m sap_rfc_mcp_server.sap_security_manager test

# Migrate between storage methods
python -m sap_rfc_mcp_server.sap_security_manager migrate
```

### Security Best Practices

1. **Use Environment Variables or Encrypted Files** for production
2. **Use System Keyring** for personal development machines
3. **Use .env Files** only for development/testing
4. **Never commit credentials** to version control
5. **Regularly rotate SAP passwords** and update configuration

## [COMPUTER] VS Code Integration (MCP 2025)

### Quick VS Code Setup

```bash
# Automated setup creates proper MCP configuration
python tools/setup_dev.py
```

This creates `.vscode/mcp.json`:
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

### Using SAP MCP in VS Code

1. **Open workspace** with `.vscode/mcp.json`
2. **Enable agent mode** (if using GitHub Copilot)
3. **Ask questions** like:
   - "Get SAP system information"
   - "Search for functions containing 'TABLE'"
   - "Show RFC_READ_TABLE metadata"

**📖 Complete Guide**: [VS Code Integration Guide](docs/VSCODE_INTEGRATION_GUIDE.md)

## [ALERT] Troubleshooting
```

### 4. API Documentation Test
```bash
# Start HTTP server and test API docs
./tools/start_sap_mcp_server.ps1
# Then visit: http://localhost:8000/docs
```

### 5. MCP Server Test (Optional)
```bash
# Test MCP server stdio mode (requires MCP client)
./tools/start_sap_mcp_server.ps1 -Mode stdio
# Server will wait for JSON-RPC messages via stdin
# Press Ctrl+C to exit
# For actual testing, use with MCP clients like Claude Desktop or VS Code
```

## [HELP] Troubleshooting

### Common Issues

#### SAP RFC SDK Not Found
```
Error: RFC SDK not found
```
**Solution**: Install SAP NetWeaver RFC SDK and ensure it's in your PATH.

**Quick check**: Run `python tools/check_sapnwrfc_sdk.py` for detailed validation.

#### Setup Prerequisites Failed
```
Error: SAP NetWeaver RFC SDK prerequisites not met!
```
**Solution**:
- Run `python tools/check_sapnwrfc_sdk.py` for detailed diagnosis
- Ensure SAPNWRFC_HOME environment variable is set
- Add SAP NetWeaver RFC lib directory to PATH
- Download SDK from SAP Support Portal if missing

#### Connection Refused
```
Error: Connection to SAP system failed
```
**Solution**:
- Check your SAP connection parameters using: `python -m sap_rfc_mcp_server.sap_security_manager info`
- Test connection with: `python -m sap_rfc_mcp_server.sap_security_manager test`
- Verify network connectivity to SAP server
- Ensure SAP user has RFC authorization
- Run `python tools/check_config.py` for detailed configuration analysis

#### Import Errors
```
ImportError: No module named 'pyrfc'
```
**Solution**:
- Activate virtual environment
- Reinstall dependencies: `pip install -e .`

#### Unicode/Console Encoding Issues
```
Error: Unicode characters in output
```
**Solution**:
- All scripts now use ASCII-safe output
- Windows console compatibility has been enhanced

#### DATA_BUFFER_EXCEEDED Errors
```
Error: DATA_BUFFER_EXCEEDED when reading large tables
```
**Solution**:
- Use the enhanced table reading tools in `tools/` directory
- The server now includes automatic buffer overflow protection

### Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages in the console output
2. **Verify configuration**: Use `python -m sap_rfc_mcp_server.sap_security_manager info` to check your setup
3. **Test connectivity**: Use `python -m sap_rfc_mcp_server.sap_security_manager test` for connection validation
4. **Check documentation**: See the full documentation in `README.md`
5. **Ask for help**: Open an issue on GitHub

## [PARTY] What's Next?

Once you have the basic setup working:

1. **Explore the MCP Tools**: Try different RFC functions with buffer overflow protection
2. **Check the Metadata Cache**: See how function metadata is cached for performance
3. **Try the HTTP API**: Use the web interface at http://localhost:8000/docs
4. **Use the Tools Directory**: Explore enhanced helper scripts in `tools/`
5. **Test Table Reading**: Try the advanced table reading capabilities
6. **VS Code Integration**: Set up the development environment using `docs/VSCODE_INTEGRATION_GUIDE.md`
7. **Read the Documentation**: Check out the `docs/` folder for detailed guides
8. **Contribute**: See `CONTRIBUTING.md` for how to help improve the project

## [BOOKS] Key Files

- **`.env`**: Your SAP connection configuration
- **`examples/basic_usage.py`**: Simple usage example (recently updated and verified)
- **`tools/`**: Enhanced helper scripts and utilities
- **`tests/`**: Test files to verify functionality
- **`cache/`**: Metadata cache directory
- **`docs/`**: Comprehensive documentation including VS Code integration
- **`README.md`**: Comprehensive documentation

## [STAR] Recent Enhancements (August 2025)

- [CHECKMARK] **Unicode Compatibility**: All scripts now use ASCII-safe output for Windows console
- [CHECKMARK] **Buffer Overflow Protection**: Automatic handling of DATA_BUFFER_EXCEEDED errors
- [CHECKMARK] **Enhanced Table Reading**: Intelligent field selection and iterative reading
- [CHECKMARK] **VS Code Integration**: Complete development environment setup guide
- [CHECKMARK] **Improved Error Handling**: Better diagnostics and user-friendly error messages
- [CHECKMARK] **Tool Organization**: Helper scripts organized in `tools/` directory
- [CHECKMARK] **Fixed Function Calls**: Corrected RFC function call syntax in examples
- [CHECKMARK] **Verified Installation**: All commands and examples tested and working

## [INFO] Verification Status

This QUICKSTART.md has been verified on August 10, 2025 with:
- Python 3.11
- SAP R/3 4.5B system
- Windows PowerShell environment
- All commands tested and confirmed working

Happy coding! [ROCKET]
