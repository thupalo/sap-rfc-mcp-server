#!/usr/bin/env python3
"""Quick test of MCP HTTP API - RFC_SYSTEM_INFO."""

import json

import requests


def test_mcp_api():
    """Test RFC_SYSTEM_INFO via MCP HTTP API."""
    try:
        # Call the MCP tool
        payload = {"name": "rfc_system_info", "arguments": {}}

        response = requests.post(
            "http://127.0.0.1:8000/mcp/call_tool",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        print(f"Request sent to: http://127.0.0.1:8000/mcp/call_tool")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("[OK] MCP RFC_SYSTEM_INFO successful!")

            # Extract result
            if "result" in result and len(result["result"]) > 0:
                result_text = result["result"][0].get("text", "")
                if result_text:
                    system_info = json.loads(result_text)
                    rfcsi = system_info.get("RFCSI_EXPORT", {})
                    print(f"[INFO] System: {rfcsi.get('RFCSYSID', 'N/A')}")
                    print(f"[INFO] Host: {rfcsi.get('RFCHOST', 'N/A')}")
                    print(f"[INFO] Database: {rfcsi.get('RFCDBSYS', 'N/A')}")
                    return True
        else:
            print(f"[ERROR] Failed: {response.text}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")

    return False


if __name__ == "__main__":
    print("[TEST] Testing MCP HTTP API - RFC_SYSTEM_INFO")
    print("=" * 45)
    success = test_mcp_api()
    print("[SUCCESS] Success!" if success else "[ERROR] Failed!")
