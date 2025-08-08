"""HTTP MCP Server for SAP RFC functions with streaming support."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
)
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .sap_client import SAPRFCManager, SAPConnectionError


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
    lifespan=lifespan
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
                        "description": "Function name mask (use * for wildcards, e.g., 'RFC_*')"
                    },
                    "devclass": {
                        "type": "string", 
                        "description": "Development class filter (use * for wildcards)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of functions to return",
                        "default": 100
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
        ),
        Tool(
            name="stream_rfc_table_data",
            description="Stream large table data from RFC functions in chunks",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the SAP table to read"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of field names to retrieve"
                    },
                    "where_clause": {
                        "type": "string",
                        "description": "WHERE clause for filtering data"
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Number of rows per chunk",
                        "default": 1000
                    }
                },
                "required": ["table_name"]
            }
        )
    ]


@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "rfc_system_info":
            result = await asyncio.get_event_loop().run_in_executor(
                None, _get_sap_client().get_system_info
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
            limit = arguments.get("limit", 100)
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, _get_sap_client().get_rfc_functions, funcs_mask, devclass
            )
            
            # Apply limit
            if limit and len(result) > limit:
                result = result[:limit]
                result.append({"INFO": f"Results limited to {limit} entries"})
            
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
                None, _get_sap_client().call_rfc_function, function_name, **parameters
            )
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        
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
                    text=f"Stream available at: {stream_url}\nUse HTTP GET to retrieve streaming data."
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
            "health": "/health"
        }
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
            "system": system_info.get("RFCSI_EXPORT", {}).get("RFCPROTO", "unknown")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "sap_connection": "error",
            "error": str(e)
        }


@app.get("/mcp/tools")
async def list_tools():
    """List available MCP tools."""
    tools = await handle_list_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
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
                {
                    "type": content.type,
                    "text": content.text
                }
                for content in result
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _call_rfc_read_table(table_name: str, fields: List[dict], options: List[dict], 
                        rowskips: int = 0, rowcount: int = 0):
    """Helper function to call RFC_READ_TABLE with proper parameters."""
    params = {
        "QUERY_TABLE": table_name,
        "DELIMITER": "|",
        "FIELDS": fields,
        "OPTIONS": options
    }
    if rowskips > 0:
        params["ROWSKIPS"] = rowskips
    if rowcount > 0:
        params["ROWCOUNT"] = rowcount
    
    return _get_sap_client().call_rfc_function("RFC_READ_TABLE", **params)


async def stream_table_data(table_name: str, fields: List[str] = None, 
                           where_clause: str = "", chunk_size: int = 1000):
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
            1   # rowcount - just get one row to check structure
        )
        
        # Yield metadata first
        metadata = {
            "type": "metadata",
            "table_name": table_name,
            "fields": [field["FIELDNAME"] for field in rfc_fields] if rfc_fields else [],
            "structure": initial_result.get("FIELDS", []),
            "chunk_size": chunk_size
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
                offset,     # rowskips
                chunk_size  # rowcount
            )
            
            data_rows = chunk_result.get("DATA", [])
            
            if not data_rows or len(data_rows) < chunk_size:
                has_more = False
            
            # Process and yield chunk
            if data_rows:
                field_names = [field["FIELDNAME"] for field in chunk_result.get("FIELDS", [])]
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
                    "has_more": has_more
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
            
            offset += chunk_size
            chunk_number += 1
        
        # Send completion message
        completion = {
            "type": "complete",
            "total_chunks": chunk_number,
            "message": f"Streaming complete for table {table_name}"
        }
        yield f"data: {json.dumps(completion)}\n\n"
        
    except Exception as e:
        error_data = {
            "type": "error",
            "error": str(e),
            "table_name": table_name
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@app.get("/stream/table/{table_name}")
async def stream_table(
    table_name: str,
    fields: str = None,
    where: str = "",
    chunk_size: int = 1000
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
        }
    )


def run_http_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the HTTP MCP server."""
    logger.info(f"Starting SAP RFC MCP HTTP Server on {host}:{port}")
    uvicorn.run(
        "sap_rfc_mcp_server.http_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    reload = "--reload" in sys.argv
    
    run_http_server(host, port, reload)
