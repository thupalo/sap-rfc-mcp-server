#!/usr/bin/env python3
"""
Basic usage example for SAP RFC MCP Server.

This example demonstrates:
1. Basic SAP connection
2. Simple RFC function call
3. Metadata retrieval
4. Error handling

Updated: August 2025
- Fixed RFC function call syntax (removed 'parameters' wrapper)
- Improved error handling and output formatting
- Added ASCII-safe console output
- Enhanced metadata parameter display
"""

import logging
import os
import sys

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sap_rfc_mcp_server import RFCMetadataManager, SAPRFCManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def safe_print(text):
    """Print text with ASCII-safe encoding for Windows console."""
    try:
        print(text.encode("ascii", "replace").decode("ascii"))
    except:
        print(text)


def main():
    """Basic usage example."""
    safe_print("=== SAP RFC MCP Server - Basic Usage Example ===\n")

    try:
        # Initialize SAP client
        safe_print("1. Initializing SAP client...")
        sap_client = SAPRFCManager()
        safe_print("   [OK] SAP client initialized successfully")

        # Test connection
        safe_print("\n2. Testing SAP connection...")
        try:
            # Simple RFC call to test connectivity
            result = sap_client.call_rfc_function("RFC_SYSTEM_INFO")

            system_info = result.get("RFCSI_EXPORT", {})
            safe_print(f"   [OK] Connected to SAP system:")
            safe_print(f"      System ID: {system_info.get('RFCSYSID', 'Unknown')}")
            safe_print(f"      Release: {system_info.get('RFCSAPRL', 'Unknown')}")
            safe_print(f"      Host: {system_info.get('RFCHOST', 'Unknown')}")

        except Exception as e:
            safe_print(f"   [ERROR] Connection failed: {e}")
            return False

        # Read table example
        safe_print("\n3. Reading SAP table data...")
        try:
            table_result = sap_client.call_rfc_function(
                "RFC_READ_TABLE",
                QUERY_TABLE="T001",  # Company codes table
                DELIMITER="|",
                ROWCOUNT=5,
            )

            data = table_result.get("DATA", [])
            fields = table_result.get("FIELDS", [])

            safe_print(f"   [OK] Retrieved {len(data)} rows from T001 table")
            safe_print(f"   [INFO] Table has {len(fields)} fields")

            if data:
                first_row = data[0].get("WA", "No data")
                # Truncate long output for readability
                if len(first_row) > 100:
                    first_row = first_row[:100] + "..."
                safe_print(f"   [SAMPLE] First row: {first_row}")
            else:
                safe_print("   [INFO] No data rows returned")

        except Exception as e:
            safe_print(f"   [WARNING] Table read failed: {e}")

        # Metadata example
        safe_print("\n4. Working with metadata...")
        try:
            # Initialize metadata manager
            connection_params = sap_client.config.to_connection_params()
            metadata_manager = RFCMetadataManager(connection_params)

            # Get function metadata
            metadata = metadata_manager.get_function_metadata(
                "RFC_READ_TABLE", language="EN"
            )

            if metadata:
                safe_print(f"   [OK] Retrieved metadata for RFC_READ_TABLE")

                # Get function name and description
                func_name = metadata.get(
                    "function_name",
                    metadata.get("_metadata", {}).get(
                        "function_name", "RFC_READ_TABLE"
                    ),
                )
                description = metadata.get(
                    "description",
                    metadata.get("_metadata", {}).get(
                        "description", "No description available"
                    ),
                )

                safe_print(f"      Function: {func_name}")
                safe_print(f"      Description: {description}")

                # Handle different metadata structure formats
                import_params = metadata.get(
                    "import_parameters", metadata.get("inputs", [])
                )
                export_params = metadata.get(
                    "export_parameters", metadata.get("outputs", [])
                )
                table_params = metadata.get(
                    "table_parameters", metadata.get("tables", [])
                )

                safe_print(
                    f"      Parameters: {len(import_params)} import, "
                    f"{len(export_params)} export, {len(table_params)} tables"
                )

                # Show a few parameter examples if available
                if import_params:
                    try:
                        # import_params is a dictionary, get the first parameter name
                        if isinstance(import_params, dict):
                            first_param_name = list(import_params.keys())[0]
                            first_param_info = import_params[first_param_name]
                            safe_print(
                                f"      First import parameter: {first_param_name}"
                            )
                            safe_print(
                                f"        Type: {first_param_info.get('type', 'Unknown')}"
                            )
                            safe_print(
                                f"        Description: {first_param_info.get('description', 'No description')}"
                            )
                        else:
                            # Fallback for list format
                            first_param_name = import_params[0].get(
                                "name",
                                import_params[0].get("parameter_name", "Unknown"),
                            )
                            safe_print(
                                f"      First import parameter: {first_param_name}"
                            )
                    except (IndexError, AttributeError, TypeError, KeyError) as e:
                        safe_print(
                            f"      Import parameters available but structure access failed: {e}"
                        )
            else:
                safe_print("   [WARNING] No metadata retrieved")

        except Exception as e:
            safe_print(f"   [ERROR] Metadata retrieval failed: {e}")

        safe_print("\n=== Example completed successfully! ===")
        return True

    except Exception as e:
        safe_print(f"\n[ERROR] Example failed: {e}")
        logger.exception("Example error details:")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
