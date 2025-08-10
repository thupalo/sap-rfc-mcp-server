# SAP RFC MCP Server

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Model Context Protocol (MCP) server that provides seamless integration with SAP systems through RFC (Remote Function Call) connections. This server enables AI assistants and applications to interact with SAP functions, retrieve metadata, and perform operations with enhanced caching and version compatibility.

## 🚀 Features

### Core Functionality
- **SAP RFC Integration**: Direct connection to SAP systems using pyrfc
- **MCP Server**: Full Model Context Protocol implementation for AI assistant integration
- **HTTP Server**: RESTful API for web-based integrations
- **Version-Aware**: Automatic detection and compatibility with SAP R/3 4.5B through S/4HANA

### Enhanced Metadata Management
- **Intelligent Caching**: Persistent file-based cache with TTL and compression
- **Metadata Search**: Fast text-based search through cached RFC function metadata
- **Bulk Operations**: Parallel loading and processing of multiple functions
- **RAG Optimization**: Export metadata in formats optimized for Retrieval-Augmented Generation

### Advanced Development Tools
- **Port Management**: Automatic port conflict detection and resolution
- **Smart Startup**: Intelligent server startup with process management
- **VS Code Integration**: Complete development environment with tasks and snippets
- **Table Access Tools**: Enhanced SAP table operations with comprehensive error handling

### Language Support
- **Multi-Language**: Support for English, Polish, German, French, Spanish descriptions
- **Version-Aware Language Handling**: Automatic detection of SAP version and appropriate language code mapping
- **Legacy Compatibility**: Proper handling of single-letter language codes for older SAP systems (R/3 4.5B)

### Security & Configuration
- **Secure Configuration**: Encrypted storage of SAP connection parameters
- **Environment Variables**: Support for secure credential management
- **Connection Pooling**: Efficient connection management and reuse

## 📋 Requirements

### System Requirements
- Python 3.9 or higher
- SAP NetWeaver RFC SDK (for pyrfc)
- Access to SAP system with RFC connectivity

### SAP System Compatibility
- ✅ SAP R/3 4.5B and higher
- ✅ SAP ECC 6.0/6.1
- ✅ SAP ECC with Enhancement Packages
- ✅ SAP S/4HANA (all versions)

## 🛠 Installation

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/thupalo/sap-rfc-mcp-server.git
cd sap-rfc-mcp-server

# Automated development environment setup (includes SAP NetWeaver RFC SDK validation)
python tools/setup_dev.py
```

> **🔍 Enhanced Setup**: The automated setup now includes comprehensive SAP NetWeaver RFC SDK validation and provides detailed troubleshooting guidance if prerequisites are not met.

### Manual Installation

#### 1. Install SAP NetWeaver RFC SDK

Download and install the SAP NetWeaver RFC SDK from SAP Service Marketplace:
- [SAP NW RFC SDK Download](https://support.sap.com/en/product/connectors/nwrfcsdk.html)

#### 2. Install Python Package

```bash
# Clone the repository
git clone https://github.com/thupalo/sap-rfc-mcp-server.git
cd sap-rfc-mcp-server

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

#### 3. Configure SAP Connection

Create a `.env` file in the project root:

```env
# SAP Connection Parameters
SAP_ASHOST=your-sap-hostname
SAP_SYSNR=00
SAP_CLIENT=100
SAP_USER=your-username
SAP_PASSWD=your-password
SAP_LANG=EN

# Optional: Advanced Connection Settings
SAP_SAPROUTER=your-saprouter
SAP_POOL_SIZE=10
SAP_TRACE=0
```

## 🚀 Quick Start

### Smart Server Startup (Recommended)

```bash
# Intelligent startup with automatic port management
python tools/start_mcp_smart.py

# Alternative PowerShell startup
.\tools\start_sap_mcp_server.ps1 -Mode http -Port 8000
```

### Manual Server Startup

#### MCP Server (for AI Assistants)

```bash
# Start the MCP server
python -m sap_rfc_mcp_server.server

# The server will be available via stdio for MCP clients
```

#### HTTP Server (for Web Applications)

```bash
# Start the HTTP server
python -m sap_rfc_mcp_server.http_server 127.0.0.1 8000

# Server will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

### Port Management

```bash
# Check port availability
python tools/port_manager.py --suggest

# Check specific port
python tools/port_manager.py --check 8000

# Release MCP processes
python tools/port_manager.py --release-mcp 8000 8020
```

### Python API Usage

```python
from sap_rfc_mcp_server import SAPRFCManager, RFCMetadataManager

# Initialize SAP client
sap_client = SAPRFCManager()

# Call RFC function
result = sap_client.call_rfc_function(
    function_name="RFC_READ_TABLE",
    parameters={
        "QUERY_TABLE": "T001",
        "DELIMITER": "|",
        "ROWCOUNT": 10
    }
)

# Initialize metadata manager for enhanced capabilities
metadata_manager = RFCMetadataManager(
    connection_params=sap_client.config.to_connection_params()
)

# Get function metadata with caching
metadata = metadata_manager.get_function_metadata(
    "RFC_READ_TABLE",
    language="EN"
)

# Search for functions
search_results = metadata_manager.search_functions("table")

# Bulk load metadata
functions = ["RFC_READ_TABLE", "DDIF_FIELDINFO_GET", "RFC_GET_FUNCTION_INTERFACE_US"]
bulk_metadata = metadata_manager.bulk_load_metadata(functions, language="EN")
```

## 📖 Documentation

### 📁 Project Structure
```
sap-rfc-mcp-server/
├── sap_rfc_mcp_server/     # Main application package
├── tools/                  # Development tools and utilities
│   ├── start_mcp_smart.py         # Smart server startup
│   ├── port_manager.py            # Port management utility
│   ├── sap_dev_helper.py          # Development helper tools
│   ├── setup_dev.py               # Environment setup
│   └── README.md                  # Tools documentation
├── docs/                   # Technical documentation
│   ├── VSCODE_INTEGRATION_GUIDE.md
│   ├── PORT_MANAGEMENT_GUIDE.md
│   ├── TABLE_ACCESS_REPAIR_SUMMARY.md
│   └── README.md                  # Documentation index
├── tests/                  # Unit and integration tests
├── examples/               # Usage examples
└── README.md              # This file
```

### 🛠️ Development Tools
- **[Tools README](tools/README.md)** - Complete guide to development utilities
- **[Port Management Guide](docs/PORT_MANAGEMENT_GUIDE.md)** - Server and port management
- **[VS Code Integration](docs/VSCODE_INTEGRATION_GUIDE.md)** - Development environment setup

### 📚 Technical Documentation
- **[Documentation Index](docs/README.md)** - Complete documentation overview
- **[Table Access Guide](docs/TABLE_ACCESS_REPAIR_SUMMARY.md)** - SAP table operations
- **[Integration Success](docs/INTEGRATION_SUCCESS.md)** - Project achievements

## 🧪 Testing

### Automated Testing

```bash
# Test development tools
python tools/sap_dev_helper.py --system-info
python tools/sap_dev_helper.py --test-table T000

# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=sap_rfc_mcp_server
```

### Development Environment Testing

```bash
# Test VS Code integration
python tools/test_vscode_integration.py

# Verify SAP connection
python tools/test_direct_sap.py

# Test MCP server functionality
python tools/test_metadata_stdio.py
```

## 🔧 Development

### Quick Development Setup

```bash
# Automated setup (recommended)
python tools/setup_dev.py

# Manual VS Code setup
code .  # Open in VS Code
# Select Python interpreter: ./venv/Scripts/python.exe
```

### Development Tools Usage

```bash
# Port management
python tools/port_manager.py --help

# Development helpers
python tools/sap_dev_helper.py --help

# Smart server startup
python tools/start_mcp_smart.py
```

### Code Quality

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run code formatting
black sap_rfc_mcp_server tests
isort sap_rfc_mcp_server tests

# Type checking
mypy sap_rfc_mcp_server
```

### Project Structure

```
sap-rfc-mcp-server/
├── sap_rfc_mcp_server/         # Main package
│   ├── __init__.py
│   ├── server.py               # MCP server implementation
│   ├── http_server.py          # HTTP server implementation
│   ├── sap_client.py           # SAP RFC client
│   ├── metadata_manager.py     # Enhanced metadata management
│   ├── metadata_cache.py       # Persistent caching system
│   ├── config.py               # Configuration management
│   ├── secure_config.py        # Secure configuration handling
│   └── sap_security_manager.py # Security utilities
├── tests/                      # Test suite
├── examples/                   # Usage examples
├── docs/                       # Documentation
├── cache/                      # Default cache directory
├── pyproject.toml             # Project configuration
├── README.md                  # This file
├── LICENSE                    # MIT License
└── CHANGELOG.md              # Version history
```

## 📊 Performance

### Caching Benefits
- **First Call**: Direct SAP RFC call (~200-500ms)
- **Cached Call**: File-based cache retrieval (~1-5ms)
- **Search**: Indexed text search (~1-10ms)
- **Bulk Operations**: Parallel processing with connection pooling

### Memory Usage
- **Base Server**: ~50MB
- **With Cache**: +10-50MB (depending on cached functions)
- **Connection Pool**: +5-20MB per connection

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues
- [SAP Connection Problems](docs/troubleshooting.md#connection-issues)
- [RFC SDK Installation](docs/troubleshooting.md#rfc-sdk)
- [Performance Optimization](docs/troubleshooting.md#performance)

### Getting Help
- 📧 Email: sap-rfc-mcp@example.com
- 🐛 [Report Issues](https://github.com/thupalo/sap-rfc-mcp-server/issues)
- 💬 [Discussions](https://github.com/thupalo/sap-rfc-mcp-server/discussions)

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## 🏆 Acknowledgments

- SAP AG for the RFC SDK and documentation
- The pyrfc project for Python RFC connectivity
- The Model Context Protocol community
- All contributors who have helped improve this project

---

**Note**: This is not an official SAP product. SAP and other SAP products mentioned herein are trademarks or registered trademarks of SAP SE in Germany and other countries.
