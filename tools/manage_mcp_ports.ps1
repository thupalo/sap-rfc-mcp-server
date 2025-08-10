# SAP RFC MCP Server - Port Management PowerShell Wrapper
# Usage: .\manage_mcp_ports.ps1 [action] [parameters]

param(
    [string]$Action = "help",
    [int]$Port = 0,
    [int]$StartPort = 8000,
    [int]$EndPort = 8010,
    [switch]$Force
)

# Set up paths
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$PortManager = Join-Path $PSScriptRoot "port_manager.py"
$SmartStart = Join-Path $PSScriptRoot "start_mcp_smart.py"

# Activate virtual environment
$ActivateScript = Join-Path $ProjectRoot "venv\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Virtual environment not found at: $ActivateScript" -ForegroundColor Red
    exit 1
}

function Show-Help {
    Write-Host "SAP RFC MCP Server - Port Management" -ForegroundColor Cyan
    Write-Host "====================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\manage_mcp_ports.ps1 check -Port 8000" -ForegroundColor White
    Write-Host "  .\manage_mcp_ports.ps1 scan -StartPort 8000 -EndPort 8010" -ForegroundColor White
    Write-Host "  .\manage_mcp_ports.ps1 kill -Port 8000" -ForegroundColor White
    Write-Host "  .\manage_mcp_ports.ps1 cleanup -StartPort 8000 -EndPort 8020" -ForegroundColor White
    Write-Host "  .\manage_mcp_ports.ps1 suggest" -ForegroundColor White
    Write-Host "  .\manage_mcp_ports.ps1 start" -ForegroundColor White
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  check    - Check specific port status" -ForegroundColor White
    Write-Host "  scan     - Scan port range for busy ports" -ForegroundColor White
    Write-Host "  kill     - Kill process on specific port" -ForegroundColor White
    Write-Host "  cleanup  - Release all MCP processes in range" -ForegroundColor White
    Write-Host "  suggest  - Suggest free port for MCP server" -ForegroundColor White
    Write-Host "  start    - Smart start with automatic port management" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Force   - Force operations without confirmation" -ForegroundColor White
}

function Invoke-PortManager {
    param($Arguments)

    $Command = @($VenvPython, $PortManager) + $Arguments
    Write-Host "Executing: $($Command -join ' ')" -ForegroundColor Gray
    & $Command[0] $Command[1..($Command.Length-1)]
}

# Main logic
switch ($Action.ToLower()) {
    "check" {
        if ($Port -eq 0) {
            Write-Host "Port parameter required for check action" -ForegroundColor Red
            exit 1
        }
        Invoke-PortManager @("--check", $Port)
    }

    "scan" {
        Invoke-PortManager @("--scan", $StartPort, $EndPort)
    }

    "kill" {
        if ($Port -eq 0) {
            Write-Host "Port parameter required for kill action" -ForegroundColor Red
            exit 1
        }
        $CmdArgs = @("--kill", $Port)
        if ($Force) { $CmdArgs += "--force" }
        Invoke-PortManager $CmdArgs
    }

    "cleanup" {
        $CmdArgs = @("--release-mcp", $StartPort, $EndPort)
        if ($Force) { $CmdArgs += "--force" }
        Invoke-PortManager $CmdArgs
    }

    "suggest" {
        Invoke-PortManager @("--suggest")
    }

    "start" {
        Write-Host "Starting MCP server with smart port management..." -ForegroundColor Green
        & $VenvPython $SmartStart
    }

    "help" {
        Show-Help
    }

    default {
        Write-Host "Unknown action: $Action" -ForegroundColor Red
        Show-Help
        exit 1
    }
}

Write-Host "Operation completed" -ForegroundColor Green
