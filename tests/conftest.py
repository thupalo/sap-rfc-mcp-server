"""
Test configuration and fixtures for SAP RFC MCP Server tests.
"""

import os
from unittest.mock import MagicMock, Mock

import pytest

# Test configuration
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture
def mock_sap_connection():
    """Create a mock SAP connection for testing."""
    conn = Mock()
    conn.call.return_value = {
        "RFCSI_EXPORT": {"RFCSYSID": "TEST", "RFCSAPRL": "45B", "RFCHOST": "test-host"}
    }
    return conn


@pytest.fixture
def mock_sap_config():
    """Create a mock SAP configuration."""
    config = Mock()
    config.to_connection_params.return_value = {
        "ashost": "test-host",
        "sysnr": "00",
        "client": "100",
        "user": "testuser",
        "passwd": "testpass",
    }
    return config


@pytest.fixture
def sample_function_metadata():
    """Sample RFC function metadata for testing."""
    return {
        "function_name": "RFC_SYSTEM_INFO",
        "description": "Get SAP system information",
        "import_parameters": [],
        "export_parameters": [
            {
                "name": "RFCSI_EXPORT",
                "type": "STRUCTURE",
                "length": 200,
                "description": "System information structure",
            }
        ],
        "language": "EN",
        "version": "1.0",
    }


@pytest.fixture
def sample_table_data():
    """Sample table data for testing."""
    return {
        "DATA": [
            {"WA": "100|Company 1|Currency 1"},
            {"WA": "200|Company 2|Currency 2"},
            {"WA": "300|Company 3|Currency 3"},
        ],
        "FIELDS": [
            {"FIELDNAME": "BUKRS", "TYPE": "C", "LENGTH": 4},
            {"FIELDNAME": "BUTXT", "TYPE": "C", "LENGTH": 25},
            {"FIELDNAME": "WAERS", "TYPE": "C", "LENGTH": 5},
        ],
    }


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create a temporary cache directory for testing."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return str(cache_dir)


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
