# 🚀 Quick Start Guide

Get up and running with the SAP RFC MCP Server in minutes!

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.9 or higher** installed
- **SAP NetWeaver RFC SDK** installed and configured
- **Access to a SAP system** with RFC connectivity
- **Git** (optional, for cloning)

## ⚡ Fast Setup (Automated)

The quickest way to get started:

```bash
# 1. Clone or download the project
git clone https://github.com/thupalo/sap-rfc-mcp-server.git
cd sap-rfc-mcp-server

# 2. Run the automated setup script
python setup_dev.py

# 3. Configure your SAP connection
# Edit the .env file with your SAP details
notepad .env  # Windows
nano .env     # Linux/Mac

# 4. Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 5. Test the installation
python examples/basic_usage.py
```

## 🔧 Manual Setup

If you prefer to set up manually:

### 1. Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -e .
pip install -e ".[dev]"  # For development
```

### 3. Configure SAP Connection

Copy the environment template:
```bash
cp .env.template .env
```

Edit `.env` with your SAP connection details:
```env
SAP_ASHOST=your-sap-hostname
SAP_SYSNR=00
SAP_CLIENT=100
SAP_USER=your-username
SAP_PASSWD=your-password
SAP_LANG=EN
```

### 4. Test Connection

```bash
python examples/basic_usage.py
```

## 🎯 Usage Examples

### MCP Server (for AI Assistants)

```bash
# Start MCP server via stdio
sap-rfc-mcp-server

# The server communicates via stdin/stdout for MCP clients
```

### HTTP Server (for Web Applications)

```bash
# Start HTTP server
sap-rfc-mcp-http-server

# Server available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Python API

```python
from sap_rfc_mcp_server import SAPRFCManager

# Initialize client
client = SAPRFCManager()

# Call RFC function
result = client.call_rfc_function(
    "RFC_READ_TABLE",
    {
        "QUERY_TABLE": "T001",
        "ROWCOUNT": 10
    }
)

print(result)
```

## 🔍 Verify Installation

Run these commands to verify everything is working:

### 1. Import Test
```bash
python -c "import sap_rfc_mcp_server; print('✅ Import successful')"
```

### 2. Connection Test
```bash
python examples/basic_usage.py
```

### 3. Run Tests
```bash
pytest tests/ -v
```

## 🆘 Troubleshooting

### Common Issues

#### SAP RFC SDK Not Found
```
Error: RFC SDK not found
```
**Solution**: Install SAP NetWeaver RFC SDK and ensure it's in your PATH.

#### Connection Refused
```
Error: Connection to SAP system failed
```
**Solution**: 
- Check your SAP connection parameters in `.env`
- Verify network connectivity to SAP server
- Ensure SAP user has RFC authorization

#### Import Errors
```
ImportError: No module named 'pyrfc'
```
**Solution**: 
- Activate virtual environment
- Reinstall dependencies: `pip install -e .`

### Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages in the console output
2. **Verify configuration**: Double-check your `.env` file
3. **Test connectivity**: Use SAP GUI or other tools to verify connection
4. **Check documentation**: See the full documentation in `README.md`
5. **Ask for help**: Open an issue on GitHub

## 🎉 What's Next?

Once you have the basic setup working:

1. **Explore the MCP Tools**: Try different RFC functions
2. **Check the Metadata Cache**: See how function metadata is cached
3. **Try the HTTP API**: Use the web interface at http://localhost:8000/docs
4. **Read the Documentation**: Check out the `docs/` folder for detailed guides
5. **Contribute**: See `CONTRIBUTING.md` for how to help improve the project

## 📚 Key Files

- **`.env`**: Your SAP connection configuration
- **`examples/basic_usage.py`**: Simple usage example
- **`tests/`**: Test files to verify functionality
- **`cache/`**: Metadata cache directory
- **`README.md`**: Comprehensive documentation

Happy coding! 🚀
