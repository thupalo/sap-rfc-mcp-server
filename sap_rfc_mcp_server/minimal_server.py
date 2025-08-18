#!/usr/bin/env python3
"""
Minimal MCP Server for SAP RFC - STDIO Transport
Focuses on core MCP protocol and basic RFC connectivity.

This server provides only essential RFC functionality, pushing complex
processing to client-side implementations for better architecture.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

import mcp.server.stdio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool

from .sap_client import SAPRFCManager, SAPConnectionError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("sap-rfc-minimal-server")

# Global SAP client
sap_client = None


def _get_sap_client():
    """Get or create SAP client instance."""
    global sap_client
    if sap_client is None:
        sap_client = SAPRFCManager()
    return sap_client


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List minimal set of SAP RFC tools."""
    return [
        Tool(
            name="call_rfc_function",
            description="Call any RFC function with parameters - returns raw results without processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the RFC function to call"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Function parameters as key-value pairs"
                    }
                },
                "required": ["function_name"]
            }
        ),
        Tool(
            name="get_system_info",
            description="Get basic SAP system information using RFC_SYSTEM_INFO",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="ping_connection",
            description="Test SAP connection status and return basic connectivity info",
            inputSchema={
                "type": "object", 
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls with minimal processing."""
    try:
        client = _get_sap_client()
        
        if name == "call_rfc_function":
            function_name = arguments["function_name"]
            parameters = arguments.get("parameters", {})
            
            logger.info(f"Calling RFC function: {function_name}")
            
            # Direct RFC call - no server-side processing
            result = await asyncio.get_event_loop().run_in_executor(
                None, client.call_rfc_function, function_name, **parameters
            )
            
            # Return raw result as JSON - let client process
            return [TextContent(
                type="text", 
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
            
        elif name == "get_system_info":
            logger.info("Getting SAP system information")
            
            # Get basic system info
            result = await asyncio.get_event_loop().run_in_executor(
                None, client.get_system_info
            )
            
            return [TextContent(
                type="text", 
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
            
        elif name == "ping_connection":
            logger.info("Testing SAP connection")
            
            # Simple connection test
            try:
                # Try a lightweight RFC call
                await asyncio.get_event_loop().run_in_executor(
                    None, client.get_system_info
                )
                
                result = {
                    "status": "connected",
                    "timestamp": str(asyncio.get_event_loop().time()),
                    "server": "minimal-mcp-server"
                }
                
            except Exception as e:
                result = {
                    "status": "disconnected", 
                    "error": str(e),
                    "timestamp": str(asyncio.get_event_loop().time()),
                    "server": "minimal-mcp-server"
                }
                
            return [TextContent(
                type="text", 
                text=json.dumps(result, indent=2)
            )]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except SAPConnectionError as e:
        logger.error(f"SAP connection error in tool {name}: {e}")
        return [TextContent(
            type="text", 
            text=json.dumps({
                "error": "SAP Connection Error",
                "message": str(e),
                "tool": name
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(
            type="text", 
            text=json.dumps({
                "error": "Server Error", 
                "message": str(e),
                "tool": name
            }, indent=2)
        )]


async def main():
    """Main entry point for the minimal MCP server."""
    logger.info("Starting SAP RFC Minimal MCP Server (STDIO)")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sap-rfc-minimal-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=mcp.server.NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
