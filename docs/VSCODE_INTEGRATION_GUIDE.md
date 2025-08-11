# SAP RFC MCP Server - VS Code Integration Guide

This guide will help you set up the SAP RFC MCP server as a development tool in VS Code with GitHub Copilot for SAP data retrieval and development assistance.

## [COMPASS] Overview

The SAP RFC MCP server can be integrated with VS Code in several ways:
1. **MCP Client Extension** - Direct integration with GitHub Copilot
2. **HTTP API Integration** - Via REST API calls
3. **Terminal Commands** - Direct command-line usage
4. **Python Development** - Import as a library

## [CHECKLIST] Prerequisites

### [CHECKMARK] Check Current Installation Status

Your SAP RFC MCP server is already installed and working! Let's verify:

```bash
# Check if the server is working
cd <your-projects-root>/sap-rfc-mcp-server
./venv/Scripts/python.exe -m sap_rfc_mcp_server.server --version

# Test HTTP server
./venv/Scripts/python.exe -m sap_rfc_mcp_server.http_server 127.0.0.1 8000
```

### [CHECKMARK] Requirements Met
- [CHECKMARK] Python 3.11+ installed
- [CHECKMARK] SAP RFC SDK configured
- [CHECKMARK] SAP connection working (tested with RFC_SYSTEM_INFO)
- [CHECKMARK] Virtual environment set up
- [CHECKMARK] Dependencies installed

## [WRENCH] Method 1: MCP Client Integration (Recommended)

### Step 1: Install MCP Extension for VS Code

Search for and install the **"Model Context Protocol"** extension in VS Code:

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Model Context Protocol" or "MCP"
4. Install the official MCP extension

### Step 2: Configure MCP Client

Create/edit your VS Code MCP configuration:

**File: `.vscode/settings.json`**
```json
{
  "mcp.servers": {
    "sap-rfc-server": {
      "command": "./venv/Scripts/python.exe",
      "args": ["-m", "sap_rfc_mcp_server.server"],
      "cwd": "./sap-rfc-mcp-server",
      "env": {
        "SAP_RFC_MCP_CONFIG": "./sap-rfc-mcp-server/.env"
      }
    }
  },
  "mcp.trace": "verbose"
}
```

### Step 3: Test MCP Integration

1. Restart VS Code
2. Open Command Palette (Ctrl+Shift+P)
3. Type "MCP: List Available Tools"
4. You should see SAP RFC tools available

## [GLOBE] Method 2: HTTP API Integration

### Step 1: Start HTTP Server

You can use the included PowerShell startup script for easy server management:

**File: `tools/start_sap_mcp_server.ps1`** (already created in your project)
```powershell
# SAP RFC MCP Server Startup Script
param(
    [string]$ServerAddress = "127.0.0.1",
    [int]$Port = 8000,
    [string]$Mode = "http"
)

Write-Host "[ROCKET] Starting SAP RFC MCP Server..." -ForegroundColor Green

$serverPath = "C:/Users/<user>/Documents/Projects/sap-rfc-mcp-server"
$pythonExe = "$serverPath/venv/Scripts/python.exe"

# Change to server directory
Set-Location $serverPath

if ($Mode -eq "stdio") {
    Write-Host "Starting MCP server in stdio mode" -ForegroundColor Yellow
    & $pythonExe -m sap_rfc_mcp_server.server
} else {
    Write-Host "Starting HTTP server on http://$ServerAddress`:$Port" -ForegroundColor Yellow
    & $pythonExe -m sap_rfc_mcp_server.http_server $ServerAddress $Port
}

Write-Host "[CHECKMARK] Server started successfully!" -ForegroundColor Green
Write-Host "[BOOK] API docs available at: http://$ServerAddress`:$Port/docs" -ForegroundColor Cyan
```

To start the server, run:
```powershell
# From project root
.\tools\start_sap_mcp_server.ps1

# Or with custom parameters
.\tools\start_sap_mcp_server.ps1 -ServerAddress "0.0.0.0" -Port 8080
```

### Step 2: Create VS Code Tasks

Add SAP RFC tasks to your VS Code workspace:

**File: `.vscode/tasks.json`**
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start SAP RFC MCP Server",
      "type": "shell",
      "command": "powershell",
      "args": [
        "-ExecutionPolicy", "Bypass",
        "-File", "./tools/start_sap_mcp_server.ps1"
      ],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      },
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "Test SAP Connection",
      "type": "shell",
      "command": "./venv/Scripts/python.exe",
      "args": ["tools/test_direct_sap.py"],
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always"
      }
    },
    {
      "label": "Get RFC System Info",
      "type": "shell",
      "command": "curl",
      "args": [
        "-X", "POST",
        "http://localhost:8000/mcp/call_tool",
        "-H", "Content-Type: application/json",
        "-d", "{\"name\": \"rfc_system_info\", \"arguments\": {}}"
      ],
      "group": "test",
      "dependsOn": "Start SAP RFC MCP Server"
    }
  ]
}
```

## [SNAKE] Method 3: Python Development Integration

### Step 1: Use Development Helper Module

Your project already includes a development helper module at `tools/sap_dev_helper.py`. This module provides quick access to SAP RFC functions and metadata with ASCII-safe console output.

**Key Features of `tools/sap_dev_helper.py`:**
- Quick SAP system information
- RFC function search and metadata
- Table data retrieval with buffer overflow protection
- Console-safe ASCII output (no Unicode encoding issues)
- VS Code integration-ready

**Usage Examples:**
```python
# Run the helper directly
python tools/sap_dev_helper.py

# Or import in your Python scripts
import sys
sys.path.append('./tools')
from sap_dev_helper import SAPDevHelper

helper = SAPDevHelper()
system_info = helper.get_system_info()
print(f"Connected to SAP {system_info.get('system', 'Unknown')}")
```
### Step 2: Configure Python Path in VS Code

**File: `.vscode/settings.json` (add to existing)**
```json
{
  "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.autoComplete.extraPaths": [
    "./",
    "./sap_rfc_mcp_server",
    "./tools"
  ]
}
```

## [WRENCH] Method 4: VS Code Snippets for SAP Development

Create custom snippets for common SAP operations:

**File: `.vscode/python.json`**
```json
{
  "SAP System Info": {
    "prefix": "sap-info",
    "body": [
      "# Get SAP system information",
      "import sys",
      "sys.path.append('./tools')",
      "from sap_dev_helper import SAPDevHelper",
      "helper = SAPDevHelper()",
      "system_info = helper.get_system_info()",
      "print(f\"SAP System: {system_info.get('system', 'Unknown')}\")",
      "print(f\"Host: {system_info.get('host', 'Unknown')}\")",
      "print(f\"Database: {system_info.get('database', 'Unknown')}\")"
    ],
    "description": "Get SAP system information"
  },
  "SAP RFC Function Call": {
    "prefix": "sap-rfc",
    "body": [
      "# Call SAP RFC function",
      "import sys",
      "sys.path.append('./tools')",
      "from sap_dev_helper import SAPDevHelper",
      "helper = SAPDevHelper()",
      "result = helper.sap_client.call_rfc_function(",
      "    function_name=\"${1:RFC_FUNCTION_NAME}\",",
      "    parameters={",
      "        \"${2:PARAMETER_NAME}\": \"${3:value}\"",
      "    }",
      ")",
      "print(result)"
    ],
    "description": "Call SAP RFC function"
  },
  "SAP Table Data": {
    "prefix": "sap-table",
    "body": [
      "# Get SAP table data",
      "import sys",
      "sys.path.append('./tools')",
      "from sap_dev_helper import SAPDevHelper",
      "helper = SAPDevHelper()",
      "data = helper.get_table_data(\"${1:TABLE_NAME}\", max_rows=${2:10})",
      "print(f\"Retrieved {data.get('row_count', 0)} rows\")",
      "for row in data.get('data', [])[:5]:  # Show first 5 rows",
      "    print(row)"
    ],
    "description": "Get SAP table data"
  },
  "SAP Function Search": {
    "prefix": "sap-search",
    "body": [
      "# Search SAP RFC functions",
      "import sys",
      "sys.path.append('./tools')",
      "from sap_dev_helper import SAPDevHelper",
      "helper = SAPDevHelper()",
      "functions = helper.search_functions(\"${1:keyword}\")",
      "for func in functions:",
      "    print(f\"{func.get('FUNCNAME', 'Unknown')}: {func.get('STEXT', 'No description')}\")"
    ],
    "description": "Search SAP RFC functions"
  }
  }
}
```

## [ROCKET] Quick Start Commands

### Terminal Commands (VS Code Integrated Terminal)

```bash
# Activate environment
./venv/Scripts/Activate.ps1

# Start HTTP server using helper script
./tools/start_sap_mcp_server.ps1

# Test connection
python tools/test_direct_sap.py

# Get system info via API
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{"name": "rfc_system_info", "arguments": {}}'

# Search functions via API
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{"name": "get_rfc_functions", "arguments": {"funcs_mask": "*SYSTEM*"}}'
```

### Python Console Commands

```python
# Quick setup in VS Code Python console
import sys
sys.path.append('./tools')
exec(open('tools/sap_dev_helper.py').read())

# Get system info (using the helper instance)
helper = SAPDevHelper()
helper.get_system_info()

# Search functions
helper.search_functions("TABLE")

# Get function metadata
helper.get_function_metadata("RFC_READ_TABLE")

# Get table data
helper.get_table_data("T001", 5)
```

## [BOOKS] Usage Examples

### Example 1: Get SAP System Information
```python
import sys
sys.path.append('./tools')
from sap_dev_helper import SAPDevHelper

# Get system info
helper = SAPDevHelper()
info = helper.get_system_info()
print(f"Connected to SAP {info.get('system', 'Unknown')} on {info.get('host', 'Unknown')}")
```

### Example 2: Search and Explore Functions
```python
# Search for table-related functions
functions = helper.search_functions("TABLE")
for func in functions[:5]:
    print(f"Function: {func.get('FUNCNAME', 'Unknown')}")

    # Get detailed metadata
    metadata = helper.get_function_metadata(func['FUNCNAME'])
    if 'error' not in metadata:
        print(f"  Inputs: {len(metadata.get('inputs', []))}")
        print(f"  Outputs: {len(metadata.get('outputs', []))}")
        print(f"  Description: {metadata.get('_metadata', {}).get('description', 'No description')}")
```

### Example 3: Retrieve and Analyze SAP Data
```python
# Get company codes using the enhanced table reader
companies = helper.get_table_data("T001", 20)
print(f"Found {companies.get('row_count', 0)} company codes")

# Get user data with specific fields
users = helper.get_table_data("USR02", 10, fields=["BNAME", "CLASS", "TRDAT"])
for user in users.get('data', []):
    print(f"User: {user}")
```

## [WRENCH] Troubleshooting

### Common Issues and Solutions

1. **MCP Server not starting**
   ```bash
   # Check Python path
   which python

   # Verify virtual environment
   ./venv/Scripts/Activate.ps1
   python --version
   ```

2. **SAP connection issues**
   ```bash
   # Test direct connection
   python tools/test_direct_sap.py

   # Check environment variables
   cat .env
   ```

3. **VS Code not recognizing MCP server**
   - Restart VS Code after configuration changes
   - Check `.vscode/settings.json` syntax
   - Verify file paths are correct

### Performance Tips

1. **Use metadata caching** - Functions are cached automatically
2. **Start HTTP server once** - Keep it running for multiple requests
3. **Use bulk operations** - For multiple function metadata requests

## [PARTY] Success Verification

After setup, you should be able to:

[CHECKMARK] **VS Code Integration**
- Run SAP RFC commands from VS Code terminal
- Use Python snippets for SAP operations
- Access SAP data through integrated console

[CHECKMARK] **GitHub Copilot Enhancement**
- Copilot can suggest SAP-specific code
- Access to SAP function metadata
- Intelligent SAP data retrieval suggestions

[CHECKMARK] **Development Productivity**
- Quick SAP system information
- Fast RFC function discovery
- Efficient metadata exploration
- Streamlined data retrieval with buffer overflow protection

[ROCKET] **Your SAP RFC MCP server is now ready for development use in VS Code!**
