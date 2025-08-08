"""MCP Server for SAP RFC functions."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio

from .sap_client import SAPRFCManager, SAPConnectionError
from .metadata_manager import RFCMetadataManager


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SAP client and metadata manager
sap_client = SAPRFCManager()
metadata_manager: Optional[RFCMetadataManager] = None

# Create MCP server
server = Server("sap-rfc-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available SAP RFC tools."""
    return [
        Tool(
            name="rfc_system_info",
            description="Get SAP system information using RFC_SYSTEM_INFO",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_rfc_functions",
            description="Query available RFC functions with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "funcs_mask": {
                        "type": "string",
                        "description": "Function name mask (supports wildcards with *)"
                    },
                    "devclass": {
                        "type": "string", 
                        "description": "Development class filter"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="call_rfc_function",
            description="Call an RFC function with specified parameters",
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
            name="get_function_metadata",
            description="Get comprehensive metadata for an RFC function including parameters, types, and descriptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the RFC function"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for descriptions (EN, DE, PL, etc.)",
                        "default": "EN"
                    },
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Force refresh from SAP system (ignore cache)",
                        "default": false
                    }
                },
                "required": ["function_name"]
            }
        ),
        Tool(
            name="search_rfc_functions",
            description="Search for RFC functions using keywords in names and descriptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords to search for)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_metadata_cache_stats",
            description="Get statistics about the RFC metadata cache",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
            inputSchema={
                "type": "object",
                "properties": {
                    "funcs_mask": {
                        "type": "string",
                        "description": "Function name mask (use * for wildcards, e.g., 'RFC_*')"
                    },
                    "devclass": {
                        "type": "string", 
                        "description": "Development class filter (use * for wildcards)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="call_rfc_function",
            description="Execute an arbitrary RFC function with parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the RFC function to call"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Parameters to pass to the RFC function"
                    }
                },
                "required": ["function_name"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "rfc_system_info":
            result = await asyncio.get_event_loop().run_in_executor(
                None, sap_client.get_system_info
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        
        elif name == "get_rfc_functions":
            funcs_mask = arguments.get("funcs_mask")
            devclass = arguments.get("devclass")
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, sap_client.get_rfc_functions, funcs_mask, devclass
            )
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        
        elif name == "call_rfc_function":
            function_name = arguments["function_name"]
            parameters = arguments.get("parameters", {})
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, sap_client.call_rfc_function, function_name, **parameters
            )
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except SAPConnectionError as e:
        logger.error(f"SAP connection error in tool {name}: {e}")
        return [
            TextContent(
                type="text",
                text=f"SAP Connection Error: {str(e)}"
            )
        ]
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [
            TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]


async def main():
    """Main entry point for the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sap-rfc-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
