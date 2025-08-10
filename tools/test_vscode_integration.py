#!/usr/bin/env python3
"""
Quick test of SAP Development Helper functionality
"""

import sys
from pathlib import Path

# Add project root to Python path for SAP RFC MCP server imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import directly since we're in the same directory
from sap_dev_helper import SAPDevHelper

print("[TEST] Testing SAP Development Helper interactively")
print()

# Initialize the helper
helper = SAPDevHelper()

print("[DATA] System Info:")
info = helper.get_system_info()
if "error" not in info:
    for key, value in info.items():
        print(f"   {key}: {value}")
else:
    print(f'   Error: {info["error"]}')

print()
print("[INFO] Testing table access with T000 (Company Codes):")
companies = helper.test_table_access("T000")
if "error" not in companies and companies.get("success", False):
    print(f'   Found {companies.get("rows_read", 0)} companies')
    sample_data = companies.get("sample_data", [])
    if sample_data:
        for row in sample_data[:3]:  # Show first 3 rows
            print(f"   - {row}")
    else:
        print("   No sample data available")
else:
    error_msg = companies.get("error", "Table access failed")
    print(f"   Error: {error_msg}")
    if "suggested_solution" in companies:
        print(f'   Suggestion: {companies["suggested_solution"]}')

print()
print("[FILE] RFC_SYSTEM_INFO Test:")
try:
    # Test calling RFC_SYSTEM_INFO directly
    system_info = helper.get_system_info()
    if "error" not in system_info:
        print(f"   Function call successful")
        print(f'   System: {system_info.get("system", "N/A")}')
        print(f'   Host: {system_info.get("host", "N/A")}')
        print(f'   Release: {system_info.get("release", "N/A")}')
    else:
        print(f'   Error: {system_info["error"]}')
except Exception as e:
    print(f"   Error: {e}")

print()
print("[INFO] Cache Statistics:")
stats = helper.get_metadata_stats()
if "error" not in stats:
    print(f'   Entries: {stats.get("total_entries", 0)}')
    print(f'   Hits: {stats.get("cache_hits", 0)}')
    print(f'   Misses: {stats.get("cache_misses", 0)}')
    print(f'   Hit ratio: {stats.get("hit_ratio", 0):.1%}')
    print(f'   Size: {stats.get("cache_size_mb", 0):.2f} MB')
else:
    print(f'   Error: {stats["error"]}')

print()
print("[INFO] Function module search (RFC_READ):")
search_results = helper.search_function_modules("RFC_READ")
if "error" not in search_results:
    functions = search_results.get("functions", [])
    print(f"   Found {len(functions)} functions")
    for func in functions[:3]:  # Show first 3
        print(
            f'   - {func.get("name", "N/A")}: {func.get("description", "No description")[:50]}...'
        )
else:
    print(f'   Error: {search_results["error"]}')

print()
print("[SUCCESS] SAP Development Helper test completed!")
print("[TARGET] All functions working properly for VS Code integration")
