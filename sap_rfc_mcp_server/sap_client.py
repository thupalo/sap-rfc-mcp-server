"""SAP RFC Connection Manager."""

import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

# Try to import pyrfc - make it optional for development
try:
    import pyrfc
    PYRFC_AVAILABLE = True
    Connection = pyrfc.Connection
except ImportError:
    pyrfc = None
    PYRFC_AVAILABLE = False
    Connection = Any

from .config import SAPConfig
from .secure_config import SAPConfigManager, SecurityError


logger = logging.getLogger(__name__)


class SAPConnectionError(Exception):
    """SAP connection related error."""
    pass


class SAPRFCManager:
    """Manages SAP RFC connections and function calls."""
    
    def __init__(self, config: Optional[SAPConfig] = None):
        """Initialize with SAP configuration using secure methods."""
        if not PYRFC_AVAILABLE:
            raise SAPConnectionError(
                "pyrfc module is not available. Please install SAP NetWeaver RFC SDK and pyrfc package. "
                "See README.md for installation instructions."
            )
            
        if config is None:
            try:
                config = SAPConfigManager.get_config("auto")
                logger.info(f"Using SAP configuration from: {config.get_security_info()['source']}")
            except SecurityError as e:
                logger.error(f"Failed to load SAP configuration: {e}")
                raise SAPConnectionError(f"SAP configuration error: {e}")
        
        self.config = config
        self._connection = None  # Optional[Connection] when pyrfc is available
        
        # Set up SAP RFC environment
        self._setup_environment()
    
    def _setup_environment(self):
        """Set up SAP RFC environment variables."""
        if not os.getenv("SAPNWRFC_HOME"):
            os.environ["SAPNWRFC_HOME"] = "C:\\SAPNWRFC_750"
        
        sap_lib_path = "C:\\SAPNWRFC_750\\lib"
        if sap_lib_path not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{sap_lib_path};{os.environ.get('PATH', '')}"
    
    @contextmanager
    def connection(self):  # -> Generator[Connection, None, None] when pyrfc is available
        """Context manager for SAP RFC connection."""
        if not PYRFC_AVAILABLE:
            raise SAPConnectionError(
                "pyrfc module is not available. Please install SAP NetWeaver RFC SDK and pyrfc package."
            )
            
        conn = None
        try:
            logger.info("Establishing SAP RFC connection...")
            conn = pyrfc.Connection(**self.config.to_connection_params())
            logger.info("SAP RFC connection established successfully")
            yield conn
        except Exception as e:
            logger.error(f"Failed to establish SAP RFC connection: {e}")
            raise SAPConnectionError(f"Connection failed: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                    logger.info("SAP RFC connection closed")
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")
    
    def call_rfc_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Call an RFC function with parameters."""
        with self.connection() as conn:
            try:
                logger.info(f"Calling RFC function: {function_name}")
                result = conn.call(function_name, **kwargs)
                logger.info(f"RFC function {function_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error calling RFC function {function_name}: {e}")
                raise SAPConnectionError(f"RFC call failed: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get SAP system information using RFC_SYSTEM_INFO."""
        return self.call_rfc_function("RFC_SYSTEM_INFO")
    
    def get_rfc_functions(self, funcs_mask: Optional[str] = None, 
                         devclass: Optional[str] = None) -> List[Dict[str, str]]:
        """Get list of RFC functions with optional filtering."""
        fields = [{"FIELDNAME": "FUNCNAME"}, 
                 {"FIELDNAME": "DEVCLASS"}, 
                 {"FIELDNAME": "STEXT"}]
        options = []
        
        # Build WHERE conditions
        where_conditions = []
        
        if funcs_mask:
            if '*' in funcs_mask:
                funcs_mask = funcs_mask.replace('*', '%')
                where_conditions.append(f"FUNCNAME LIKE '{funcs_mask}'")
            else:
                where_conditions.append(f"FUNCNAME = '{funcs_mask}'")
        
        if devclass:
            if '*' in devclass:
                devclass = devclass.replace('*', '%')
                where_conditions.append(f"DEVCLASS LIKE '{devclass}'")
            else:
                where_conditions.append(f"DEVCLASS = '{devclass}'")
        
        # Add remote-enabled filter
        where_conditions.append("FMODE = 'R'")
        
        # Build OPTIONS parameter
        if where_conditions:
            where_clause = " AND ".join(where_conditions)
            options = [{"TEXT": where_clause}]
        
        try:
            result = self.call_rfc_function(
                "RFC_READ_TABLE",
                QUERY_TABLE="INFO_FUNCT",
                DELIMITER="|",
                FIELDS=fields,
                OPTIONS=options
            )
            
            # Parse the result
            data = []
            if "DATA" in result:
                field_names = [field["FIELDNAME"] for field in fields]
                for row in result["DATA"]:
                    values = row["WA"].split("|")
                    row_dict = {
                        field: value.strip() 
                        for field, value in zip(field_names, values)
                    }
                    data.append(row_dict)
            
            return data
            
        except Exception as e:
            logger.error(f"Error querying RFC functions: {e}")
            raise SAPConnectionError(f"Function query failed: {e}")
