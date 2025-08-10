#!/usr/bin/env python3
"""
Port Management Utility for SAP RFC MCP Server
Checks, displays, and optionally releases ports for MCP HTTP server startup
"""

import argparse
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil


class PortManager:
    """Manages local port checking and release operations."""

    def __init__(self):
        self.mcp_server_keywords = [
            "sap_rfc_mcp_server",
            "http_server",
            "uvicorn",
            "fastapi",
            "mcp",
        ]

    def check_port_status(self, port: int) -> dict[str, any]:
        """Check if a port is in use and get detailed information."""
        port_info = {
            "port": port,
            "in_use": False,
            "process_info": None,
            "connections": [],
            "can_connect": False,
        }

        # Test if we can bind to the port
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("127.0.0.1", port))
                port_info["can_connect"] = True
        except OSError:
            port_info["in_use"] = True

        # Get process information using psutil
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.laddr.port == port:
                    port_info["connections"].append(
                        {
                            "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                            "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}"
                            if conn.raddr
                            else "N/A",
                            "status": conn.status,
                            "pid": conn.pid,
                        }
                    )

                    if conn.pid:
                        try:
                            process = psutil.Process(conn.pid)
                            port_info["process_info"] = {
                                "pid": conn.pid,
                                "name": process.name(),
                                "cmdline": " ".join(process.cmdline())
                                if process.cmdline()
                                else "N/A",
                                "status": process.status(),
                                "cpu_percent": process.cpu_percent(),
                                "memory_info": process.memory_info()._asdict(),
                                "create_time": process.create_time(),
                                "is_mcp_related": self._is_mcp_related_process(process),
                            }
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            port_info["process_info"] = {
                                "pid": conn.pid,
                                "name": "Access Denied",
                                "cmdline": "N/A",
                                "is_mcp_related": False,
                            }
        except (psutil.AccessDenied, OSError) as e:
            print(f"[WARNING]  Limited access to network connections: {e}")

        return port_info

    def _is_mcp_related_process(self, process: psutil.Process) -> bool:
        """Check if a process is related to MCP server."""
        try:
            cmdline = " ".join(process.cmdline()).lower()
            name = process.name().lower()

            for keyword in self.mcp_server_keywords:
                if keyword in cmdline or keyword in name:
                    return True
            return False
        except:
            return False

    def scan_port_range(self, start_port: int, end_port: int) -> list[dict]:
        """Scan a range of ports and return status information."""
        print(f"[SEARCH] Scanning ports {start_port}-{end_port}...")

        results = []
        for port in range(start_port, end_port + 1):
            port_info = self.check_port_status(port)
            if port_info["in_use"]:
                results.append(port_info)

        return results

    def display_port_info(self, port_info: dict):
        """Display detailed port information."""
        port = port_info["port"]
        print(f"\n[EMOJI] Port {port}:")

        if not port_info["in_use"]:
            print(f"   [OK] Available")
            return

        print(f"   [ERROR] In Use")

        # Display connections
        if port_info["connections"]:
            for conn in port_info["connections"]:
                print(
                    f"   [EMOJI] Connection: {conn['local_address']} -> {conn['remote_address']}"
                )
                print(f"      Status: {conn['status']}")
                print(f"      PID: {conn['pid']}")

        # Display process information
        if port_info["process_info"]:
            proc = port_info["process_info"]
            print(f"   [CONFIG] Process:")
            print(f"      PID: {proc['pid']}")
            print(f"      Name: {proc['name']}")
            print(
                f"      Command: {proc['cmdline'][:100]}..."
                if len(proc.get("cmdline", "")) > 100
                else f"      Command: {proc.get('cmdline', 'N/A')}"
            )
            if "status" in proc:
                print(f"      Status: {proc['status']}")
            if "cpu_percent" in proc:
                print(f"      CPU: {proc['cpu_percent']:.1f}%")
            if "memory_info" in proc:
                memory_mb = proc["memory_info"]["rss"] / (1024 * 1024)
                print(f"      Memory: {memory_mb:.1f} MB")

            if proc.get("is_mcp_related", False):
                print(f"      [TARGET] MCP-Related Process Detected!")

    def kill_process_on_port(self, port: int, force: bool = False) -> bool:
        """Kill process using the specified port."""
        port_info = self.check_port_status(port)

        if not port_info["in_use"]:
            print(f"[OK] Port {port} is already free")
            return True

        if not port_info["process_info"]:
            print(f"[ERROR] No process information available for port {port}")
            return False

        pid = port_info["process_info"]["pid"]
        process_name = port_info["process_info"]["name"]
        is_mcp = port_info["process_info"].get("is_mcp_related", False)

        print(f"\n[TARGET] Found process using port {port}:")
        print(f"   PID: {pid}")
        print(f"   Name: {process_name}")
        print(f"   MCP-Related: {'Yes' if is_mcp else 'No'}")

        if not force and not is_mcp:
            response = input(
                f"\n[WARNING]  This doesn't appear to be an MCP process. Kill anyway? [y/N]: "
            )
            if response.lower() not in ["y", "yes"]:
                print("[ERROR] Process termination cancelled")
                return False

        try:
            process = psutil.Process(pid)

            # Try graceful termination first
            print(f"[REFRESH] Attempting graceful termination of PID {pid}...")
            process.terminate()

            # Wait for process to terminate
            try:
                process.wait(timeout=5)
                print(f"[OK] Process {pid} terminated gracefully")
            except psutil.TimeoutExpired:
                # Force kill if graceful termination fails
                print(f"[WARNING]  Graceful termination timed out, force killing...")
                process.kill()
                process.wait(timeout=3)
                print(f"[OK] Process {pid} force killed")

            # Verify port is now free
            time.sleep(1)
            new_status = self.check_port_status(port)
            if not new_status["in_use"]:
                print(f"[OK] Port {port} is now free")
                return True
            else:
                print(f"[ERROR] Port {port} is still in use")
                return False

        except psutil.NoSuchProcess:
            print(f"[OK] Process {pid} no longer exists")
            return True
        except psutil.AccessDenied:
            print(f"[ERROR] Access denied - cannot kill process {pid}")
            print(f"[TIP] Try running as administrator")
            return False
        except Exception as e:
            print(f"[ERROR] Error killing process {pid}: {e}")
            return False

    def release_mcp_ports(
        self, port_range: tuple[int, int], force: bool = False
    ) -> list[int]:
        """Release all MCP-related processes in port range."""
        start_port, end_port = port_range
        released_ports = []

        print(
            f"[SEARCH] Scanning for MCP processes on ports {start_port}-{end_port}..."
        )

        busy_ports = self.scan_port_range(start_port, end_port)
        mcp_ports = [
            port_info
            for port_info in busy_ports
            if port_info.get("process_info", {}).get("is_mcp_related", False)
        ]

        if not mcp_ports:
            print(f"[OK] No MCP processes found on ports {start_port}-{end_port}")
            return released_ports

        print(f"\n[TARGET] Found {len(mcp_ports)} MCP-related processes:")
        for port_info in mcp_ports:
            self.display_port_info(port_info)

        if not force:
            response = input(
                f"\n[REFRESH] Release all {len(mcp_ports)} MCP processes? [Y/n]: "
            )
            if response.lower() in ["n", "no"]:
                print("[ERROR] Operation cancelled")
                return released_ports

        for port_info in mcp_ports:
            port = port_info["port"]
            if self.kill_process_on_port(port, force=True):
                released_ports.append(port)

        return released_ports

    def suggest_free_port(self, preferred_ports: list[int]) -> Optional[int]:
        """Suggest a free port from preferred list."""
        for port in preferred_ports:
            port_info = self.check_port_status(port)
            if not port_info["in_use"]:
                return port

        # If no preferred ports are free, find any free port in range
        for port in range(8000, 8100):
            port_info = self.check_port_status(port)
            if not port_info["in_use"]:
                return port

        return None


def main():
    parser = argparse.ArgumentParser(
        description="Port Management Utility for SAP RFC MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python port_manager.py --check 8000                    # Check single port
  python port_manager.py --scan 8000 8010               # Scan port range
  python port_manager.py --kill 8000                    # Kill process on port
  python port_manager.py --release-mcp 8000 8020        # Release MCP processes
  python port_manager.py --suggest                      # Suggest free port
        """,
    )

    parser.add_argument(
        "--check", type=int, metavar="PORT", help="Check status of specific port"
    )
    parser.add_argument(
        "--scan",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Scan range of ports",
    )
    parser.add_argument(
        "--kill", type=int, metavar="PORT", help="Kill process using specific port"
    )
    parser.add_argument(
        "--release-mcp",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Release all MCP processes in port range",
    )
    parser.add_argument(
        "--suggest", action="store_true", help="Suggest free port for MCP server"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force operations without confirmation"
    )

    args = parser.parse_args()

    if not any([args.check, args.scan, args.kill, args.release_mcp, args.suggest]):
        parser.print_help()
        return

    port_manager = PortManager()

    print("[CONFIG] SAP RFC MCP Server - Port Management Utility")
    print("=" * 60)

    try:
        if args.check:
            port_info = port_manager.check_port_status(args.check)
            port_manager.display_port_info(port_info)

        elif args.scan:
            start_port, end_port = args.scan
            busy_ports = port_manager.scan_port_range(start_port, end_port)

            if not busy_ports:
                print(f"[OK] All ports {start_port}-{end_port} are available")
            else:
                print(f"\n[DATA] Found {len(busy_ports)} busy ports:")
                for port_info in busy_ports:
                    port_manager.display_port_info(port_info)

        elif args.kill:
            port_manager.kill_process_on_port(args.kill, force=args.force)

        elif args.release_mcp:
            start_port, end_port = args.release_mcp
            released = port_manager.release_mcp_ports(
                (start_port, end_port), force=args.force
            )
            if released:
                print(f"\n[OK] Released ports: {', '.join(map(str, released))}")

        elif args.suggest:
            preferred_ports = [8000, 8001, 8002, 8080, 8081, 8082]
            free_port = port_manager.suggest_free_port(preferred_ports)

            if free_port:
                print(f"[TIP] Suggested free port: {free_port}")
                print(f"\nTo start MCP server:")
                print(f"python -m sap_rfc_mcp_server.http_server 127.0.0.1 {free_port}")
            else:
                print("[ERROR] No free ports found in range 8000-8099")

    except KeyboardInterrupt:
        print("\n[ERROR] Operation cancelled by user")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


if __name__ == "__main__":
    main()
