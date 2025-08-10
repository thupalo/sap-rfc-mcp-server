#!/usr/bin/env python3
"""
Test RFC Function Metadata via STDIO MCP Server
Test getting metadata for RFC_SYSTEM_INFO function
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path


async def test_stdio_metadata():
    """Test getting RFC function metadata via STDIO MCP server"""
    print("[TEST] Testing STDIO MCP Server - RFC Function Metadata")
    print("=" * 55)

    try:
        # Get project root and Python executable path
        project_root = Path(__file__).parent.parent
        python_exe = project_root / "venv" / "Scripts" / "python.exe"
        server_module = "sap_rfc_mcp_server.server"

        # Start the STDIO server process
        process = await asyncio.create_subprocess_exec(
            str(python_exe),
            "-m",
            server_module,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(project_root),
        )

        print("[INFO] STDIO MCP Server started...")

        # Test 1: Initialize the session
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}, "sampling": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        print("[SEND] Sending initialize request...")
        init_message = json.dumps(init_request) + "\n"
        process.stdin.write(init_message.encode())
        await process.stdin.drain()

        # Read initialization response
        init_response_line = await process.stdout.readline()
        init_response = json.loads(init_response_line.decode().strip())
        print(
            f"[OK] Initialize response: {init_response.get('result', {}).get('protocolVersion', 'OK')}"
        )

        # Check for any errors during initialization
        if "error" in init_response:
            print(f"[ERROR] Initialization error: {init_response['error']}")
            return False

        # Send initialized notification (required by MCP protocol)
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }

        print("[SEND] Sending initialized notification...")
        init_notif_message = json.dumps(initialized_notification) + "\n"
        process.stdin.write(init_notif_message.encode())
        await process.stdin.drain()

        # Test 2: List available tools
        list_tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

        print("[SEND] Requesting available tools...")
        list_message = json.dumps(list_tools_request) + "\n"
        process.stdin.write(list_message.encode())
        await process.stdin.drain()

        # Read tools list response
        tools_response_line = await process.stdout.readline()
        tools_response = json.loads(tools_response_line.decode().strip())

        # Check for errors in tools list
        if "error" in tools_response:
            print(f"[ERROR] Tools list error: {tools_response['error']}")
            return False

        tools = tools_response.get("result", {}).get("tools", [])

        print(f"[LIST] Available tools: {len(tools)} found")
        for tool in tools:
            print(
                f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}"
            )

        # If no tools available, check stderr for errors
        if len(tools) == 0:
            print("[WARN] No tools available. Checking server stderr...")

            # Try to read any stderr output
            try:
                stderr_data = await asyncio.wait_for(
                    process.stderr.read(1024), timeout=1.0
                )
                if stderr_data:
                    stderr_text = stderr_data.decode().strip()
                    print(f"[DEBUG] Server stderr: {stderr_text}")
            except asyncio.TimeoutError:
                print("[DEBUG] No stderr output within timeout")

            print("[SKIP] Skipping metadata test due to no available tools")
            process.stdin.close()
            await process.wait()
            return False

        # Test 3: Get RFC function metadata
        metadata_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_function_metadata",
                "arguments": {"function_name": "RFC_SYSTEM_INFO"},
            },
        }

        print("\n[GET] Requesting RFC_SYSTEM_INFO metadata...")
        metadata_message = json.dumps(metadata_request) + "\n"
        process.stdin.write(metadata_message.encode())
        await process.stdin.drain()

        # Read metadata response
        metadata_response_line = await process.stdout.readline()
        metadata_response = json.loads(metadata_response_line.decode().strip())

        if metadata_response.get("result"):
            result = metadata_response["result"]
            print("[OK] RFC Metadata retrieved successfully!")

            # Parse the content
            content = result.get("content", [])
            if content and content[0].get("type") == "text":
                metadata_text = content[0].get("text", "")
                print("\n[DATA] RFC_SYSTEM_INFO Metadata:")
                print("-" * 40)
                print(metadata_text)

                # Extract key information
                if "RFCSI_EXPORT" in metadata_text:
                    print("\n[INFO] Key Export Parameters Found:")
                    lines = metadata_text.split("\n")
                    for line in lines:
                        if "RFCSI_EXPORT" in line or any(
                            param in line
                            for param in ["RFCSYSID", "RFCHOST", "RFCDEST"]
                        ):
                            print(f"   {line.strip()}")
            else:
                print("[ERROR] Unexpected response format")
        else:
            print(
                f"[ERROR] Error getting metadata: {metadata_response.get('error', 'Unknown error')}"
            )

        # Clean shutdown
        process.stdin.close()
        await process.wait()

        print("\n[SUCCESS] STDIO metadata test completed!")
        return True

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        if "process" in locals():
            process.terminate()
            await process.wait()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_stdio_metadata())
    sys.exit(0 if success else 1)
