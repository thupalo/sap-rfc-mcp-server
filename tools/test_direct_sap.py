#!/usr/bin/env python3
"""Direct test of SAP RFC connection and RFC_SYSTEM_INFO function."""

import json
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from sap_rfc_mcp_server.sap_client import SAPConnectionError, SAPRFCManager

    print("[OK] Successfully imported SAPRFCManager")
except ImportError as e:
    print(f"[ERROR] Failed to import SAPRFCManager: {e}")
    sys.exit(1)


def test_direct_sap_connection():
    """Test direct SAP connection and RFC_SYSTEM_INFO call."""
    print("[TEST] Testing Direct SAP RFC Connection - RFC_SYSTEM_INFO")
    print("=" * 60)

    try:
        # Initialize SAP client
        print("\n[1] Initializing SAP RFC Manager...")
        sap_client = SAPRFCManager()
        print("[OK] SAPRFCManager initialized successfully")

        # Test SAP connection with RFC_SYSTEM_INFO
        print("\n[2] Calling RFC_SYSTEM_INFO...")
        result = sap_client.get_system_info()
        print("[OK] RFC_SYSTEM_INFO call successful!")

        # Display system information
        print("\n[DATA] SAP System Information:")
        print("-" * 40)

        if "RFCSI_EXPORT" in result:
            rfcsi_export = result["RFCSI_EXPORT"]
            print(f"[INFO] System ID: {rfcsi_export.get('RFCSYSID', 'N/A')}")
            print(f"[INFO] Host: {rfcsi_export.get('RFCHOST', 'N/A')}")
            print(f"[INFO] System Number: {rfcsi_export.get('RFCSYSNR', 'N/A')}")
            print(f"[INFO] Client: {rfcsi_export.get('RFCMANDT', 'N/A')}")
            print(f"[INFO] Database: {rfcsi_export.get('RFCDBSYS', 'N/A')}")
            print(f"[INFO] Release: {rfcsi_export.get('RFCRELEASE', 'N/A')}")
            print(f"[INFO] Platform: {rfcsi_export.get('RFCOPSYS', 'N/A')}")
            print(f"[INFO] Protocol: {rfcsi_export.get('RFCPROTO', 'N/A')}")
            print(f"[INFO] Machine Type: {rfcsi_export.get('RFCMACH', 'N/A')}")
            print(f"[INFO] Date: {rfcsi_export.get('RFCDATE1', 'N/A')}")
            print(f"[INFO] Time: {rfcsi_export.get('RFCTIME1', 'N/A')}")

        print(f"\n[DATA] Full Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Test a simple RFC function call
        print("\n[3] Testing direct RFC function call...")
        rfc_result = sap_client.call_rfc_function("RFC_SYSTEM_INFO")
        print("[OK] Direct RFC_SYSTEM_INFO call successful!")
        print(f"Direct call result keys: {list(rfc_result.keys())}")

        return True

    except SAPConnectionError as e:
        print(f"[ERROR] SAP Connection Error: {e}")
        print("\n[CONFIG] Troubleshooting:")
        print("1. Check your .env file configuration")
        print("2. Verify SAP server is accessible")
        print("3. Confirm credentials are correct")
        print("4. Check if SAP NetWeaver RFC SDK is properly installed")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_direct_sap_connection()
    if success:
        print("\n[SUCCESS] SAP RFC MCP Server test completed successfully!")
    else:
        print("\n[ERROR] SAP RFC MCP Server test failed!")
        sys.exit(1)
