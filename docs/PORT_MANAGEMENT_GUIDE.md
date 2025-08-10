# SAP RFC MCP Server - Port Management System

## Overview

The port management system provides comprehensive tools to handle port conflicts and manage MCP HTTP server instances efficiently. This addresses common issues when starting the MCP server due to ports already being in use.

## Components

### 1. Port Manager (`port_manager.py`)
**Core Python utility for port management operations.**

#### Features
- **Port Status Checking**: Detailed port usage analysis
- **Process Information**: Complete process details including PID, command line, CPU/memory usage
- **MCP Process Detection**: Automatically identifies MCP-related processes
- **Graceful Process Termination**: Safe process cleanup with fallback to force kill
- **Port Range Scanning**: Bulk port analysis across ranges
- **Smart Port Suggestions**: Recommends free ports for server startup

#### Usage Examples
```bash
# Check specific port
python port_manager.py --check 8000

# Scan port range
python port_manager.py --scan 8000 8010

# Kill process on port
python port_manager.py --kill 8000

# Clean up all MCP processes
python port_manager.py --release-mcp 8000 8020 --force

# Get port suggestion
python port_manager.py --suggest
```

### 2. Smart Startup (`start_mcp_smart.py`)
**Automated MCP server startup with intelligent port management.**

#### Features
- **Automatic Port Detection**: Finds free ports automatically
- **Existing Process Cleanup**: Optionally stops conflicting MCP processes
- **Preferred Port List**: Uses predefined preferred ports (8000, 8001, 8002, 8080, etc.)
- **Fallback Port Discovery**: Searches for any available port in range 8000-8099
- **Real-time Output**: Streams server output with proper formatting

#### Usage
```bash
python start_mcp_smart.py
```

### 3. PowerShell Wrapper (`manage_mcp_ports.ps1`)
**Windows-friendly interface for port management operations.**

#### Features
- **Native PowerShell Interface**: Windows-optimized commands
- **Virtual Environment Management**: Automatic venv activation
- **Parameter Validation**: Type-safe parameter handling
- **Colored Output**: Enhanced readability with color coding
- **Help System**: Built-in documentation

#### Usage Examples
```powershell
# Check port status
.\manage_mcp_ports.ps1 check -Port 8000

# Scan port range
.\manage_mcp_ports.ps1 scan -StartPort 8000 -EndPort 8010

# Kill process on port
.\manage_mcp_ports.ps1 kill -Port 8000 -Force

# Clean up MCP processes
.\manage_mcp_ports.ps1 cleanup -StartPort 8000 -EndPort 8020

# Get port suggestion
.\manage_mcp_ports.ps1 suggest

# Smart startup
.\manage_mcp_ports.ps1 start
```

## Key Features

### 🔍 Intelligent Process Detection
- Automatically identifies MCP-related processes by analyzing:
  - Process command lines for MCP keywords
  - Process names and executables
  - Port usage patterns

### 🛡️ Safe Process Management
- **Graceful Termination**: Always attempts SIGTERM first
- **Force Kill Fallback**: Uses SIGKILL only if graceful termination fails
- **Confirmation Prompts**: Asks for confirmation before killing non-MCP processes
- **Access Control**: Handles permission issues gracefully

### 📊 Comprehensive Port Analysis
- **Port Binding Status**: Tests actual port availability
- **Connection Details**: Shows local/remote addresses and connection states
- **Resource Usage**: Displays CPU and memory consumption
- **Process Hierarchy**: Identifies parent/child relationships

### 🚀 Smart Server Startup
- **Conflict Resolution**: Automatically resolves port conflicts
- **Port Preferences**: Uses optimal ports when available
- **Error Recovery**: Handles startup failures gracefully
- **Output Streaming**: Real-time server log display

## Common Use Cases

### 1. Startup Port Conflicts
**Problem**: MCP server fails to start due to port already in use
**Solution**:
```bash
python start_mcp_smart.py
```
Automatically finds free port and starts server.

### 2. Multiple Server Instances
**Problem**: Multiple MCP servers running, causing confusion
**Solution**:
```bash
python port_manager.py --release-mcp 8000 8020 --force
```
Cleans up all MCP processes in range.

### 3. Port Investigation
**Problem**: Unknown process using desired port
**Solution**:
```bash
python port_manager.py --check 8000
```
Shows detailed process information.

### 4. Development Environment Cleanup
**Problem**: Multiple test servers left running
**Solution**:
```powershell
.\manage_mcp_ports.ps1 scan -StartPort 8000 -EndPort 8099
.\manage_mcp_ports.ps1 cleanup -StartPort 8000 -EndPort 8099
```
Identifies and cleans up all MCP processes.

## Technical Details

### Dependencies
- **psutil**: Process and system information
- **socket**: Port binding tests
- **subprocess**: Process management
- **pathlib**: Path handling
- **argparse**: Command-line interface

### Supported Platforms
- **Windows**: Full support with PowerShell integration
- **Linux**: Core functionality (command-line tools)
- **macOS**: Core functionality (command-line tools)

### MCP Process Detection Keywords
The system identifies MCP processes using these keywords:
- `sap_rfc_mcp_server`
- `http_server`
- `uvicorn`
- `fastapi`
- `mcp`

### Port Range Defaults
- **Preferred Ports**: 8000, 8001, 8002, 8080, 8081, 8082, 8090, 8091, 8092
- **Scan Range**: 8000-8099 (adjustable)
- **Default Suggestion**: First available in preferred list

## Error Handling

### Access Denied Errors
- **Cause**: Insufficient permissions to manage processes
- **Solution**: Run as administrator or use sudo
- **Detection**: Automatic detection and user notification

### Port Still in Use
- **Cause**: Process didn't terminate properly
- **Solution**: Force kill with confirmation
- **Recovery**: Automatic retry with different approach

### Network Permission Issues
- **Cause**: Limited network access rights
- **Solution**: Graceful degradation with available information
- **Notification**: Clear error messages to user

## Installation

### Prerequisites
```bash
pip install psutil
```

### File Setup
Ensure these files are in your project directory:
- `port_manager.py`
- `start_mcp_smart.py`
- `manage_mcp_ports.ps1`

### Permissions (Windows)
For PowerShell execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Best Practices

### 1. Regular Cleanup
Run port cleanup regularly during development:
```bash
python port_manager.py --release-mcp 8000 8099 --force
```

### 2. Use Smart Startup
Always use smart startup for development:
```bash
python start_mcp_smart.py
```

### 3. Check Before Manual Start
Verify port availability before manual server start:
```bash
python port_manager.py --suggest
```

### 4. Monitor Resource Usage
Regular monitoring during development:
```bash
python port_manager.py --scan 8000 8010
```

## Troubleshooting

### Issue: "Access Denied" when killing processes
**Solution**: Run with administrator privileges:
```powershell
# PowerShell as Administrator
.\manage_mcp_ports.ps1 cleanup -StartPort 8000 -EndPort 8020 -Force
```

### Issue: Port still shows as busy after cleanup
**Solution**: Wait and retry, or check for zombie processes:
```bash
python port_manager.py --check 8000
# Wait 5 seconds
python port_manager.py --check 8000
```

### Issue: Smart startup can't find free ports
**Solution**: Expand port range or clean up existing processes:
```bash
python port_manager.py --scan 8000 8099
python port_manager.py --release-mcp 8000 8099 --force
```

### Issue: PowerShell script execution policy error
**Solution**: Allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

## Integration with MCP Server

The port management system integrates seamlessly with the SAP RFC MCP server:

### Startup Integration
```bash
# Instead of manual port management:
python -m sap_rfc_mcp_server.http_server 127.0.0.1 8000

# Use smart startup:
python start_mcp_smart.py
```

### Development Workflow
1. **Cleanup**: `python port_manager.py --release-mcp 8000 8020 --force`
2. **Start**: `python start_mcp_smart.py`
3. **Monitor**: `python port_manager.py --scan 8000 8010`
4. **Stop**: Ctrl+C (graceful) or port cleanup (force)

### Production Deployment
```bash
# Check environment
python port_manager.py --scan 8000 8010

# Get recommended port
RECOMMENDED_PORT=$(python port_manager.py --suggest | grep -o '[0-9]\+')

# Start server
python -m sap_rfc_mcp_server.http_server 127.0.0.1 $RECOMMENDED_PORT
```

This port management system eliminates common startup issues and provides robust tools for managing MCP server instances efficiently.
