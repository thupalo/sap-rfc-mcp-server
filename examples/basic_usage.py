#!/usr/bin/env python3
"""
Basic usage example for SAP RFC MCP Server.

This example demonstrates:
1. Basic SAP connection
2. Simple RFC function call
3. Metadata retrieval
4. Error handling
"""

import logging
import os
import sys

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sap_rfc_mcp_server import SAPRFCManager, RFCMetadataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Basic usage example."""
    print("=== SAP RFC MCP Server - Basic Usage Example ===\n")
    
    try:
        # Initialize SAP client
        print("1. Initializing SAP client...")
        sap_client = SAPRFCManager()
        print("   ✅ SAP client initialized successfully")
        
        # Test connection
        print("\n2. Testing SAP connection...")
        try:
            # Simple RFC call to test connectivity
            result = sap_client.call_rfc_function(
                function_name="RFC_SYSTEM_INFO",
                parameters={}
            )
            
            system_info = result.get('RFCSI_EXPORT', {})
            print(f"   ✅ Connected to SAP system:")
            print(f"      System ID: {system_info.get('RFCSYSID', 'Unknown')}")
            print(f"      Release: {system_info.get('RFCSAPRL', 'Unknown')}")
            print(f"      Host: {system_info.get('RFCHOST', 'Unknown')}")
            
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return False
        
        # Read table example
        print("\n3. Reading SAP table data...")
        try:
            table_result = sap_client.call_rfc_function(
                function_name="RFC_READ_TABLE",
                parameters={
                    "QUERY_TABLE": "T001",  # Company codes table
                    "DELIMITER": "|",
                    "ROWCOUNT": 5
                }
            )
            
            data = table_result.get('DATA', [])
            fields = table_result.get('FIELDS', [])
            
            print(f"   ✅ Retrieved {len(data)} rows from T001 table")
            if data:
                print(f"   First row: {data[0].get('WA', 'No data')}")
                
        except Exception as e:
            print(f"   ⚠️  Table read failed: {e}")
        
        # Metadata example
        print("\n4. Working with metadata...")
        try:
            # Initialize metadata manager
            connection_params = sap_client.config.to_connection_params()
            metadata_manager = RFCMetadataManager(connection_params)
            
            # Get function metadata
            metadata = metadata_manager.get_function_metadata(
                "RFC_READ_TABLE", 
                language="EN"
            )
            
            if metadata:
                print(f"   ✅ Retrieved metadata for RFC_READ_TABLE")
                print(f"      Function: {metadata.get('function_name', 'Unknown')}")
                print(f"      Description: {metadata.get('description', 'No description')}")
                print(f"      Parameters: {len(metadata.get('import_parameters', []))} import, "
                      f"{len(metadata.get('export_parameters', []))} export")
            else:
                print("   ⚠️  No metadata retrieved")
                
        except Exception as e:
            print(f"   ❌ Metadata retrieval failed: {e}")
        
        print("\n=== Example completed successfully! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        logger.exception("Example error details:")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
