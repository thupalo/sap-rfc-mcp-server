# Tools Directory

This directory contains development tools and utilities for the SAP RFC MCP Server project.

## Available Tools

### [ROCKET] Server Management
- **`start_mcp_smart.py`** - Intelligent MCP server startup with automatic port management
- **`port_manager.py`** - Port management utility for checking, scanning, and releasing ports
- **`manage_mcp_ports.ps1`** - PowerShell wrapper for port management operations
- **`start_sap_mcp_server.ps1`** - Alternative PowerShell-based server startup script

### [WRENCH] Development Utilities
- **`sap_dev_helper.py`** - VS Code development helper with SAP connection utilities
- **`setup_dev.py`** - Automated development environment setup
- **`check_config.py`** - SAP configuration analysis and troubleshooting utility
- **`check_sapnwrfc_sdk.py`** - SAP NetWeaver RFC SDK installation validation

### [TEST] Testing and Verification
- **`test_table_access_verification.py`** - Comprehensive SAP table access testing
- **`test_direct_sap.py`** - Direct SAP RFC connection testing with RFC_SYSTEM_INFO validation
- **`test_metadata_performance_http_stdio.py`** - Performance testing for metadata caching (HTTP & STDIO)
- **`test_metadata_stdio.py`** - STDIO-only RFC function metadata testing
- **`test_mcp_http_quick.py`** - Quick MCP HTTP API test with RFC_SYSTEM_INFO
- **`test_vscode_integration.py`** - VS Code development helper testing with SAPDevHelper class

## Usage Examples

### Port Management
```bash
# Check if a port is available
python tools/port_manager.py --check 8000

# Scan for busy ports in range
python tools/port_manager.py --scan 8000 8010

# Suggest a free port
python tools/port_manager.py --suggest

# Release MCP processes
python tools/port_manager.py --release-mcp 8000 8020
```

### PowerShell Port Management
```powershell
# Check port status
.\tools\manage_mcp_ports.ps1 check -Port 8000

# Start server with smart port management
.\tools\manage_mcp_ports.ps1 start

# Clean up MCP processes
.\tools\manage_mcp_ports.ps1 cleanup -StartPort 8000 -EndPort 8020
```

### Smart Server Startup
```bash
# Start with automatic port management and conflict resolution
python tools/start_mcp_smart.py

# Alternative PowerShell startup
.\tools\start_sap_mcp_server.ps1 -Mode http -Port 8000
```

### Development Helper
```bash
# Get SAP system information
python tools/sap_dev_helper.py --system-info

# Get table structure
python tools/sap_dev_helper.py --table-structure T000

# Test table access
python tools/sap_dev_helper.py --test-table T000

# Search function modules
python tools/sap_dev_helper.py --search-functions RFC_READ
```

### Environment Setup
```bash
# Set up development environment
python tools/setup_dev.py
```

### Configuration Analysis
```bash
# Analyze current SAP configuration
python tools/check_config.py

# Check SAP NetWeaver RFC SDK installation
python tools/check_sapnwrfc_sdk.py
```

### Testing and Verification
```bash
# Run comprehensive table access tests
python tools/test_table_access_verification.py

# Test direct SAP RFC connection with system info
python tools/test_direct_sap.py

# Test metadata caching performance (HTTP & STDIO)
python tools/test_metadata_performance_http_stdio.py

# Test STDIO-only RFC function metadata
python tools/test_metadata_stdio.py

# Quick MCP HTTP API test
python tools/test_mcp_http_quick.py

# Test VS Code development helper functionality
python tools/test_vscode_integration.py
```

## Tool Features

### Port Management
- [CHECKMARK] Automatic port conflict detection
- [CHECKMARK] MCP process identification
- [CHECKMARK] Graceful process termination
- [CHECKMARK] Free port suggestions
- [CHECKMARK] Cross-platform compatibility

### Development Support
- [CHECKMARK] SAP connection testing
- [CHECKMARK] Table access verification
- [CHECKMARK] Function module discovery
- [CHECKMARK] Metadata cache management
- [CHECKMARK] VS Code integration helpers
- [CHECKMARK] Configuration analysis and troubleshooting
- [CHECKMARK] Direct RFC connection validation with system information
- [CHECKMARK] Performance testing for metadata caching effectiveness
- [CHECKMARK] Quick MCP HTTP API validation
- [CHECKMARK] SAP NetWeaver RFC SDK installation validation

### Server Management
- [CHECKMARK] Intelligent startup with port management
- [CHECKMARK] Background process monitoring
- [CHECKMARK] Automatic conflict resolution
- [CHECKMARK] Multiple startup modes (HTTP/STDIO)

## Dependencies

All tools use the main project dependencies and should be run from the activated virtual environment:

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run any tool
python tools/<tool_name>.py [options]
```
