"""MCP Server for SAP RFC functions with enhanced metadata support."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from collections.abc import Sequence

import mcp.server.stdio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    LoggingLevel,
    Resource,
    TextContent,
    Tool,
)

from .sap_client import SAPConnectionError, SAPRFCManager

try:
    from .metadata_manager import RFCMetadataManager
except ImportError:
    RFCMetadataManager = None


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize global variables
sap_client = None
metadata_manager = None

# Create MCP server
server = Server("sap-rfc-mcp-server")


def _get_sap_client():
    """Get or create SAP client instance."""
    global sap_client
    if sap_client is None:
        sap_client = SAPRFCManager()
    return sap_client


def _get_metadata_manager():
    """Get or create metadata manager instance."""
    global metadata_manager
    if metadata_manager is None:
        if RFCMetadataManager is None:
            raise ImportError("RFCMetadataManager not available")
        try:
            # Get connection params from sap_client
            client = _get_sap_client()
            config = client.config
            connection_params = config.to_connection_params()
            metadata_manager = RFCMetadataManager(connection_params)
            logger.info("Metadata manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize metadata manager: {e}")
            raise
    return metadata_manager


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available SAP RFC tools."""
    return [
        Tool(
            name="rfc_system_info",
            description="Get SAP system information using RFC_SYSTEM_INFO",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_rfc_functions",
            description="Query available RFC functions with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "funcs_mask": {
                        "type": "string",
                        "description": "Function name mask (supports wildcards with *)",
                    },
                    "devclass": {
                        "type": "string",
                        "description": "Development class filter",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="call_rfc_function",
            description="Call an RFC function with specified parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the RFC function to call",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Function parameters as key-value pairs",
                    },
                },
                "required": ["function_name"],
            },
        ),
        Tool(
            name="get_function_metadata",
            description="Get comprehensive metadata for an RFC function including parameters, types, and descriptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the RFC function",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for descriptions (EN, DE, PL, etc.)",
                        "default": "EN",
                    },
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Force refresh from SAP system (ignore cache)",
                    },
                },
                "required": ["function_name"],
            },
        ),
        Tool(
            name="search_rfc_functions",
            description="Search for RFC functions using keywords in names and descriptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords to search for)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_metadata_cache_stats",
            description="Get statistics about the RFC metadata cache",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="bulk_load_metadata",
            description="Load metadata for multiple RFC functions efficiently",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of RFC function names to load metadata for",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for descriptions (EN, DE, PL, etc.)",
                        "default": "EN",
                    },
                },
                "required": ["function_names"],
            },
        ),
        Tool(
            name="export_metadata_for_rag",
            description="Export RFC metadata in RAG-friendly format",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_file": {
                        "type": "string",
                        "description": "Output file path for RAG export",
                        "default": "rfc_metadata_rag.json",
                    }
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "rfc_system_info":
            result = await asyncio.get_event_loop().run_in_executor(
                None, _get_sap_client().get_system_info
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_rfc_functions":
            funcs_mask = arguments.get("funcs_mask")
            devclass = arguments.get("devclass")

            result = await asyncio.get_event_loop().run_in_executor(
                None, _get_sap_client().get_rfc_functions, funcs_mask, devclass
            )

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "call_rfc_function":
            function_name = arguments["function_name"]
            parameters = arguments.get("parameters", {})

            result = await asyncio.get_event_loop().run_in_executor(
                None, _get_sap_client().call_rfc_function, function_name, **parameters
            )

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_function_metadata":
            function_name = arguments["function_name"]
            language = arguments.get("language", "EN")
            force_refresh = arguments.get("force_refresh", False)

            metadata_mgr = _get_metadata_manager()
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                metadata_mgr.get_function_metadata,
                function_name,
                language,
                force_refresh,
            )

            return [
                TextContent(
                    type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "search_rfc_functions":
            query = arguments["query"]
            limit = arguments.get("limit", 20)

            metadata_mgr = _get_metadata_manager()
            result = await asyncio.get_event_loop().run_in_executor(
                None, metadata_mgr.search_functions, query, limit
            )

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"query": query, "limit": limit, "functions": result}, indent=2
                    ),
                )
            ]

        elif name == "get_metadata_cache_stats":
            metadata_mgr = _get_metadata_manager()
            result = await asyncio.get_event_loop().run_in_executor(
                None, metadata_mgr.get_cache_stats
            )

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "bulk_load_metadata":
            function_names = arguments["function_names"]
            language = arguments.get("language", "EN")

            metadata_mgr = _get_metadata_manager()
            result = await asyncio.get_event_loop().run_in_executor(
                None, metadata_mgr.bulk_load_metadata, function_names, language
            )

            return [
                TextContent(
                    type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "export_metadata_for_rag":
            output_file = arguments.get("output_file", "rfc_metadata_rag.json")

            metadata_mgr = _get_metadata_manager()
            await asyncio.get_event_loop().run_in_executor(
                None, metadata_mgr.export_for_rag, output_file
            )

            return [
                TextContent(type="text", text=f"Metadata exported to {output_file}")
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except SAPConnectionError as e:
        logger.error(f"SAP connection error in tool {name}: {e}")
        return [TextContent(type="text", text=f"SAP Connection Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sap-rfc-mcp-server",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=mcp.server.NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
