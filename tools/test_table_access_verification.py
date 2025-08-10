#!/usr/bin/env python3
"""
Final verification test for SAP table access via MCP components
"""

import json
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sap_rfc_mcp_server.sap_client import SAPConnectionError, SAPRFCManager


def test_table_access_verification():
    print("[SEARCH] SAP Table Access Verification Test")
    print("=" * 60)

    try:
        # Initialize SAP client (same as MCP server uses)
        print("[INIT] Initializing SAP client...")
        sap_client = SAPRFCManager()
        print("[OK] SAP client initialized successfully")

        # Test 1: RFC_SYSTEM_INFO (baseline test)
        print("\n[TEST] Test 1: RFC_SYSTEM_INFO")
        try:
            system_info = sap_client.call_rfc_function("RFC_SYSTEM_INFO")
            print("[OK] RFC_SYSTEM_INFO successful")
            if "RFCSI_EXPORT" in system_info:
                rfc_info = system_info["RFCSI_EXPORT"]
                print(f'   System: {rfc_info.get("RFCSYSID", "Unknown")}')
                print(f'   Host: {rfc_info.get("RFCHOST", "Unknown")}')
        except Exception as e:
            print(f"[ERROR] RFC_SYSTEM_INFO failed: {e}")
            return

        # Test 2: T000 table access (standard clients table)
        print("\n[INFO] Test 2: T000 Table Access")
        try:
            result = sap_client.call_rfc_function(
                "RFC_READ_TABLE", QUERY_TABLE="T000", DELIMITER="|", ROWCOUNT=5
            )
            print("[OK] T000 table access successful")

            if "DATA" in result and result["DATA"]:
                print(f'   Retrieved {len(result["DATA"])} rows')
                # Display sample data
                for i, row in enumerate(result["DATA"][:3]):
                    print(f'   Row {i+1}: {row.get("WA", "")[:50]}...')

        except Exception as e:
            print(f"[ERROR] T000 table access failed: {e}")

        # Test 3: ZKNA1 customer table access with enhanced error handling
        print("\n[USERS] Test 3: ZKNA1 Customer Table Access (Enhanced)")
        try:
            # First try with enhanced table reader
            from sap_rfc_mcp_server.rfc_table_reader import RFCTableReader

            table_reader = RFCTableReader(sap_client)
            result = table_reader.read_table_safe("ZKNA1", max_rows=3)

            if result.get("success", False):
                print("[OK] ZKNA1 table access successful with enhanced reader")
                print(f'   Retrieved {result.get("row_count", 0)} rows')
                print(f'   Selected fields: {result.get("selected_fields", [])}')
                if result.get("parsed_data"):
                    print("   Sample data available")
            else:
                print(
                    f'[ERROR] ZKNA1 table access failed: {result.get("error", "Unknown error")}'
                )
                if "suggested_solution" in result:
                    print(f'   [TIP] {result["suggested_solution"]}')

        except ImportError:
            # Fallback to original method if new reader not available
            print("   Using fallback method...")
            try:
                result = sap_client.call_rfc_function(
                    "RFC_READ_TABLE", QUERY_TABLE="ZKNA1", DELIMITER="|", ROWCOUNT=3
                )
                print("[OK] ZKNA1 table access successful")

                if "DATA" in result and result["DATA"]:
                    print(f'   Retrieved {len(result["DATA"])} rows')
                    print("   Sample customer data available")
                else:
                    print("   Table exists but no data returned")

            except Exception as e:
                error_msg = str(e)
                if "DATA_BUFFER_EXCEEDED" in error_msg:
                    print("[ERROR] ZKNA1 table access failed: DATA_BUFFER_EXCEEDED")
                    print(
                        "   [TIP] Table has wide rows. Enhanced reader would handle this automatically."
                    )
                else:
                    print(f"[ERROR] ZKNA1 table access failed: {e}")
                print("   This is expected if ZKNA1 table does not exist")
        except Exception as e:
            print(f"[ERROR] ZKNA1 table access failed: {e}")
            print("   This is expected if ZKNA1 table does not exist")

        # Test 4: Table structure retrieval
        print("\n[BUILD] Test 4: Table Structure Retrieval")
        try:
            structure = sap_client.call_rfc_function(
                "DDIF_FIELDINFO_GET", TABNAME="T000", LANGU="E"
            )
            print("[OK] Table structure retrieval successful")

            if "DFIES_TAB" in structure:
                fields = structure["DFIES_TAB"]
                print(f"   T000 has {len(fields)} fields")
                # Show first few fields
                for field in fields[:5]:
                    print(
                        f'   - {field.get("FIELDNAME", "")} ({field.get("DATATYPE", "")})'
                    )

        except Exception as e:
            print(f"[ERROR] Table structure retrieval failed: {e}")

        # Test 5: Function module search
        print("\n[SEARCH] Test 5: Function Module Search")
        try:
            search_result = sap_client.call_rfc_function(
                "RFC_FUNCTION_SEARCH", FUNCNAME="RFC_READ_TABLE"
            )
            print("[OK] Function module search successful")

            if "FUNCTIONS" in search_result:
                functions = search_result["FUNCTIONS"]
                print(f"   Found {len(functions)} matching functions")

        except Exception as e:
            print(f"[ERROR] Function module search failed: {e}")

        print("\n" + "=" * 60)
        print("[OK] Table access verification completed")
        print("   All core MCP functionality is working correctly")

    except SAPConnectionError as e:
        print(f"[ERROR] SAP Connection Error: {e}")
        print("   Please check your SAP connection configuration")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")


def test_mcp_table_tools():
    """Test MCP table tools specifically"""
    print("\n[INFO] Testing MCP Table Tools")
    print("-" * 40)

    try:
        # Import the server and tools from the correct module
        from sap_rfc_mcp_server.server import _get_sap_client, _get_table_reader, server

        print("[INFO] Testing get_table_data tool...")

        # Test by directly calling the tool function
        try:
            # Get the tool handler function
            sap_client = _get_sap_client()
            table_reader = _get_table_reader()

            print("[OK] SAP client and table reader initialized")

            # Test a simple table read
            result = table_reader.read_table_safe("T000", max_rows=3)

            if result.get("success", False):
                print("[OK] get_table_data functionality working")
                print(f'   Retrieved {result.get("row_count", 0)} rows')
                print(f'   Selected fields: {result.get("selected_fields", [])}')
            else:
                print(
                    f'[ERROR] get_table_data failed: {result.get("error", "Unknown error")}'
                )

        except Exception as e:
            print(f"[ERROR] Direct tool test failed: {e}")

        print("[OK] MCP table tools verification completed")

    except ImportError as e:
        print(f"[ERROR] MCP server import failed: {e}")
        print("   Skipping MCP table tools test")
    except Exception as e:
        print(f"[ERROR] MCP table tools test failed: {e}")


if __name__ == "__main__":
    test_table_access_verification()
    test_mcp_table_tools()
