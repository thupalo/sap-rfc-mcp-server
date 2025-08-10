"""HTTP MCP Server for SAP RFC functions with streaming support."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool

# Handle imports for both module and direct execution
try:
    from .sap_client import SAPConnectionError, SAPRFCManager
except ImportError:
    # If relative import fails, this is likely direct execution
    import os
    import sys

    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from sap_rfc_mcp_server.sap_client import SAPConnectionError, SAPRFCManager
    except ImportError as e:
        print("[ERROR] Cannot import required modules!")
        print("")
        print("[INFO] Recommended usage:")
        print("   python -m sap_rfc_mcp_server.http_server [host] [port]")
        print("")
        print("[INFO] Or use the startup script:")
        print("   .\\tools\\start_sap_mcp_server.ps1 -Mode http")
        print("")
        print(f"[DEBUG] Import error details: {e}")
        sys.exit(1)


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SAP client lazily
sap_client = None


def _get_sap_client():
    """Get or create SAP client instance."""
    global sap_client
    if sap_client is None:
        sap_client = SAPRFCManager()
    return sap_client


# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    logger.info("Starting SAP RFC MCP HTTP Server...")
    yield
    logger.info("Shutting down SAP RFC MCP HTTP Server...")


app = FastAPI(
    title="SAP RFC MCP Server",
    description="HTTP MCP Server for SAP RFC functions with streaming support",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP server instance
mcp_server = Server("sap-rfc-mcp-http-server")


@mcp_server.list_tools()
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
                        "description": "Function name mask (use * for wildcards, e.g., 'RFC_*')",
                    },
                    "devclass": {
                        "type": "string",
                        "description": "Development class filter (use * for wildcards)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of functions to return",
                        "default": 100,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="call_rfc_function",
            description="Execute an arbitrary RFC function with parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the RFC function to call",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Parameters to pass to the RFC function",
                    },
                },
                "required": ["function_name"],
            },
        ),
        Tool(
            name="stream_rfc_table_data",
            description="Stream large table data from RFC functions in chunks",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the SAP table to read",
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of field names to retrieve",
                    },
                    "where_clause": {
                        "type": "string",
                        "description": "WHERE clause for filtering data",
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Number of rows per chunk",
                        "default": 1000,
                    },
                },
                "required": ["table_name"],
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
                        "description": "Force refresh metadata from SAP system",
                        "default": False,
                    },
                },
                "required": ["function_name"],
            },
        ),
        Tool(
            name="get_metadata_cache_stats",
            description="Get statistics about the RFC metadata cache",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="bulk_load_metadata",
            description="Bulk load metadata for multiple RFC functions",
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


@mcp_server.call_tool()
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
            limit = arguments.get("limit", 100)

            result = await asyncio.get_event_loop().run_in_executor(
                None, _get_sap_client().get_rfc_functions, funcs_mask, devclass
            )

            # Apply limit
            if limit and len(result) > limit:
                result = result[:limit]
                result.append({"INFO": f"Results limited to {limit} entries"})

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "call_rfc_function":
            function_name = arguments["function_name"]
            parameters = arguments.get("parameters", {})

            result = await asyncio.get_event_loop().run_in_executor(
                None, _get_sap_client().call_rfc_function, function_name, **parameters
            )

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "stream_rfc_table_data":
            # This tool returns a reference to the streaming endpoint
            table_name = arguments["table_name"]
            fields = arguments.get("fields", [])
            where_clause = arguments.get("where_clause", "")
            chunk_size = arguments.get("chunk_size", 1000)

            stream_url = f"/stream/table/{table_name}?chunk_size={chunk_size}"
            if fields:
                stream_url += f"&fields={','.join(fields)}"
            if where_clause:
                stream_url += f"&where={where_clause}"

            return [
                TextContent(
                    type="text",
                    text=f"Stream available at: {stream_url}\nUse HTTP GET to retrieve streaming data.",
                )
            ]

        elif name == "get_function_metadata":
            # Get metadata for a specific RFC function
            from .server import _get_metadata_manager

            try:
                metadata_manager = _get_metadata_manager()
                if metadata_manager is None:
                    return [
                        TextContent(
                            type="text", text="Error: Metadata manager not available"
                        )
                    ]

                function_name = arguments["function_name"]
                language = arguments.get("language", "EN")
                force_refresh = arguments.get("force_refresh", False)

                metadata = metadata_manager.get_function_metadata(
                    function_name, language=language, force_refresh=force_refresh
                )

                return [TextContent(type="text", text=json.dumps(metadata, indent=2))]
            except Exception as e:
                return [
                    TextContent(
                        type="text",
                        text=f"Error getting metadata for {function_name}: {str(e)}",
                    )
                ]

        elif name == "get_metadata_cache_stats":
            # Get metadata cache statistics
            from .server import _get_metadata_manager

            try:
                metadata_manager = _get_metadata_manager()
                if metadata_manager is None:
                    return [
                        TextContent(
                            type="text", text="Error: Metadata manager not available"
                        )
                    ]

                stats = metadata_manager.get_cache_stats()

                return [TextContent(type="text", text=json.dumps(stats, indent=2))]
            except Exception as e:
                return [
                    TextContent(
                        type="text", text=f"Error getting cache stats: {str(e)}"
                    )
                ]

        elif name == "bulk_load_metadata":
            # Bulk load metadata for multiple functions
            from .server import _get_metadata_manager

            try:
                metadata_manager = _get_metadata_manager()
                if metadata_manager is None:
                    return [
                        TextContent(
                            type="text", text="Error: Metadata manager not available"
                        )
                    ]

                function_names = arguments["function_names"]
                language = arguments.get("language", "EN")

                results = metadata_manager.bulk_load_metadata(
                    function_names, language=language
                )

                return [TextContent(type="text", text=json.dumps(results, indent=2))]
            except Exception as e:
                return [
                    TextContent(
                        type="text", text=f"Error bulk loading metadata: {str(e)}"
                    )
                ]

        elif name == "export_metadata_for_rag":
            # Export metadata for RAG
            from .server import _get_metadata_manager

            try:
                metadata_manager = _get_metadata_manager()
                if metadata_manager is None:
                    return [
                        TextContent(
                            type="text", text="Error: Metadata manager not available"
                        )
                    ]

                output_file = arguments.get("output_file", "rfc_metadata_rag.json")

                result = metadata_manager.export_for_rag(output_file)

                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [
                    TextContent(
                        type="text", text=f"Error exporting metadata for RAG: {str(e)}"
                    )
                ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except SAPConnectionError as e:
        logger.error(f"SAP connection error in tool {name}: {e}")
        return [TextContent(type="text", text=f"SAP Connection Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# HTTP Endpoints


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "server": "SAP RFC MCP HTTP Server",
        "version": "0.1.0",
        "description": "HTTP MCP Server for SAP RFC functions with streaming support",
        "endpoints": {
            "tools": "/mcp/tools",
            "call_tool": "/mcp/call_tool",
            "stream_table": "/stream/table/{table_name}",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Quick SAP connection test
        system_info = await asyncio.get_event_loop().run_in_executor(
            None, _get_sap_client().get_system_info
        )
        return {
            "status": "healthy",
            "sap_connection": "ok",
            "system": system_info.get("RFCSI_EXPORT", {}).get("RFCPROTO", "unknown"),
        }
    except Exception as e:
        return {"status": "unhealthy", "sap_connection": "error", "error": str(e)}


@app.get("/mcp/tools")
async def list_tools():
    """List available MCP tools."""
    tools = await handle_list_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
            for tool in tools
        ]
    }


@app.post("/mcp/call_tool")
async def call_tool(request: dict):
    """Call an MCP tool."""
    try:
        name = request.get("name")
        arguments = request.get("arguments", {})

        if not name:
            raise HTTPException(status_code=400, detail="Tool name is required")

        result = await handle_call_tool(name, arguments)
        return {
            "result": [
                {"type": content.type, "text": content.text} for content in result
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _call_rfc_read_table(
    table_name: str,
    fields: list[dict],
    options: list[dict],
    rowskips: int = 0,
    rowcount: int = 0,
):
    """Helper function to call RFC_READ_TABLE with proper parameters."""
    params = {
        "QUERY_TABLE": table_name,
        "DELIMITER": "|",
        "FIELDS": fields,
        "OPTIONS": options,
    }
    if rowskips > 0:
        params["ROWSKIPS"] = rowskips
    if rowcount > 0:
        params["ROWCOUNT"] = rowcount

    return _get_sap_client().call_rfc_function("RFC_READ_TABLE", **params)


async def stream_table_data(
    table_name: str,
    fields: list[str] = None,
    where_clause: str = "",
    chunk_size: int = 1000,
):
    """Stream table data in chunks."""
    try:
        logger.info(f"Starting stream for table {table_name}")

        # Prepare fields for RFC_READ_TABLE
        rfc_fields = []
        if fields:
            rfc_fields = [{"FIELDNAME": field} for field in fields]

        # Prepare options (WHERE clause)
        options = []
        if where_clause:
            options = [{"TEXT": where_clause}]

        # Initial call to get row count and structure
        initial_result = await asyncio.get_event_loop().run_in_executor(
            None,
            _call_rfc_read_table,
            table_name,
            rfc_fields,
            options,
            0,  # rowskips
            1,  # rowcount - just get one row to check structure
        )

        # Yield metadata first
        metadata = {
            "type": "metadata",
            "table_name": table_name,
            "fields": [field["FIELDNAME"] for field in rfc_fields]
            if rfc_fields
            else [],
            "structure": initial_result.get("FIELDS", []),
            "chunk_size": chunk_size,
        }
        yield f"data: {json.dumps(metadata)}\n\n"

        # Stream data in chunks
        offset = 0
        has_more = True
        chunk_number = 0

        while has_more:
            logger.info(f"Fetching chunk {chunk_number} starting at offset {offset}")

            chunk_result = await asyncio.get_event_loop().run_in_executor(
                None,
                _call_rfc_read_table,
                table_name,
                rfc_fields,
                options,
                offset,  # rowskips
                chunk_size,  # rowcount
            )

            data_rows = chunk_result.get("DATA", [])

            if not data_rows or len(data_rows) < chunk_size:
                has_more = False

            # Process and yield chunk
            if data_rows:
                field_names = [
                    field["FIELDNAME"] for field in chunk_result.get("FIELDS", [])
                ]
                processed_rows = []

                for row in data_rows:
                    values = row["WA"].split("|")
                    row_dict = {
                        field: value.strip()
                        for field, value in zip(field_names, values)
                    }
                    processed_rows.append(row_dict)

                chunk_data = {
                    "type": "chunk",
                    "chunk_number": chunk_number,
                    "row_count": len(processed_rows),
                    "data": processed_rows,
                    "has_more": has_more,
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"

            offset += chunk_size
            chunk_number += 1

        # Send completion message
        completion = {
            "type": "complete",
            "total_chunks": chunk_number,
            "message": f"Streaming complete for table {table_name}",
        }
        yield f"data: {json.dumps(completion)}\n\n"

    except Exception as e:
        error_data = {"type": "error", "error": str(e), "table_name": table_name}
        yield f"data: {json.dumps(error_data)}\n\n"


@app.get("/stream/table/{table_name}")
async def stream_table(
    table_name: str, fields: str = None, where: str = "", chunk_size: int = 1000
):
    """Stream table data endpoint."""
    field_list = fields.split(",") if fields else None

    return StreamingResponse(
        stream_table_data(table_name, field_list, where, chunk_size),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


def run_http_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the HTTP MCP server."""
    logger.info(f"Starting SAP RFC MCP HTTP Server on {host}:{port}")
    uvicorn.run(
        "sap_rfc_mcp_server.http_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    reload = "--reload" in sys.argv

    print(f"[*] Starting SAP RFC MCP HTTP Server on {host}:{port}")
    if reload:
        print("[*] Auto-reload enabled")

    run_http_server(host, port, reload)
