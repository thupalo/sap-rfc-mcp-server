#!/usr/bin/env python3
"""
MCP Client Architecture Analysis Tool

This tool analyzes the current MCP server architecture and provides recommendations
for moving implementation logic from server to client where possible to keep
the server code minimal and focused on core MCP protocol handling.
"""

import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Set

logger = logging.getLogger(__name__)


class MCPArchitectureAnalyzer:
    """Analyzes MCP server architecture for client-side optimization opportunities."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.server_code = {}
        self.analysis_results = {}
        
    def load_server_code(self):
        """Load and parse server code files."""
        server_files = [
            "sap_rfc_mcp_server/server.py",
            "sap_rfc_mcp_server/http_server.py",
            "sap_rfc_mcp_server/sap_client.py",
            "sap_rfc_mcp_server/metadata_manager.py",
            "sap_rfc_mcp_server/rfc_table_reader.py",
        ]
        
        for file_path in server_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.server_code[file_path] = {
                        'content': content,
                        'ast': ast.parse(content),
                        'lines': len(content.splitlines())
                    }
                    
    def analyze_server_tools(self) -> Dict[str, Any]:
        """Analyze current server tools and their complexity."""
        server_file = "sap_rfc_mcp_server/server.py"
        if server_file not in self.server_code:
            return {}
            
        ast_tree = self.server_code[server_file]['ast']
        tools = {}
        
        # Find the list_tools function
        for node in ast.walk(ast_tree):
            if (isinstance(node, ast.FunctionDef) and 
                node.name == "handle_list_tools"):
                # Extract tool definitions
                for tool_node in ast.walk(node):
                    if isinstance(tool_node, ast.Call) and hasattr(tool_node.func, 'id') and tool_node.func.id == 'Tool':
                        tool_info = self._extract_tool_info(tool_node)
                        if tool_info:
                            tools[tool_info['name']] = tool_info
                            
        # Find the call_tool function to analyze implementation complexity
        for node in ast.walk(ast_tree):
            if (isinstance(node, ast.FunctionDef) and 
                node.name == "handle_call_tool"):
                self._analyze_tool_implementations(node, tools)
                
        return tools
    
    def _extract_tool_info(self, tool_node: ast.Call) -> Dict[str, Any]:
        """Extract tool information from Tool() call."""
        tool_info = {}
        
        for keyword in tool_node.keywords:
            if keyword.arg == 'name' and isinstance(keyword.value, ast.Constant):
                tool_info['name'] = keyword.value.value
            elif keyword.arg == 'description' and isinstance(keyword.value, ast.Constant):
                tool_info['description'] = keyword.value.value
                
        return tool_info
    
    def _analyze_tool_implementations(self, call_tool_node: ast.FunctionDef, tools: Dict):
        """Analyze tool implementation complexity."""
        # Find elif blocks for each tool
        for node in ast.walk(call_tool_node):
            if isinstance(node, ast.If):
                self._analyze_tool_condition(node, tools)
    
    def _analyze_tool_condition(self, if_node: ast.If, tools: Dict):
        """Analyze individual tool conditions and implementations."""
        # This is a simplified analysis - in practice, would need more sophisticated AST parsing
        pass
    
    def analyze_client_movement_opportunities(self) -> Dict[str, Any]:
        """Identify opportunities to move logic from server to client."""
        opportunities = {
            "data_processing": [],
            "business_logic": [],
            "caching": [],
            "validation": [],
            "formatting": []
        }
        
        # Analyze current server tools
        tools = self.analyze_server_tools()
        
        for tool_name, tool_info in tools.items():
            opportunities.update(self._analyze_tool_for_client_movement(tool_name, tool_info))
            
        return opportunities
    
    def _analyze_tool_for_client_movement(self, tool_name: str, tool_info: Dict) -> Dict[str, List]:
        """Analyze specific tool for client movement opportunities."""
        opportunities = {
            "data_processing": [],
            "business_logic": [],
            "caching": [],
            "validation": [],
            "formatting": []
        }
        
        # Analysis based on tool patterns
        if "search" in tool_name.lower():
            opportunities["business_logic"].append({
                "tool": tool_name,
                "opportunity": "Search filtering and ranking logic",
                "benefit": "Reduced server load, customizable search"
            })
            
        if "metadata" in tool_name.lower():
            opportunities["caching"].append({
                "tool": tool_name,
                "opportunity": "Client-side metadata caching",
                "benefit": "Reduced network calls, faster responses"
            })
            
        if "export" in tool_name.lower():
            opportunities["data_processing"].append({
                "tool": tool_name,
                "opportunity": "Client-side data transformation",
                "benefit": "Reduced server processing, customizable formats"
            })
            
        return opportunities
    
    def generate_minimal_server_design(self) -> Dict[str, Any]:
        """Generate design for minimal MCP server."""
        return {
            "core_server_functions": [
                "RFC connection management",
                "Basic RFC function calls",
                "Error handling and logging",
                "MCP protocol compliance"
            ],
            "client_side_functions": [
                "Data formatting and transformation",
                "Business logic processing",
                "Caching and optimization",
                "Complex queries and filtering",
                "Export and reporting",
                "Validation and preprocessing"
            ],
            "interface_design": {
                "server_tools": [
                    {
                        "name": "call_rfc_function",
                        "description": "Direct RFC function call - minimal processing",
                        "complexity": "low"
                    },
                    {
                        "name": "get_connection_info",
                        "description": "SAP system information",
                        "complexity": "low"
                    },
                    {
                        "name": "list_available_functions",
                        "description": "Basic function enumeration",
                        "complexity": "low"
                    }
                ],
                "client_utilities": [
                    {
                        "name": "RFCMetadataClient",
                        "description": "Client-side metadata management",
                        "functions": ["caching", "search", "export"]
                    },
                    {
                        "name": "RFCTableClient", 
                        "description": "Client-side table operations",
                        "functions": ["pagination", "filtering", "formatting"]
                    },
                    {
                        "name": "RFCQueryBuilder",
                        "description": "Client-side query construction",
                        "functions": ["validation", "optimization", "templating"]
                    }
                ]
            }
        }
    
    def create_stdio_minimal_server(self) -> str:
        """Generate minimal STDIO server implementation."""
        return """#!/usr/bin/env python3
\"\"\"
Minimal MCP Server for SAP RFC - STDIO Transport
Focuses on core MCP protocol and basic RFC connectivity.
\"\"\"

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
    \"\"\"Get or create SAP client instance.\"\"\"
    global sap_client
    if sap_client is None:
        sap_client = SAPRFCManager()
    return sap_client

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    \"\"\"List minimal set of SAP RFC tools.\"\"\"
    return [
        Tool(
            name="call_rfc_function",
            description="Call any RFC function with parameters - raw results",
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
            description="Get basic SAP system information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="ping_connection",
            description="Test SAP connection status",
            inputSchema={
                "type": "object", 
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    \"\"\"Handle tool calls with minimal processing.\"\"\"
    try:
        client = _get_sap_client()
        
        if name == "call_rfc_function":
            function_name = arguments["function_name"]
            parameters = arguments.get("parameters", {})
            
            # Direct RFC call - no processing
            result = await asyncio.get_event_loop().run_in_executor(
                None, client.call_rfc_function, function_name, **parameters
            )
            
            return [TextContent(
                type="text", 
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
            
        elif name == "get_system_info":
            result = await asyncio.get_event_loop().run_in_executor(
                None, client.get_system_info
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "ping_connection":
            # Simple connection test
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, client.get_system_info
                )
                result = {"status": "connected", "timestamp": str(asyncio.get_event_loop().time())}
            except Exception as e:
                result = {"status": "disconnected", "error": str(e)}
                
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except SAPConnectionError as e:
        return [TextContent(type="text", text=f"SAP Connection Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    \"\"\"Main entry point for the minimal MCP server.\"\"\"
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
"""
    
    def generate_client_utilities(self) -> Dict[str, str]:
        """Generate client-side utility classes."""
        return {
            "rfc_metadata_client.py": self._generate_metadata_client(),
            "rfc_table_client.py": self._generate_table_client(),
            "rfc_query_builder.py": self._generate_query_builder(),
            "mcp_sap_client.py": self._generate_mcp_client()
        }
    
    def _generate_metadata_client(self) -> str:
        """Generate metadata client implementation."""
        return '''"""
Client-side RFC Metadata Management
Handles caching, searching, and processing of SAP RFC metadata.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any


class RFCMetadataClient:
    """Client-side RFC metadata management with local caching."""
    
    def __init__(self, cache_dir: str = "cache", mcp_client=None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.mcp_client = mcp_client
        self.db_path = self.cache_dir / "rfc_metadata.db"
        self._init_cache_db()
    
    def _init_cache_db(self):
        """Initialize SQLite cache database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS function_metadata (
                function_name TEXT PRIMARY KEY,
                metadata TEXT,
                language TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_index (
                function_name TEXT,
                search_text TEXT,
                FOREIGN KEY (function_name) REFERENCES function_metadata(function_name)
            )
        """)
        conn.commit()
        conn.close()
    
    async def get_function_metadata(self, function_name: str, language: str = "EN") -> Dict:
        """Get function metadata with client-side caching."""
        # Check cache first
        cached = self._get_cached_metadata(function_name, language)
        if cached:
            return cached
            
        # Fetch from server via MCP
        if self.mcp_client:
            raw_result = await self.mcp_client.call_tool("call_rfc_function", {
                "function_name": "RFC_GET_FUNCTION_INTERFACE",
                "parameters": {"FUNCNAME": function_name, "LANGUAGE": language}
            })
            
            # Process and cache the result
            processed = self._process_metadata(raw_result, function_name, language)
            self._cache_metadata(function_name, language, processed)
            return processed
            
        return {}
    
    def search_functions(self, query: str, limit: int = 20) -> List[Dict]:
        """Client-side function search using local index."""
        conn = sqlite3.connect(self.db_path)
        results = conn.execute("""
            SELECT DISTINCT f.function_name, f.metadata 
            FROM function_metadata f
            JOIN search_index s ON f.function_name = s.function_name
            WHERE s.search_text LIKE ? 
            LIMIT ?
        """, (f"%{query.lower()}%", limit)).fetchall()
        conn.close()
        
        return [{"name": name, "metadata": json.loads(metadata)} 
                for name, metadata in results]
    
    def _get_cached_metadata(self, function_name: str, language: str) -> Optional[Dict]:
        """Get metadata from cache."""
        conn = sqlite3.connect(self.db_path)
        result = conn.execute(
            "SELECT metadata FROM function_metadata WHERE function_name = ? AND language = ?",
            (function_name, language)
        ).fetchone()
        conn.close()
        
        return json.loads(result[0]) if result else None
    
    def _cache_metadata(self, function_name: str, language: str, metadata: Dict):
        """Cache metadata and update search index."""
        conn = sqlite3.connect(self.db_path)
        
        # Cache metadata
        conn.execute("""
            INSERT OR REPLACE INTO function_metadata (function_name, metadata, language)
            VALUES (?, ?, ?)
        """, (function_name, json.dumps(metadata), language))
        
        # Update search index
        search_text = " ".join([
            function_name.lower(),
            metadata.get("description", "").lower(),
            " ".join(p.get("name", "") for p in metadata.get("parameters", []))
        ])
        
        conn.execute("DELETE FROM search_index WHERE function_name = ?", (function_name,))
        conn.execute("INSERT INTO search_index (function_name, search_text) VALUES (?, ?)",
                    (function_name, search_text))
        
        conn.commit()
        conn.close()
    
    def _process_metadata(self, raw_result: Dict, function_name: str, language: str) -> Dict:
        """Process raw RFC metadata into structured format."""
        # Client-side processing logic here
        return {
            "function_name": function_name,
            "language": language,
            "description": "Processed description",
            "parameters": [],
            "processed_by": "client"
        }
'''
    
    def _generate_table_client(self) -> str:
        """Generate table client implementation."""
        return '''"""
Client-side RFC Table Operations
Handles table reading, pagination, and data processing.
"""

import json
from typing import Dict, List, Optional, Any


class RFCTableClient:
    """Client-side table operations with smart chunking and processing."""
    
    def __init__(self, mcp_client=None):
        self.mcp_client = mcp_client
        self.chunk_size = 1000  # Default chunk size
        
    async def read_table_smart(self, 
                              table_name: str,
                              fields: List[str] = None,
                              where_conditions: List[str] = None,
                              max_rows: int = 10000) -> Dict[str, Any]:
        """Smart table reading with client-side optimization."""
        
        # Client-side field optimization
        if fields:
            fields = self._optimize_field_selection(table_name, fields)
        
        # Client-side where clause optimization  
        if where_conditions:
            where_conditions = self._optimize_where_conditions(where_conditions)
            
        # Chunked reading for large datasets
        all_data = []
        rows_read = 0
        skip_rows = 0
        
        while rows_read < max_rows:
            chunk_size = min(self.chunk_size, max_rows - rows_read)
            
            # Call minimal server function
            chunk_result = await self.mcp_client.call_tool("call_rfc_function", {
                "function_name": "RFC_READ_TABLE",
                "parameters": {
                    "QUERY_TABLE": table_name,
                    "DELIMITER": "|",
                    "FIELDS": [{"FIELDNAME": f} for f in (fields or [])],
                    "OPTIONS": [{"TEXT": cond} for cond in (where_conditions or [])],
                    "ROWCOUNT": chunk_size,
                    "ROWSKIPS": skip_rows
                }
            })
            
            # Client-side processing
            processed_chunk = self._process_table_chunk(chunk_result)
            
            if not processed_chunk["data"]:
                break  # No more data
                
            all_data.extend(processed_chunk["data"])
            rows_read += len(processed_chunk["data"])
            skip_rows += len(processed_chunk["data"])
            
        return {
            "table_name": table_name,
            "total_rows": len(all_data),
            "data": all_data,
            "processed_by": "client"
        }
    
    def _optimize_field_selection(self, table_name: str, fields: List[str]) -> List[str]:
        """Client-side field selection optimization."""
        # Remove duplicates, optimize order, etc.
        return list(dict.fromkeys(fields))  # Remove duplicates preserving order
    
    def _optimize_where_conditions(self, conditions: List[str]) -> List[str]:
        """Client-side where clause optimization."""
        # Optimize conditions, remove redundancies, etc.
        return conditions
    
    def _process_table_chunk(self, raw_result: Dict) -> Dict:
        """Process raw table data chunk."""
        # Client-side data processing
        result_text = raw_result  # Simplified
        
        return {
            "data": [],  # Processed data
            "fields": [],  # Field metadata
            "processed_by": "client"
        }
    
    async def get_table_structure(self, table_name: str, language: str = "EN") -> Dict:
        """Get table structure with client-side caching."""
        # Use minimal server call and process client-side
        raw_result = await self.mcp_client.call_tool("call_rfc_function", {
            "function_name": "DDIF_FIELDINFO_GET",
            "parameters": {
                "TABNAME": table_name,
                "LANGU": language
            }
        })
        
        return self._process_table_structure(raw_result, table_name)
    
    def _process_table_structure(self, raw_result: Dict, table_name: str) -> Dict:
        """Process raw table structure data."""
        return {
            "table_name": table_name,
            "fields": [],  # Processed field information
            "processed_by": "client"
        }
'''
    
    def _generate_query_builder(self) -> str:
        """Generate query builder implementation."""
        return '''"""
Client-side RFC Query Builder
Constructs and validates RFC function calls.
"""

from typing import Dict, List, Any, Optional


class RFCQueryBuilder:
    """Client-side RFC query construction and validation."""
    
    def __init__(self, metadata_client=None):
        self.metadata_client = metadata_client
        
    def build_rfc_call(self, 
                      function_name: str,
                      parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build validated RFC function call."""
        
        # Client-side validation
        if self.metadata_client:
            metadata = self.metadata_client.get_cached_metadata(function_name)
            if metadata:
                parameters = self._validate_parameters(parameters or {}, metadata)
        
        return {
            "function_name": function_name,
            "parameters": parameters or {},
            "validated": True
        }
    
    def build_table_query(self,
                         table_name: str,
                         fields: List[str] = None,
                         where_conditions: List[str] = None,
                         max_rows: int = 100) -> Dict[str, Any]:
        """Build optimized table query."""
        
        return {
            "function_name": "RFC_READ_TABLE",
            "parameters": {
                "QUERY_TABLE": table_name,
                "DELIMITER": "|",
                "FIELDS": [{"FIELDNAME": f} for f in (fields or [])],
                "OPTIONS": [{"TEXT": cond} for cond in (where_conditions or [])],
                "ROWCOUNT": max_rows
            }
        }
    
    def _validate_parameters(self, parameters: Dict, metadata: Dict) -> Dict:
        """Validate parameters against function metadata."""
        # Client-side parameter validation
        return parameters
'''
    
    def _generate_mcp_client(self) -> str:
        """Generate MCP client wrapper."""
        return '''"""
MCP SAP Client - High-level client for SAP RFC MCP server
Combines minimal server calls with rich client-side processing.
"""

import asyncio
import json
import subprocess
from typing import Dict, List, Any, Optional

from .rfc_metadata_client import RFCMetadataClient
from .rfc_table_client import RFCTableClient
from .rfc_query_builder import RFCQueryBuilder


class MCPSAPClient:
    """High-level client for SAP RFC operations via minimal MCP server."""
    
    def __init__(self, server_command: List[str] = None):
        self.server_command = server_command or [
            "python", "-m", "sap_rfc_mcp_server.minimal_server"
        ]
        self.process = None
        
        # Client-side components
        self.metadata = RFCMetadataClient(mcp_client=self)
        self.tables = RFCTableClient(mcp_client=self)
        self.query_builder = RFCQueryBuilder(metadata_client=self.metadata)
        
    async def connect(self):
        """Start MCP server process and establish connection."""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize MCP session
        await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}},
                "clientInfo": {"name": "sap-client", "version": "1.0.0"}
            }
        })
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
    
    async def call_tool(self, name: str, arguments: Dict = None) -> Any:
        """Call MCP tool on server."""
        response = await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments or {}
            }
        })
        
        return response.get("result", {})
    
    async def call_rfc_function(self, function_name: str, **parameters) -> Dict:
        """High-level RFC function call with client-side optimization."""
        
        # Use query builder for validation
        query = self.query_builder.build_rfc_call(function_name, parameters)
        
        # Call minimal server
        result = await self.call_tool("call_rfc_function", {
            "function_name": query["function_name"],
            "parameters": query["parameters"]
        })
        
        return result
    
    async def read_table(self, table_name: str, **kwargs) -> Dict:
        """High-level table reading with client-side optimization."""
        return await self.tables.read_table_smart(table_name, **kwargs)
    
    async def get_function_metadata(self, function_name: str, language: str = "EN") -> Dict:
        """Get function metadata with client-side caching."""
        return await self.metadata.get_function_metadata(function_name, language)
    
    async def search_functions(self, query: str, limit: int = 20) -> List[Dict]:
        """Search functions using client-side index."""
        return self.metadata.search_functions(query, limit)
    
    async def _send_mcp_request(self, request: Dict) -> Dict:
        """Send MCP request to server and get response."""
        if not self.process:
            raise RuntimeError("Not connected to server")
            
        # Send request
        request_data = json.dumps(request) + "\\n"
        self.process.stdin.write(request_data.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_data = await self.process.stdout.readline()
        return json.loads(response_data.decode())
'''
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete architecture analysis."""
        self.load_server_code()
        
        tools = self.analyze_server_tools()
        opportunities = self.analyze_client_movement_opportunities()
        minimal_design = self.generate_minimal_server_design()
        client_utilities = self.generate_client_utilities()
        minimal_server = self.create_stdio_minimal_server()
        
        return {
            "current_analysis": {
                "server_files": list(self.server_code.keys()),
                "total_lines": sum(data['lines'] for data in self.server_code.values()),
                "tools_count": len(tools),
                "tools": tools
            },
            "optimization_opportunities": opportunities,
            "minimal_server_design": minimal_design,
            "recommended_architecture": {
                "server_responsibilities": [
                    "MCP protocol handling",
                    "SAP RFC connection management", 
                    "Basic RFC function calls",
                    "Connection status and health"
                ],
                "client_responsibilities": [
                    "Data processing and transformation",
                    "Metadata caching and search",
                    "Business logic and validation",
                    "Complex query optimization",
                    "Export and formatting operations"
                ]
            },
            "implementation": {
                "minimal_server_code": minimal_server,
                "client_utilities": client_utilities
            }
        }


def main():
    """Run MCP architecture analysis."""
    analyzer = MCPArchitectureAnalyzer()
    results = analyzer.run_analysis()
    
    print("📊 MCP Server Architecture Analysis")
    print("=" * 50)
    
    print(f"\\n📈 Current Server Analysis:")
    print(f"  - Files analyzed: {len(results['current_analysis']['server_files'])}")
    print(f"  - Total lines of code: {results['current_analysis']['total_lines']:,}")
    print(f"  - Tools implemented: {results['current_analysis']['tools_count']}")
    
    print(f"\\n🎯 Optimization Opportunities:")
    opportunities = results['optimization_opportunities']
    for category, items in opportunities.items():
        if items:
            print(f"  - {category.title()}: {len(items)} opportunities")
    
    print(f"\\n🏗️  Recommended Architecture:")
    design = results['recommended_architecture']
    print(f"  Server responsibilities: {len(design['server_responsibilities'])}")
    print(f"  Client responsibilities: {len(design['client_responsibilities'])}")
    
    print(f"\\n💡 Benefits of Client-Side Architecture:")
    print("  ✅ Reduced server complexity and maintenance")
    print("  ✅ Better scalability - server handles only core functions")
    print("  ✅ Improved client customization and flexibility")
    print("  ✅ Faster responses through client-side caching")
    print("  ✅ Reduced network traffic for common operations")
    
    # Save detailed results
    output_file = Path(__file__).parent / "mcp_architecture_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\\n📁 Detailed analysis saved to: {output_file}")


if __name__ == "__main__":
    main()
