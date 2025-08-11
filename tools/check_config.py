#!/usr/bin/env python3
"""
Check current SAP configuration
"""

import os
import sys

# Better approach for tools scripts - try direct import first
try:
    from sap_rfc_mcp_server.config import SAPConfig
except ImportError:
    # If direct import fails, add parent directory to path
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

    # Show connection parameters that will be used
    print("\n[INFO] Connection Parameters:")
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
