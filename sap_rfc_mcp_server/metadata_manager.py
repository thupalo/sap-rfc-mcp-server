"""Enhanced RFC Metadata Manager with caching and optimization."""

import logging
import os
from typing import Dict, Any, Optional, List
import pyrfc
from .metadata_cache import RFCMetadataCache

logger = logging.getLogger(__name__)


class RFCMetadataManager:
    """Enhanced RFC metadata manager with caching and optimization."""
    
    def __init__(self, connection_params: Dict[str, str], 
                 cache_dir: str = "cache", 
                 default_language: str = "EN"):
        """
        Initialize metadata manager.
        
        Args:
            connection_params: SAP connection parameters
            cache_dir: Directory for cache storage
            default_language: Default language for descriptions
        """
        self.connection_params = connection_params
        self.default_language = default_language
        self.cache = RFCMetadataCache(cache_dir)
        self._connection: Optional[pyrfc.Connection] = None
        self._sap_version: Optional[str] = None
        self._version_category: Optional[str] = None
        
        # Configuration
        self.expand_descriptions = True
        self.language_fallback = ['EN', 'DE', 'PL']  # Language priority
        
        # SAP language code mapping (ISO 2-letter to SAP 1-letter)
        self.sap_language_mapping = {
            'EN': 'E',  # English
            'DE': 'D',  # German (Deutsch)
            'PL': 'L',  # Polish
            'FR': 'F',  # French
            'ES': 'S',  # Spanish
            'IT': 'I',  # Italian
            'RU': 'R',  # Russian
            'JA': 'J',  # Japanese
            'ZH': 'C',  # Chinese
            'PT': 'P',  # Portuguese
            'NL': 'N',  # Dutch
            'DA': 'K',  # Danish
            'SV': 'V',  # Swedish
            'NO': 'O',  # Norwegian
            'FI': 'U',  # Finnish
            'CS': 'Q',  # Czech
            'HU': 'H',  # Hungarian
            'TR': 'T',  # Turkish
            'AR': 'A',  # Arabic
            'HE': 'W',  # Hebrew
            'TH': 'B',  # Thai
            'KO': 'M',  # Korean
        }
        
    def _get_sap_language_code(self, language: str) -> str:
        """
        Convert ISO 2-letter language code to SAP language code.
        Uses version-aware logic based on SAP system version.
        
        Args:
            language: ISO 2-letter language code (e.g., 'EN', 'PL', 'DE')
            
        Returns:
            SAP language code (1-letter for older systems, potentially 2-letter for newer)
        """
        # Ensure we know the SAP version
        if self._sap_version is None:
            self._detect_sap_version()
        
        # Convert to uppercase and take first 2 characters
        lang_code = language.upper()[:2]
        
        # For R/3 4.5B and other legacy systems, always use single-letter codes
        if self._version_category in ['R/3 4.5', 'R/3 4.6', 'R/3 4.7']:
            sap_code = self.sap_language_mapping.get(lang_code)
            if sap_code is None:
                logger.warning(f"Unknown language code '{lang_code}' for {self._version_category}, falling back to English ('E')")
                return 'E'
            logger.debug(f"Using single-letter language code '{sap_code}' for {self._version_category}")
            return sap_code
        
        # For ECC 6.0+, prefer single-letter but could potentially use 2-letter as fallback
        elif self._version_category in ['ECC 6.0/6.1', 'ECC 6.0 EHP']:
            sap_code = self.sap_language_mapping.get(lang_code)
            if sap_code is None:
                logger.warning(f"Unknown language code '{lang_code}' for {self._version_category}, falling back to English ('E')")
                return 'E'
            logger.debug(f"Using single-letter language code '{sap_code}' for {self._version_category} (recommended)")
            return sap_code
        
        # For S/4HANA, could use 2-letter codes but single-letter is safer for compatibility
        else:
            sap_code = self.sap_language_mapping.get(lang_code)
            if sap_code is None:
                logger.warning(f"Unknown language code '{lang_code}' for {self._version_category}, falling back to English ('E')")
                return 'E'
            logger.debug(f"Using single-letter language code '{sap_code}' for {self._version_category} (compatibility mode)")
            return sap_code
    
    def _detect_sap_version(self):
        """Detect SAP system version to determine appropriate language code handling."""
        try:
            conn = self._get_connection()
            sys_info = conn.call('RFC_SYSTEM_INFO')
            self._sap_version = sys_info["RFCSI_EXPORT"]["RFCSAPRL"]
            
            # Categorize version
            if self._sap_version.startswith('45'):
                self._version_category = "R/3 4.5"
            elif self._sap_version.startswith('46'):
                self._version_category = "R/3 4.6"
            elif self._sap_version.startswith('47'):
                self._version_category = "R/3 4.7"
            elif self._sap_version.startswith('60') or self._sap_version.startswith('61'):
                self._version_category = "ECC 6.0/6.1"
            elif self._sap_version.startswith('70'):
                self._version_category = "ECC 6.0 EHP"
            elif self._sap_version.startswith('75'):
                self._version_category = "S/4HANA 1.0"
            elif self._sap_version.startswith('76'):
                self._version_category = "S/4HANA 2.0"
            else:
                self._version_category = "Unknown/Newer"
            
            logger.info(f"Detected SAP version: {self._sap_version} ({self._version_category})")
            
        except Exception as e:
            logger.warning(f"Could not detect SAP version: {e}. Assuming legacy system.")
            self._sap_version = "Unknown"
            self._version_category = "R/3 4.5"  # Default to most restrictive for safety
    
    def _get_connection(self) -> pyrfc.Connection:
        """Get or create SAP connection."""
        if self._connection is None:
            try:
                self._connection = pyrfc.Connection(**self.connection_params)
                logger.info("SAP RFC connection established for metadata retrieval")
            except Exception as e:
                logger.error(f"Failed to establish SAP connection: {e}")
                raise
        return self._connection
    
    def close_connection(self):
        """Close SAP connection."""
        if self._connection:
            try:
                self._connection.close()
                self._connection = None
                logger.info("SAP RFC connection closed")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
    
    def get_function_metadata(self, func_name: str, 
                            language: Optional[str] = None,
                            force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive RFC function metadata.
        
        Args:
            func_name: RFC function name
            language: Language for descriptions (defaults to default_language)
            force_refresh: Force refresh from SAP system
            
        Returns:
            Comprehensive metadata dictionary
        """
        if language is None:
            language = self.default_language
            
        # Check cache first
        if not force_refresh:
            cached_metadata = self.cache.get_function_metadata(func_name)
            if cached_metadata:
                logger.debug(f"Retrieved cached metadata for {func_name}")
                return cached_metadata
        
        # Retrieve from SAP
        logger.info(f"Retrieving metadata for {func_name} from SAP")
        metadata = self._retrieve_function_metadata(func_name, language)
        
        # Cache the result
        self.cache.store_function_metadata(func_name, metadata)
        
        return metadata
    
    def _retrieve_function_metadata(self, func_name: str, language: str) -> Dict[str, Any]:
        """Retrieve metadata from SAP system."""
        conn = self._get_connection()
        
        # Get function basic information
        function_info = self._get_function_info(conn, func_name)
        
        # Get function interface
        interface_info = self._get_function_interface(conn, func_name, language)
        
        # Process parameters
        inputs, outputs, tables = self._process_parameters(conn, interface_info['PARAMS'])
        
        # Build complete metadata
        metadata = {
            '_metadata': function_info,
            '_language': language,
            '_retrieved_at': interface_info.get('_retrieved_at'),
            'inputs': inputs,
            'outputs': outputs,
            'tables': tables,
            '_schema_version': '2.0'
        }
        
        return metadata
    
    def _get_function_info(self, conn: pyrfc.Connection, func_name: str) -> Dict[str, Any]:
        """Get basic function information from INFO_FUNCT table."""
        options = [{'TEXT': f"FUNCNAME = '{func_name}' AND ACTIVE = 'X' AND FMODE = 'R'"}]
        fields = [
            {"FIELDNAME": "STEXT"}, 
            {"FIELDNAME": "AREA"},
            {"FIELDNAME": "APPL"},
            {"FIELDNAME": "DEVCLASS"},
            {"FIELDNAME": "FREEDATE"}
        ]
        
        try:
            result = conn.call('RFC_READ_TABLE', 
                             QUERY_TABLE='INFO_FUNCT', 
                             DELIMITER='|',
                             FIELDS=fields, 
                             OPTIONS=options)
            
            if 'DATA' in result and len(result['DATA']) > 0:
                row = result['DATA'][0]['WA'].split('|')
                return {
                    'function_name': func_name,
                    'description': row[0].strip(),
                    'area': row[1].strip(),
                    'application': row[2].strip(),
                    'dev_class': row[3].strip(),
                    'release_date': row[4].strip(),
                    'last_changed': ''  # Not available in INFO_FUNCT
                }
            else:
                raise ValueError(f"Function {func_name} not found in INFO_FUNCT")
        except Exception as e:
            logger.error(f"Error retrieving function info for {func_name}: {e}")
            raise
    
    def _get_function_interface(self, conn: pyrfc.Connection, 
                              func_name: str, language: str) -> Dict[str, Any]:
        """Get function interface information."""
        try:
            result = conn.call('RFC_GET_FUNCTION_INTERFACE_US', 
                             FUNCNAME=func_name, 
                             LANGUAGE=language)
            result['_retrieved_at'] = language
            return result
        except Exception as e:
            # Try with different language if specified language fails
            if language != 'EN':
                logger.warning(f"Failed to get interface in {language}, trying EN")
                try:
                    result = conn.call('RFC_GET_FUNCTION_INTERFACE_US', 
                                     FUNCNAME=func_name, 
                                     LANGUAGE='EN')
                    result['_retrieved_at'] = 'EN'
                    return result
                except Exception as e2:
                    logger.error(f"Error retrieving function interface for {func_name}: {e2}")
                    raise e2
            else:
                logger.error(f"Error retrieving function interface for {func_name}: {e}")
                raise
    
    def _process_parameters(self, conn: pyrfc.Connection, 
                          params: List[Dict[str, Any]]) -> tuple:
        """Process function parameters and build metadata."""
        inputs, outputs, tables = {}, {}, {}
        
        for param in params:
            param_name = param['PARAMETER']
            param_class = param['PARAMCLASS']
            default_value = param.get('DEFAULT', '')
            description = param.get('PARAMTEXT', '').strip()
            
            # Get parameter metadata
            param_metadata = self._get_parameter_metadata(conn, param)
            
            # Add common attributes
            if default_value:
                param_metadata['default'] = default_value
            if self.expand_descriptions and description:
                param_metadata['description'] = description
            
            # Add to appropriate collection
            if param_class == 'I':  # Import (Input)
                inputs[param_name] = param_metadata
            elif param_class == 'E':  # Export (Output)
                outputs[param_name] = param_metadata
            elif param_class == 'T':  # Table
                tables[param_name] = param_metadata
            elif param_class == 'C':  # Changing (both input and output)
                inputs[param_name] = param_metadata.copy()
                outputs[param_name] = param_metadata.copy()
            # 'X' parameters (exceptions) are skipped
        
        return inputs, outputs, tables
    
    def _get_parameter_metadata(self, conn: pyrfc.Connection, 
                              param: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed metadata for a parameter."""
        # Initialize metadata
        metadata = {
            'sap_type': param.get('EXID', 'ANY'),
            'length': int(param.get('INTLENGTH', 0)),
            'decimals': int(param.get('DECIMALS', 0))
        }
        
        # Process based on parameter structure
        if param.get('TABNAME'):
            if param.get('FIELDNAME') or param['PARAMCLASS'] == 'T' or param.get('EXID') == 'u':
                # Field or table parameter
                field_metadata = self._get_field_metadata(conn, param['TABNAME'], 
                                                        param.get('FIELDNAME', ''))
                if param['PARAMCLASS'] == 'T':
                    metadata.update({
                        'type': 'TABLE',
                        'table_structure': field_metadata,
                        'fields': list(field_metadata.keys()) if isinstance(field_metadata, dict) else []
                    })
                else:
                    metadata.update(field_metadata.get(param.get('FIELDNAME', ''), {}))
            else:
                # Data element
                dtel_metadata = self._get_data_element_metadata(conn, param)
                metadata.update(dtel_metadata)
        else:
            # Simple parameter
            metadata.update({
                'type': self._map_abap_type(param.get('EXID', 'ANY'), 
                                          int(param.get('INTLENGTH', 0)),
                                          int(param.get('DECIMALS', 0)))
            })
        
        return metadata
    
    def _get_field_metadata(self, conn: pyrfc.Connection, 
                           table_name: str, field_name: str = '') -> Dict[str, Any]:
        """Get field metadata using DDIF_FIELDINFO_GET."""
        try:
            result = conn.call('DDIF_FIELDINFO_GET', 
                             TABNAME=table_name, 
                             FIELDNAME=field_name, 
                             LANGU=self._get_sap_language_code(self.default_language))
            
            fields_metadata = {}
            for field_info in result.get('DFIES_TAB', []):
                field_name = field_info['FIELDNAME']
                
                # Map ABAP types
                sap_type = field_info.get('INTTYPE', 'ANY')
                length = int(field_info.get('LENG', 0))
                decimals = int(field_info.get('DECIMALS', 0))
                
                field_meta = {
                    'type': self._map_abap_type(sap_type, length, decimals),
                    'sap_type': sap_type,
                    'length': length,
                    'decimals': decimals,
                    'position': int(field_info.get('POSITION', 0)),
                    'description': self._get_best_description(field_info),
                    'key_field': field_info.get('KEYFLAG') == 'X',
                    'data_element': field_info.get('ROLLNAME', ''),
                    'domain': field_info.get('DOMNAME', ''),
                    'check_table': field_info.get('CHECKTABLE', '')
                }
                
                fields_metadata[field_name] = field_meta
            
            return fields_metadata
            
        except Exception as e:
            logger.error(f"Error retrieving field metadata for {table_name}.{field_name}: {e}")
            return {}
    
    def _get_data_element_metadata(self, conn: pyrfc.Connection, 
                                 param: Dict[str, Any]) -> Dict[str, Any]:
        """Get data element metadata from DD04V table."""
        try:
            options = f"DDLANGUAGE = '{self._get_sap_language_code(self.default_language)}' AND ROLLNAME = '{param['TABNAME']}'"
            
            result = conn.call('RFC_READ_TABLE', 
                             QUERY_TABLE='DD04V', 
                             DELIMITER='|',
                             FIELDS=[{"FIELDNAME": 'DDTEXT'},
                                   {"FIELDNAME": 'REPTEXT'},
                                   {"FIELDNAME": 'SCRTEXT_L'}],
                             OPTIONS=[{'TEXT': options}])
            
            metadata = {}
            if 'DATA' in result and result['DATA']:
                texts = result['DATA'][0]['WA'].split('|')
                description = next((text.strip() for text in texts if text.strip()), '')
                metadata['description'] = description
            
            # Map type information
            sap_type = param.get('EXID', 'ANY')
            length = int(param.get('INTLENGTH', 0))
            decimals = int(param.get('DECIMALS', 0))
            
            metadata.update({
                'type': self._map_abap_type(sap_type, length, decimals),
                'sap_type': sap_type,
                'length': length,
                'decimals': decimals,
                'data_element': param.get('TABNAME', '')
            })
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error retrieving data element metadata for {param.get('TABNAME')}: {e}")
            return {
                'type': 'ANY',
                'description': param.get('PARAMTEXT', '').strip()
            }
    
    def _map_abap_type(self, sap_type: str, length: int, decimals: int) -> str:
        """Map SAP ABAP types to standard types."""
        type_mapping = {
            'C': f'CHAR({length})',
            'N': f'NUMC({length})',
            'D': 'DATE',
            'T': 'TIME',
            'X': f'XSTRING({length})',
            'I': f'INT({length})',
            'P': f'DECIMAL({length},{decimals})' if decimals > 0 else f'DECIMAL({length})',
            'F': 'FLOAT',
            'S': 'STRING',
            'G': 'XSTRING',
            'u': 'STRUCTURE'
        }
        return type_mapping.get(sap_type, 'ANY')
    
    def _get_best_description(self, field_info: Dict[str, Any]) -> str:
        """Get the best available description from field info."""
        description_fields = ['FIELDTEXT', 'REPTEXT', 'SCRTEXT_L', 'SCRTEXT_M', 'SCRTEXT_S']
        for field in description_fields:
            desc = field_info.get(field, '').strip()
            if desc:
                return desc
        return ''
    
    def bulk_load_metadata(self, function_names: List[str], 
                          language: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Load metadata for multiple functions efficiently."""
        if language is None:
            language = self.default_language
            
        results = {}
        for func_name in function_names:
            try:
                metadata = self.get_function_metadata(func_name, language)
                results[func_name] = metadata
                logger.debug(f"Loaded metadata for {func_name}")
            except Exception as e:
                logger.error(f"Failed to load metadata for {func_name}: {e}")
                results[func_name] = {'error': str(e)}
        
        return results
    
    def search_functions(self, query: str, limit: int = 20) -> List[str]:
        """Search for functions using cached index."""
        return self.cache.search_functions(query, limit)
    
    def export_for_rag(self, output_file: str) -> None:
        """Export metadata in RAG-friendly format."""
        self.cache.export_for_rag(output_file)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_cache_stats()
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries."""
        return self.cache.clear_expired()
