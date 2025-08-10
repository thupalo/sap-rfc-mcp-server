"""
SAP Development Helper for VS Code
Quick access to SAP RFC functions and metadata
"""

import json
import os
import sys
from pathlib import Path

# Add the SAP RFC MCP server to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from sap_rfc_mcp_server import SAPRFCManager
    from sap_rfc_mcp_server.config import SAPConfig
    from sap_rfc_mcp_server.metadata_manager import RFCMetadataManager
except ImportError as e:
    print(f"[ERROR] Error importing SAP RFC MCP server: {e}")
    print(
        "Make sure the virtual environment is activated and dependencies are installed"
    )
    sys.exit(1)


class SAPDevHelper:
    """SAP Development Helper for VS Code"""

    def __init__(self):
        """Initialize SAP connection"""
        try:
            self.config = SAPConfig.from_env()
            self.sap_client = SAPRFCManager()
            self.metadata_manager = RFCMetadataManager(
                connection_params=self.config.to_connection_params()
            )
            print("[OK] SAP Development Helper initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize SAP connection: {e}")
            self.sap_client = None
            self.metadata_manager = None

    def get_system_info(self):
        """Get SAP system information"""
        if not self.sap_client:
            return {"error": "SAP client not initialized"}

        try:
            result = self.sap_client.call_rfc_function("RFC_SYSTEM_INFO")
            rfcsi = result.get("RFCSI_EXPORT", {})
            return {
                "system": rfcsi.get("RFCSYSID", "Unknown"),
                "host": rfcsi.get("RFCHOST", "Unknown"),
                "client": rfcsi.get("RFCMANDT", "Unknown"),
                "user": rfcsi.get("RFCUSER", "Unknown"),
                "release": rfcsi.get("RFCSAPRL", "Unknown"),
                "database": rfcsi.get("RFCDBSYS", "Unknown"),
            }
        except Exception as e:
            return {"error": f"Failed to get system info: {e}"}

    def get_table_structure(self, table_name):
        """Get table structure using DDIF_FIELDINFO_GET"""
        if not self.sap_client:
            return {"error": "SAP client not initialized"}

        try:
            result = self.sap_client.call_rfc_function(
                "DDIF_FIELDINFO_GET", TABNAME=table_name, LANGU="E"
            )

            fields = []
            for field in result.get("DFIES_TAB", []):
                fields.append(
                    {
                        "field": field.get("FIELDNAME", ""),
                        "type": field.get("DATATYPE", ""),
                        "length": field.get("LENG", 0),
                        "decimals": field.get("DECIMALS", 0),
                        "description": field.get("FIELDTEXT", ""),
                    }
                )

            return {"table": table_name, "fields": fields, "field_count": len(fields)}
        except Exception as e:
            return {"error": f"Failed to get table structure: {e}"}

    def test_table_access(self, table_name, max_rows=5):
        """Test table access by reading sample data with enhanced error handling"""
        if not self.sap_client:
            return {"error": "SAP client not initialized"}

        try:
            # Try with enhanced table reader first
            from sap_rfc_mcp_server.rfc_table_reader import RFCTableReader

            table_reader = RFCTableReader(self.sap_client)
            result = table_reader.read_table_safe(table_name, max_rows=max_rows)

            if result.get("success", False):
                return {
                    "table": table_name,
                    "success": True,
                    "method": "enhanced_reader",
                    "rows_read": result.get("row_count", 0),
                    "selected_fields": result.get("selected_fields", []),
                    "estimated_buffer_size": result.get("estimated_buffer_size", 0),
                    "sample_data": result.get("parsed_data", [])[:3],  # First 3 rows
                }
            else:
                return {
                    "table": table_name,
                    "success": False,
                    "method": "enhanced_reader",
                    "error": result.get("error", "Unknown error"),
                    "suggested_solution": result.get("suggested_solution", ""),
                }

        except ImportError:
            # Fallback to original method
            try:
                result = self.sap_client.call_rfc_function(
                    "RFC_READ_TABLE", QUERY_TABLE=table_name, ROWCOUNT=max_rows
                )

                return {
                    "table": table_name,
                    "success": True,
                    "method": "fallback",
                    "rows_read": len(result.get("DATA", [])),
                    "sample_data": result.get("DATA", [])[:3],  # First 3 rows
                }
            except Exception as e:
                error_msg = str(e)
                if "DATA_BUFFER_EXCEEDED" in error_msg:
                    return {
                        "table": table_name,
                        "success": False,
                        "method": "fallback",
                        "error": "DATA_BUFFER_EXCEEDED",
                        "suggested_solution": "Table has wide rows. Use enhanced reader or specify specific fields.",
                    }
                else:
                    return {
                        "table": table_name,
                        "success": False,
                        "method": "fallback",
                        "error": str(e),
                    }
        except Exception as e:
            return {"table": table_name, "success": False, "error": str(e)}

    def search_function_modules(self, pattern=""):
        """Search for function modules"""
        if not self.sap_client:
            return {"error": "SAP client not initialized"}

        try:
            result = self.sap_client.call_rfc_function(
                "RFC_FUNCTION_SEARCH", FUNCNAME=f"*{pattern}*"
            )

            functions = []
            for func in result.get("FUNCTIONS", [])[:20]:  # Limit to 20 results
                functions.append(
                    {
                        "name": func.get("FUNCNAME", ""),
                        "group": func.get("GROUPNAME", ""),
                        "text": func.get("STEXT", ""),
                    }
                )

            return {"pattern": pattern, "functions": functions, "count": len(functions)}
        except Exception as e:
            return {"error": f"Failed to search functions: {e}"}

    def get_metadata_stats(self):
        """Get metadata cache statistics"""
        if not self.metadata_manager:
            return {"error": "Metadata manager not initialized"}

        try:
            stats = self.metadata_manager.get_cache_stats()
            return {
                "cache_stats": stats,
                "has_cache": stats.get("total_functions", 0) > 0,
            }
        except Exception as e:
            return {"error": f"Failed to get metadata stats: {e}"}

    def test_enhanced_table_access(self, table_name, requested_fields=None, max_rows=5):
        """Test enhanced table access with specific field selection"""
        if not self.sap_client:
            return {"error": "SAP client not initialized"}

        try:
            from sap_rfc_mcp_server.rfc_table_reader import RFCTableReader

            table_reader = RFCTableReader(self.sap_client)

            # Test both safe and iterative methods
            results = {
                "table": table_name,
                "requested_fields": requested_fields,
                "safe_method": {},
                "iterative_method": {},
            }

            # Test safe method
            try:
                safe_result = table_reader.read_table_safe(
                    table_name, fields=requested_fields, max_rows=max_rows
                )
                results["safe_method"] = {
                    "success": safe_result.get("success", False),
                    "selected_fields": safe_result.get("selected_fields", []),
                    "buffer_size": safe_result.get("estimated_buffer_size", 0),
                    "row_count": safe_result.get("row_count", 0),
                    "error": safe_result.get("error", None),
                }
            except Exception as e:
                results["safe_method"] = {"success": False, "error": str(e)}

            # Test iterative method if fields specified
            if requested_fields:
                try:
                    iter_result = table_reader.read_table_iterative(
                        table_name, all_fields=requested_fields, max_rows=max_rows
                    )
                    results["iterative_method"] = {
                        "success": iter_result.get("success", False),
                        "method": iter_result.get("method", ""),
                        "chunk_count": iter_result.get("chunk_count", 0),
                        "field_chunks": iter_result.get("field_chunks", []),
                        "row_count": iter_result.get("row_count", 0),
                        "error": iter_result.get("error", None),
                    }
                except Exception as e:
                    results["iterative_method"] = {"success": False, "error": str(e)}

            return results

        except ImportError:
            return {
                "error": "Enhanced table reader not available",
                "suggested_action": "Enhanced RFC table reader module not found",
            }
        except Exception as e:
            return {"error": f"Enhanced table access test failed: {e}"}

    def refresh_metadata_cache(self):
        """Refresh metadata cache"""
        if not self.metadata_manager:
            return {"error": "Metadata manager not initialized"}

        try:
            print("[REFRESH] Refreshing metadata cache...")
            self.metadata_manager.refresh_cache()
            stats = self.metadata_manager.get_cache_stats()
            return {
                "success": True,
                "message": "Metadata cache refreshed",
                "stats": stats,
            }
        except Exception as e:
            return {"error": f"Failed to refresh cache: {e}"}


def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="SAP Development Helper")
    parser.add_argument(
        "--system-info", action="store_true", help="Get system information"
    )
    parser.add_argument("--table-structure", help="Get table structure")
    parser.add_argument("--test-table", help="Test table access")
    parser.add_argument("--search-functions", help="Search function modules")
    parser.add_argument(
        "--metadata-stats", action="store_true", help="Get metadata statistics"
    )
    parser.add_argument(
        "--refresh-cache", action="store_true", help="Refresh metadata cache"
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    helper = SAPDevHelper()

    if args.system_info:
        result = helper.get_system_info()
        print(json.dumps(result, indent=2))

    if args.table_structure:
        result = helper.get_table_structure(args.table_structure)
        print(json.dumps(result, indent=2))

    if args.test_table:
        result = helper.test_table_access(args.test_table)
        print(json.dumps(result, indent=2))

    if args.search_functions:
        result = helper.search_function_modules(args.search_functions)
        print(json.dumps(result, indent=2))

    if args.metadata_stats:
        result = helper.get_metadata_stats()
        print(json.dumps(result, indent=2))

    if args.refresh_cache:
        result = helper.refresh_metadata_cache()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
