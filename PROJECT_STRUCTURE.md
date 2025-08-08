# 📂 Project Structure Overview

This document explains the structure and organization of the SAP RFC MCP Server project.

## 🏗️ Directory Structure

```
sap-rfc-mcp-server/
├── 📋 Project Configuration
│   ├── pyproject.toml           # Python project configuration & dependencies
│   ├── .gitignore              # Git ignore patterns
│   ├── .pre-commit-config.yaml # Pre-commit hooks configuration
│   └── .env.template           # Environment variables template
│
├── 📚 Documentation
│   ├── README.md               # Main project documentation
│   ├── QUICKSTART.md           # Quick start guide
│   ├── CHANGELOG.md            # Version history and changes
│   ├── CONTRIBUTING.md         # Contribution guidelines
│   └── LICENSE                 # MIT License
│
├── 🐍 Core Package (sap_rfc_mcp_server/)
│   ├── __init__.py             # Package initialization
│   ├── server.py               # MCP server implementation
│   ├── http_server.py          # HTTP/REST API server
│   ├── sap_client.py           # SAP RFC client wrapper
│   ├── metadata_manager.py     # Enhanced metadata management
│   ├── metadata_cache.py       # Persistent caching system
│   ├── config.py               # Configuration management
│   ├── secure_config.py        # Secure configuration handling
│   └── sap_security_manager.py # Security utilities
│
├── 🧪 Testing (tests/)
│   ├── conftest.py             # Pytest configuration & fixtures
│   └── test_metadata_manager.py # Metadata manager tests
│
├── 📘 Examples (examples/)
│   └── basic_usage.py          # Basic usage demonstration
│
├── 💾 Cache (cache/)           # Metadata cache directory
├── 📖 Docs (docs/)            # Additional documentation
├── setup_dev.py               # Development environment setup script
└── 🚀 Runtime Files
    ├── .env                    # Environment configuration (created from template)
    └── sap_config.json         # Encrypted SAP configuration (auto-generated)
```

## 🔧 Core Components

### 1. **MCP Server** (`server.py`)
- **Purpose**: Model Context Protocol server for AI assistant integration
- **Key Features**: 15+ specialized tools for SAP operations
- **Tools Include**: RFC calling, metadata retrieval, search, table operations
- **Usage**: `sap-rfc-mcp-server` command

### 2. **HTTP Server** (`http_server.py`)
- **Purpose**: REST API server for web applications
- **Key Features**: OpenAPI documentation, CORS support
- **Endpoints**: `/rfc/call`, `/rfc/metadata`, `/rfc/search`
- **Usage**: `sap-rfc-mcp-http-server` command

### 3. **SAP Client** (`sap_client.py`)
- **Purpose**: Core SAP RFC connectivity and function calling
- **Key Features**: Connection pooling, error handling, retry logic
- **Dependencies**: pyrfc library, SAP NetWeaver RFC SDK

### 4. **Metadata Manager** (`metadata_manager.py`)
- **Purpose**: Enhanced RFC function metadata handling
- **Key Features**: Version-aware language mapping, caching, search
- **Special**: Handles R/3 4.5B through S/4HANA compatibility

### 5. **Metadata Cache** (`metadata_cache.py`)
- **Purpose**: Persistent file-based caching system
- **Key Features**: TTL support, search indexing, RAG export
- **Storage**: JSON files with optional compression

### 6. **Configuration** (`config.py`, `secure_config.py`)
- **Purpose**: Secure configuration management
- **Key Features**: Environment variables, encryption, validation
- **Security**: AES encryption for sensitive data

## 🔒 Security Features

### Configuration Security
- **Encryption**: AES-256 encryption for stored credentials
- **Environment Variables**: Secure credential loading from `.env`
- **Validation**: Input validation and sanitization

### Connection Security
- **SAP RFC**: Native SAP security protocols
- **Authentication**: User/password, SSO support
- **Network**: Support for SAP Router and secure connections

## 🚀 Deployment Options

### 1. **Development Setup**
```bash
python setup_dev.py
```

### 2. **Production Install**
```bash
pip install sap-rfc-mcp-server
```

### 3. **Docker Deployment**
```bash
docker build -t sap-rfc-mcp-server .
docker run -p 8000:8000 sap-rfc-mcp-server
```

## 📊 Performance Characteristics

### Caching Performance
- **Cold Start**: ~200-500ms (SAP RFC call)
- **Cache Hit**: ~1-5ms (file system read)
- **Search**: ~1-10ms (indexed search)

### Memory Usage
- **Base Server**: ~50MB
- **With Cache**: +10-50MB (depends on cached functions)
- **Per Connection**: +5-20MB

### Scalability
- **Concurrent Connections**: Limited by SAP RFC SDK
- **HTTP Requests**: Configurable worker processes
- **Cache Size**: Configurable maximum size

## 🔄 Development Workflow

### 1. **Setup Environment**
```bash
python setup_dev.py
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. **Code Quality**
```bash
black sap_rfc_mcp_server tests
isort sap_rfc_mcp_server tests
flake8 sap_rfc_mcp_server tests
mypy sap_rfc_mcp_server
```

### 3. **Testing**
```bash
pytest tests/ -v
pytest --cov=sap_rfc_mcp_server
```

### 4. **Pre-commit Hooks**
```bash
pre-commit install
pre-commit run --all-files
```

## 📋 Configuration Files

### Essential Files
- **`.env`**: Environment variables (create from `.env.template`)
- **`pyproject.toml`**: Python project configuration
- **`sap_config.json`**: Encrypted SAP configuration (auto-generated)

### Development Files
- **`.pre-commit-config.yaml`**: Code quality hooks
- **`conftest.py`**: Pytest configuration
- **`setup_dev.py`**: Development environment setup

## 🎯 Quick Commands

### Start Servers
```bash
# MCP Server
sap-rfc-mcp-server

# HTTP Server
sap-rfc-mcp-http-server
```

### Development
```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy sap_rfc_mcp_server
```

### Maintenance
```bash
# Clear cache
python -c "from sap_rfc_mcp_server import RFCMetadataManager; RFCMetadataManager().clear_cache()"

# Update dependencies
pip install --upgrade -r requirements.txt
```

## 🆘 Troubleshooting

### Common File Locations
- **Configuration**: `.env` or environment variables
- **Logs**: Console output or specified log file
- **Cache**: `cache/` directory
- **Tests**: `tests/` directory

### Debug Mode
Set `DEBUG=true` in `.env` for detailed logging and error information.

---

This structure provides a clean, maintainable, and scalable codebase for the SAP RFC MCP Server project. Each component has a specific purpose and clear interfaces, making it easy to understand, modify, and extend.
