# PowerShell script to start SAP RFC MCP Server with enhanced error handling
param(
    [string]$Mode = "http",
    [string]$ServerAddress = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$Help
)

if ($Help) {
    Write-Host "SAP RFC MCP Server Startup Script" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\start_sap_mcp_server.ps1 [-Mode <stdio|http>] [-ServerAddress <host>] [-Port <port>]" -ForegroundColor White
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Yellow
    Write-Host "  -Mode           Server mode: 'stdio' or 'http' (default: http)" -ForegroundColor White
    Write-Host "  -ServerAddress  Host address for HTTP mode (default: 127.0.0.1)" -ForegroundColor White
    Write-Host "  -Port           Port for HTTP mode (default: 8000)" -ForegroundColor White
    Write-Host "  -Help        Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\start_sap_mcp_server.ps1                           # HTTP mode on 127.0.0.1:8000" -ForegroundColor White
    Write-Host "  .\start_sap_mcp_server.ps1 -Mode stdio               # STDIO mode" -ForegroundColor White
    Write-Host "  .\start_sap_mcp_server.ps1 -Port 8080                # HTTP mode on port 8080" -ForegroundColor White
    exit 0
}

# Set up paths
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$ActivateScript = Join-Path $ProjectRoot "venv\Scripts\Activate.ps1"

Write-Host "SAP RFC MCP Server Startup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
Write-Host "Mode: $Mode" -ForegroundColor Gray

# Check if virtual environment exists
if (-not (Test-Path $ActivateScript)) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Expected location: $ActivateScript" -ForegroundColor Red
    Write-Host ""
    Write-Host "To set up the development environment:" -ForegroundColor Yellow
    Write-Host "   python tools/setup_dev.py" -ForegroundColor White
    exit 1
}

# No need to activate virtual environment; will use venv Python executable directly
Write-Host "Using virtual environment Python executable..." -ForegroundColor Green

# Check if Python executable exists
if (-not (Test-Path $VenvPython)) {
    Write-Host "Python executable not found: $VenvPython" -ForegroundColor Red
    exit 1
}

# Change to project directory
Set-Location $ProjectRoot

# Start server based on mode
try {
    switch ($Mode.ToLower()) {
        "stdio" {
            Write-Host "Starting SAP RFC MCP Server in STDIO mode..." -ForegroundColor Green
            & $VenvPython -m sap_rfc_mcp_server.server
        }
        "http" {
            Write-Host "Starting SAP RFC MCP Server in HTTP mode..." -ForegroundColor Green
            Write-Host "   Host: $ServerAddress" -ForegroundColor Gray
            Write-Host "   Port: $Port" -ForegroundColor Gray
            & $VenvPython -m sap_rfc_mcp_server.http_server $ServerAddress $Port
        }
        default {
            Write-Host "Invalid mode: $Mode" -ForegroundColor Red
            Write-Host "Valid modes: stdio, http" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "Failed to start server: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Check SAP connection configuration in .env file" -ForegroundColor White
    Write-Host "2. Verify SAP RFC SDK is installed" -ForegroundColor White
    Write-Host "3. Check if port $Port is available (for HTTP mode)" -ForegroundColor White
    Write-Host "4. Use port management tools: python tools/port_manager.py --help" -ForegroundColor White
    exit 1
}
