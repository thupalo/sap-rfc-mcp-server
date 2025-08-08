"""
SAP RFC MCP Server - Model Context Protocol server for SAP RFC function calls.

This package provides a comprehensive solution for integrating SAP systems with
AI assistants and applications through the Model Context Protocol (MCP). It includes
enhanced metadata management, persistent caching, and version-aware compatibility
with SAP systems from R/3 4.5B through S/4HANA.

Key Components:
- MCP Server: For AI assistant integration
- HTTP Server: For web application integration  
- SAP Client: Core RFC connectivity
- Metadata Manager: Enhanced metadata handling with caching
- Security Manager: Secure configuration and encryption

Example Usage:
    >>> from sap_rfc_mcp_server import SAPRFCManager, RFCMetadataManager
    >>> 
    >>> # Initialize SAP client
    >>> client = SAPRFCManager()
    >>> 
    >>> # Call RFC function
    >>> result = client.call_rfc_function("RFC_READ_TABLE", {
    ...     "QUERY_TABLE": "T001",
    ...     "ROWCOUNT": 10
    ... })
    >>> 
    >>> # Initialize metadata manager
    >>> metadata_manager = RFCMetadataManager(
    ...     client.config.to_connection_params()
    ... )
    >>> 
    >>> # Get function metadata with caching
    >>> metadata = metadata_manager.get_function_metadata("RFC_READ_TABLE")
"""

from .sap_client import SAPRFCManager, SAPConnectionError
from .config import SAPConfig
from .secure_config import SAPConfigManager

# Import metadata components if available
try:
    from .metadata_manager import RFCMetadataManager
    from .metadata_cache import RFCMetadataCache
except ImportError:
    # Metadata components not available
    RFCMetadataManager = None
    RFCMetadataCache = None

# Import server components
try:
    from .server import main as run_mcp_server
except ImportError:
    run_mcp_server = None

try:
    from .http_server import run_http_server
except ImportError:
    run_http_server = None

# Package metadata
__version__ = "1.0.0"
__author__ = "SAP RFC MCP Server Team"
__email__ = "sap-rfc-mcp@example.com"
__description__ = "Model Context Protocol server for SAP RFC function calls"
__url__ = "https://github.com/thupalo/sap-rfc-mcp-server"

# Public API
__all__ = [
    # Core components
    "SAPRFCManager",
    "SAPConnectionError", 
    "SAPConfig",
    "SAPConfigManager",
    
    # Metadata components (if available)
    "RFCMetadataManager",
    "RFCMetadataCache",
    
    # Server functions (if available)
    "run_mcp_server",
    "run_http_server",
    
    # Package info
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__url__",
]

# Version info tuple
VERSION = tuple(map(int, __version__.split('.')))

def get_version():
    """Get the package version string."""
    return __version__

def get_version_info():
    """Get detailed version information."""
    return {
        'version': __version__,
        'version_tuple': VERSION,
        'description': __description__,
        'author': __author__,
        'url': __url__
    }

# Feature availability checks
def has_metadata_manager():
    """Check if metadata manager is available."""
    return RFCMetadataManager is not None

def has_mcp_server():
    """Check if MCP server is available."""
    return run_mcp_server is not None

def has_http_server():
    """Check if HTTP server is available."""
    return run_http_server is not None

# Convenience functions
def create_sap_client(**kwargs):
    """
    Create a configured SAP client.
    
    Args:
        **kwargs: SAP connection parameters
        
    Returns:
        SAPRFCManager: Configured SAP client
    """
    return SAPRFCManager(**kwargs)

def create_metadata_manager(connection_params=None, **kwargs):
    """
    Create a metadata manager instance.
    
    Args:
        connection_params: SAP connection parameters dict
        **kwargs: Additional metadata manager parameters
        
    Returns:
        RFCMetadataManager: Configured metadata manager
        
    Raises:
        ImportError: If metadata manager is not available
    """
    if RFCMetadataManager is None:
        raise ImportError("Metadata manager not available")
    
    if connection_params is None:
        # Try to get connection params from default client
        client = SAPRFCManager()
        connection_params = client.config.to_connection_params()
    
    return RFCMetadataManager(connection_params, **kwargs)
