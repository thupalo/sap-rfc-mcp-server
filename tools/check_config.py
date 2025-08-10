#!/usr/bin/env python3
"""
Check current SAP configuration
"""

import os
import sys

# Add parent directory to path since we're in tools folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sap_rfc_mcp_server.config import SAPConfig

print("[CONFIG] Current SAP Configuration Analysis")
print("=" * 45)

try:
    config = SAPConfig.from_env()
    print(f"Host (ASHOST):     {config.ashost}")
    print(f"System Nr (SYSNR): {config.sysnr}")
    print(f"Client (MANDT):    {config.client}")
    print(f"User:              {config.user}")

    print("-" * 35)

    expected_client = "005"
    actual_client = config.client

    print(f"Expected Client: {expected_client}")
    print(f"Actual Client:   {actual_client}")

    if actual_client != expected_client:
        print(f"\n[ERROR] CLIENT MISMATCH DETECTED!")
        print(f"Currently connected to client {actual_client}")
        print(f"\n[CONFIG] Solution:")
        print(f"1. Update .env file: SAP_CLIENT={expected_client}")
        print(f"2. Restart SAP RFC MCP Server")
        print(f"3. Verify table access")

        print(f"\n[NOTE] Required .env change:")
        print(f"   Change: SAP_CLIENT={actual_client}")
        print(f"   To:     SAP_CLIENT={expected_client}")
    else:
        print(f"\n[OK] Client configuration is correct")
        print(f"Table access issue may be due to authorization")

    # Show connection parameters that will be used
    print(f"\n[INFO] Connection Parameters:")
    print("-" * 25)
    conn_params = config.to_connection_params()
    for key, value in conn_params.items():
        if "passwd" in key.lower():
            print(f"{key}: ***MASKED***")
        else:
            print(f"{key}: {value}")

except Exception as e:
    print(f"[ERROR] Error reading config: {e}")
    import traceback

    traceback.print_exc()
