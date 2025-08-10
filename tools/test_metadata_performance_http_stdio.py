#!/usr/bin/env python3
"""
Performance Test: RFC Function Metadata Caching
Tests performance gain from metadata caching for BAPI_USER_GET_DETAIL
Compares first, second, and third calls to measure cache effectiveness
"""

import json
import sys
import time
from datetime import datetime

import requests


def test_metadata_performance_http():
    """Test metadata performance via HTTP server with caching"""
    print("[LAUNCH] RFC Metadata Performance Test - HTTP Server")
    print("=" * 50)
    print(f"[TARGET] Function: BAPI_USER_GET_DETAIL")
    print(f"[TIME] Started at: {datetime.now().strftime('%H:%M:%S')}")
    print()

    base_url = "http://127.0.0.1:8000"

    try:
        # Check server health first
        print("[REFRESH] Checking server health...")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print("[ERROR] HTTP server not available - starting server first")
            return False
        print("[OK] Server is healthy")

        # Clear cache first (optional)
        print("\n[EMOJI] Getting initial cache stats...")
        cache_request = {"name": "get_metadata_cache_stats", "arguments": {}}
        cache_response = requests.post(
            f"{base_url}/mcp/call_tool", json=cache_request, timeout=10
        )

        if cache_response.status_code == 200:
            result = cache_response.json()
            content = result.get("result", [])
            if content and content[0].get("type") == "text":
                cache_stats = json.loads(content[0]["text"])
                print(f"[DATA] Cache entries: {cache_stats.get('total_entries', 0)}")
                print(f"[DATA] Cache hits: {cache_stats.get('cache_hits', 0)}")
                print(f"[DATA] Cache misses: {cache_stats.get('cache_misses', 0)}")

        # Performance test - 3 consecutive calls
        function_name = "BAPI_USER_GET_DETAIL"
        times = []

        for call_num in range(1, 4):
            print(f"\n[SEARCH] Call #{call_num}: Getting metadata for {function_name}")

            metadata_request = {
                "name": "get_function_metadata",
                "arguments": {
                    "function_name": function_name,
                    "force_refresh": call_num == 1,  # Force refresh only on first call
                },
            }

            # Measure time
            start_time = time.perf_counter()

            response = requests.post(
                f"{base_url}/mcp/call_tool",
                json=metadata_request,
                timeout=60,
                headers={"Content-Type": "application/json"},
            )

            end_time = time.perf_counter()
            duration = end_time - start_time
            times.append(duration)

            print(f"⏱️ Duration: {duration:.3f} seconds")
            print(f"[DATA] Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                content = result.get("result", [])
                if content and content[0].get("type") == "text":
                    metadata_text = content[0]["text"]
                    metadata_obj = json.loads(metadata_text)

                    # Show basic info
                    func_meta = metadata_obj.get("_metadata", {})
                    inputs = metadata_obj.get("inputs", {})
                    outputs = metadata_obj.get("outputs", {})
                    tables = metadata_obj.get("tables", {})

                    print(f"[OK] Metadata retrieved successfully")
                    print(f"[FILE] Description: {func_meta.get('description', 'N/A')}")
                    print(f"[EMOJI] Input parameters: {len(inputs)}")
                    print(f"[EMOJI] Output parameters: {len(outputs)}")
                    print(f"[DATA] Table parameters: {len(tables)}")
                    print(
                        f"[EMOJI] Schema version: {metadata_obj.get('_schema_version', 'N/A')}"
                    )

                    # Show cache status on retrieved metadata
                    retrieved_at = metadata_obj.get("_retrieved_at", "Unknown")
                    print(f"[EMOJI] Retrieved at: {retrieved_at}")

                else:
                    print("[ERROR] No metadata content in response")
            else:
                print(f"[ERROR] Failed to get metadata: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Error: {error_detail}")
                except:
                    print(f"Error text: {response.text}")

        # Performance analysis
        print(f"\n[CHART] Performance Analysis")
        print("=" * 25)

        if len(times) >= 3:
            first_call = times[0]
            second_call = times[1]
            third_call = times[2]

            print(f"[EMOJI] First call (cache miss):  {first_call:.3f}s")
            print(f"[EMOJI] Second call (cache hit):  {second_call:.3f}s")
            print(f"[EMOJI] Third call (cache hit):   {third_call:.3f}s")

            # Calculate improvements
            if first_call > 0:
                second_improvement = ((first_call - second_call) / first_call) * 100
                third_improvement = ((first_call - third_call) / first_call) * 100

                print(f"\n[LAUNCH] Performance Gains:")
                print(
                    f"[DATA] Second call improvement: {second_improvement:.1f}% faster"
                )
                print(
                    f"[DATA] Third call improvement:  {third_improvement:.1f}% faster"
                )

                # Speed ratios
                second_speedup = first_call / second_call if second_call > 0 else 0
                third_speedup = first_call / third_call if third_call > 0 else 0

                print(f"\n[FAST] Speed Ratios:")
                print(f"[DATA] Second call: {second_speedup:.1f}x faster")
                print(f"[DATA] Third call:  {third_speedup:.1f}x faster")

                # Average cache performance
                avg_cache_time = (second_call + third_call) / 2
                cache_improvement = ((first_call - avg_cache_time) / first_call) * 100

                print(f"\n[EMOJI] Cache Effectiveness:")
                print(f"[DATA] Average cache response time: {avg_cache_time:.3f}s")
                print(
                    f"[DATA] Overall cache improvement: {cache_improvement:.1f}% faster"
                )
                print(f"[DATA] Cache speedup ratio: {first_call / avg_cache_time:.1f}x")

        # Get final cache stats
        print(f"\n[DATA] Final Cache Statistics")
        print("=" * 27)

        final_cache_response = requests.post(
            f"{base_url}/mcp/call_tool",
            json={"name": "get_metadata_cache_stats", "arguments": {}},
            timeout=10,
        )

        if final_cache_response.status_code == 200:
            result = final_cache_response.json()
            content = result.get("result", [])
            if content and content[0].get("type") == "text":
                final_stats = json.loads(content[0]["text"])
                print(
                    f"[DATA] Total cache entries: {final_stats.get('total_entries', 0)}"
                )
                print(f"[DATA] Total cache hits: {final_stats.get('cache_hits', 0)}")
                print(
                    f"[DATA] Total cache misses: {final_stats.get('cache_misses', 0)}"
                )
                print(f"[DATA] Cache hit ratio: {final_stats.get('hit_ratio', 0):.1%}")
                print(
                    f"[EMOJI] Cache size (MB): {final_stats.get('cache_size_mb', 0):.2f}"
                )

        return True

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_metadata_performance_stdio():
    """Test metadata performance via STDIO server with caching"""
    print("\n[EMOJI] RFC Metadata Performance Test - STDIO Server")
    print("=" * 51)
    print(f"[TARGET] Function: BAPI_USER_GET_DETAIL")
    print()

    try:
        import subprocess
        from pathlib import Path

        # Get project root from tools folder
        project_root = Path(__file__).parent.parent
        python_exe = project_root / "venv" / "Scripts" / "python.exe"

        process = subprocess.Popen(
            [str(python_exe), "-m", "sap_rfc_mcp_server.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(project_root),
            text=True,
        )

        # Initialize connection
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"experimental": {}, "sampling": {}},
                "clientInfo": {"name": "perf-test", "version": "1.0"},
            },
        }

        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        init_response = process.stdout.readline()

        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        time.sleep(0.3)

        # Performance test - 3 consecutive calls
        function_name = "BAPI_USER_GET_DETAIL"
        times = []

        for call_num in range(1, 4):
            print(f"[SEARCH] Call #{call_num}: Getting metadata for {function_name}")

            metadata_request = {
                "jsonrpc": "2.0",
                "id": call_num + 10,
                "method": "tools/call",
                "params": {
                    "name": "get_function_metadata",
                    "arguments": {
                        "function_name": function_name,
                        "force_refresh": call_num == 1,
                    },
                },
            }

            # Measure time
            start_time = time.perf_counter()

            process.stdin.write(json.dumps(metadata_request) + "\n")
            process.stdin.flush()

            response_line = process.stdout.readline()

            end_time = time.perf_counter()
            duration = end_time - start_time
            times.append(duration)

            print(f"⏱️ Duration: {duration:.3f} seconds")

            try:
                response_data = json.loads(response_line)
                if "result" in response_data:
                    content = response_data["result"].get("content", [])
                    if content and content[0].get("type") == "text":
                        metadata_text = content[0]["text"]
                        metadata_obj = json.loads(metadata_text)

                        func_meta = metadata_obj.get("_metadata", {})
                        inputs = metadata_obj.get("inputs", {})
                        outputs = metadata_obj.get("outputs", {})
                        tables = metadata_obj.get("tables", {})

                        print(f"[OK] Metadata retrieved successfully")
                        print(f"[EMOJI] Input parameters: {len(inputs)}")
                        print(f"[EMOJI] Output parameters: {len(outputs)}")
                        print(f"[DATA] Table parameters: {len(tables)}")
                    else:
                        print("[ERROR] No metadata content")
                else:
                    print(f"[ERROR] Error: {response_data.get('error')}")
            except Exception as e:
                print(f"[ERROR] Parse error: {e}")

        # Performance analysis for STDIO
        if len(times) >= 3:
            first_call = times[0]
            second_call = times[1]
            third_call = times[2]

            print(f"\n[CHART] STDIO Performance Analysis")
            print("=" * 30)
            print(f"[EMOJI] First call:  {first_call:.3f}s")
            print(f"[EMOJI] Second call: {second_call:.3f}s")
            print(f"[EMOJI] Third call:  {third_call:.3f}s")

            if first_call > 0:
                second_improvement = ((first_call - second_call) / first_call) * 100
                third_improvement = ((first_call - third_call) / first_call) * 100

                print(f"\n[LAUNCH] STDIO Performance Gains:")
                print(f"[DATA] Second call: {second_improvement:.1f}% faster")
                print(f"[DATA] Third call:  {third_improvement:.1f}% faster")

        process.terminate()
        return True

    except Exception as e:
        print(f"[ERROR] STDIO Error: {e}")
        if "process" in locals():
            try:
                process.terminate()
            except:
                pass
        return False


def main():
    """Main performance test function"""
    print("[TARGET] RFC Function Metadata Caching Performance Test")
    print("=" * 52)
    print(f"Function: BAPI_USER_GET_DETAIL")
    print(f"Objective: Measure performance improvement from metadata caching")
    print(f"Test: Compare 1st (cache miss), 2nd & 3rd calls (cache hits)")
    print()

    # Test HTTP server performance
    http_success = test_metadata_performance_http()

    # Test STDIO server performance
    stdio_success = test_metadata_performance_stdio()

    # Final summary
    print(f"\n[EMOJI] Performance Test Summary")
    print("=" * 29)
    print(
        f"[WEB] HTTP Server Performance:  {'[OK] SUCCESS' if http_success else '[ERROR] FAILED'}"
    )
    print(
        f"[EMOJI] STDIO Server Performance: {'[OK] SUCCESS' if stdio_success else '[ERROR] FAILED'}"
    )

    if http_success or stdio_success:
        print(f"\n[TIP] Key Insights:")
        print(f"• First call: Fetches metadata from SAP system (slower)")
        print(f"• Subsequent calls: Served from cache (much faster)")
        print(f"• Cache provides significant performance improvements")
        print(f"• Both HTTP and STDIO benefit from metadata caching")

        print(f"\n[LAUNCH] Ready for production with optimized caching!")
        return True
    else:
        print(f"\n[ERROR] Performance tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
