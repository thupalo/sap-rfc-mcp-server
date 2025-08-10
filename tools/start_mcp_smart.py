#!/usr/bin/env python3
"""
MCP Server Startup Helper with Automatic Port Management
Automatically finds free ports and starts the MCP HTTP server
"""

import subprocess
import sys
import time
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.port_manager import PortManager


def start_mcp_server_with_port_management():
    """Start MCP HTTP server with automatic port management."""
    print("[LAUNCH] SAP RFC MCP Server - Smart Startup")
    print("=" * 50)

    port_manager = PortManager()
    preferred_ports = [8000, 8001, 8002, 8080, 8081, 8082, 8090, 8091, 8092]

    # Check for existing MCP processes
    print("\n[SEARCH] Checking for existing MCP processes...")
    existing_mcp = port_manager.scan_port_range(8000, 8099)
    mcp_processes = [
        p
        for p in existing_mcp
        if p.get("process_info", {}).get("is_mcp_related", False)
    ]

    if mcp_processes:
        print(f"[WARNING]  Found {len(mcp_processes)} existing MCP processes:")
        for proc_info in mcp_processes:
            port = proc_info["port"]
            pid = proc_info.get("process_info", {}).get("pid", "Unknown")
            print(f"   Port {port}: PID {pid}")

        response = input("\n[REFRESH] Stop existing MCP processes? [Y/n]: ")
        if response.lower() not in ["n", "no"]:
            print("[EMOJI] Stopping existing MCP processes...")
            for proc_info in mcp_processes:
                port = proc_info["port"]
                port_manager.kill_process_on_port(port, force=True)

            # Wait a moment for processes to fully terminate
            time.sleep(2)

    # Find free port
    print("\n[SEARCH] Finding free port...")
    free_port = None

    for port in preferred_ports:
        port_info = port_manager.check_port_status(port)
        if not port_info["in_use"]:
            free_port = port
            break

    if not free_port:
        # Find any free port in range
        for port in range(8000, 8100):
            port_info = port_manager.check_port_status(port)
            if not port_info["in_use"]:
                free_port = port
                break

    if not free_port:
        print("[ERROR] No free ports available in range 8000-8099")
        print("[TIP] Try manually releasing some ports:")
        print("   python tools/port_manager.py --scan 8000 8099")
        return False

    print(f"[OK] Using port {free_port}")

    # Prepare server command
    venv_python = project_root / "venv" / "Scripts" / "python.exe"
    server_cmd = [
        str(venv_python),
        "-m",
        "sap_rfc_mcp_server.http_server",
        "127.0.0.1",
        str(free_port),
    ]

    print(f"\n[LAUNCH] Starting MCP HTTP server on port {free_port}...")
    print(f"Command: {' '.join(server_cmd)}")
    print("\n" + "=" * 50)
    print("Server output:")
    print("=" * 50)

    try:
        # Start the server
        process = subprocess.Popen(
            server_cmd,
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Print server URL
        print(f"\n[TIP] Server should be available at: http://127.0.0.1:{free_port}")
        print(f"[TIP] Test with: curl http://127.0.0.1:{free_port}/mcp/ping")
        print(f"[TIP] Stop with: Ctrl+C")
        print()

        # Stream output
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

        return_code = process.poll()
        print(f"\n[FINISH] Server stopped with exit code: {return_code}")

        return return_code == 0

    except KeyboardInterrupt:
        print(f"\n[EMOJI] Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("[OK] Server stopped")
        return True

    except Exception as e:
        print(f"[ERROR] Error starting server: {e}")
        return False


if __name__ == "__main__":
    success = start_mcp_server_with_port_management()
    sys.exit(0 if success else 1)
