"""
Unit tests for metadata manager functionality.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from sap_rfc_mcp_server.metadata_manager import RFCMetadataManager


class TestRFCMetadataManager:
    """Test cases for RFCMetadataManager."""

    @pytest.fixture
    def connection_params(self):
        """Sample connection parameters."""
        return {
            "ashost": "test-host",
            "sysnr": "00",
            "client": "100",
            "user": "testuser",
            "passwd": "testpass",
        }

    @pytest.fixture
    def metadata_manager(self, connection_params, temp_cache_dir):
        """Create metadata manager instance."""
        return RFCMetadataManager(connection_params, cache_dir=temp_cache_dir)

    @pytest.mark.unit
    def test_language_code_mapping_legacy(self, metadata_manager):
        """Test language code mapping for legacy SAP systems."""
        # Simulate R/3 4.5B detection
        metadata_manager._sap_version = "45B"
        metadata_manager._version_category = "R/3 4.5"

        # Test common language mappings
        assert metadata_manager._get_sap_language_code("EN") == "E"
        assert metadata_manager._get_sap_language_code("PL") == "L"
        assert metadata_manager._get_sap_language_code("DE") == "D"
        assert metadata_manager._get_sap_language_code("FR") == "F"
        assert metadata_manager._get_sap_language_code("ES") == "S"

    @pytest.mark.unit
    def test_language_code_unknown_fallback(self, metadata_manager):
        """Test fallback to English for unknown language codes."""
        metadata_manager._sap_version = "45B"
        metadata_manager._version_category = "R/3 4.5"

        # Test unknown language falls back to English
        assert metadata_manager._get_sap_language_code("XX") == "E"
        assert metadata_manager._get_sap_language_code("ZZ") == "E"

    @pytest.mark.unit
    @patch("sap_rfc_mcp_server.metadata_manager.pyrfc.Connection")
    def test_version_detection(self, mock_connection_class, metadata_manager):
        """Test SAP version detection."""
        # Mock connection and system info
        mock_conn = Mock()
        mock_conn.call.return_value = {"RFCSI_EXPORT": {"RFCSAPRL": "45B"}}
        mock_connection_class.return_value = mock_conn

        # Test version detection
        metadata_manager._detect_sap_version()

        assert metadata_manager._sap_version == "45B"
        assert metadata_manager._version_category == "R/3 4.5"

    @pytest.mark.unit
    def test_cache_integration(self, metadata_manager, sample_function_metadata):
        """Test cache integration."""
        # Mock the cache
        metadata_manager.cache.get_function_metadata = Mock(return_value=None)
        metadata_manager.cache.store_function_metadata = Mock()

        # Mock SAP call
        with patch.object(metadata_manager, "_retrieve_function_metadata") as mock_sap:
            mock_sap.return_value = sample_function_metadata

            # First call should retrieve from SAP and cache
            result = metadata_manager.get_function_metadata("RFC_SYSTEM_INFO")

            assert result == sample_function_metadata
            metadata_manager.cache.store_function_metadata.assert_called_once()

    @pytest.mark.unit
    def test_search_functionality(self, metadata_manager):
        """Test search functionality."""
        # Mock cache search
        expected_results = ["RFC_READ_TABLE", "RFC_WRITE_TABLE"]
        metadata_manager.cache.search_functions = Mock(return_value=expected_results)

        results = metadata_manager.search_functions("table")

        assert results == expected_results
        metadata_manager.cache.search_functions.assert_called_once_with("table", 20)

    @pytest.mark.integration
    def test_real_metadata_retrieval(self, metadata_manager, sample_function_metadata):
        """Integration test for metadata retrieval."""
        # Mock the internal methods to avoid complex connection mocking
        with patch.object(
            metadata_manager, "_get_connection"
        ) as mock_conn_method, patch.object(
            metadata_manager, "_get_function_info"
        ) as mock_info, patch.object(
            metadata_manager, "_get_function_interface"
        ) as mock_interface, patch.object(
            metadata_manager, "_process_parameters"
        ) as mock_process:
            # Setup mock connection
            mock_conn = Mock()
            mock_conn_method.return_value = mock_conn

            # Setup mock returns
            mock_info.return_value = {
                "function_name": "RFC_SYSTEM_INFO",
                "description": "Get system information",
                "area": "SRFC",
                "application": "S",
                "dev_class": "SABP",
                "release_date": "00000000",
                "last_changed": "",
            }

            mock_interface.return_value = {"PARAMS": [], "_retrieved_at": "EN"}

            mock_process.return_value = ({}, {"RFCSI_EXPORT": {}}, {})

            # Test metadata retrieval
            result = metadata_manager.get_function_metadata("RFC_SYSTEM_INFO")

            assert result is not None
            assert "function_name" in result["_metadata"]
            assert result["_metadata"]["function_name"] == "RFC_SYSTEM_INFO"


@pytest.mark.slow
class TestPerformance:
    """Performance tests for metadata operations."""

    @pytest.fixture
    def metadata_manager(self, temp_cache_dir):
        """Create metadata manager instance for performance tests."""
        connection_params = {
            "ashost": "test-host",
            "sysnr": "00",
            "client": "100",
            "user": "testuser",
            "passwd": "testpass",
        }
        return RFCMetadataManager(connection_params, cache_dir=temp_cache_dir)

    def test_bulk_loading_performance(self, metadata_manager):
        """Test performance of bulk metadata loading."""
        # Mock multiple function calls
        functions = [f"TEST_FUNCTION_{i}" for i in range(10)]

        with patch.object(metadata_manager, "get_function_metadata") as mock_get:
            mock_get.return_value = {"function_name": "test"}

            import time

            start_time = time.time()
            results = metadata_manager.bulk_load_metadata(functions)
            end_time = time.time()

            # Should complete reasonably quickly
            assert end_time - start_time < 5.0  # 5 seconds max
            assert len(results) == len(functions)
