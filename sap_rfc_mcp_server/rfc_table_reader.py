"""
Enhanced RFC_READ_TABLE Handler with DATA_BUFFER_EXCEEDED Protection
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RFCTableReader:
    """Enhanced RFC_READ_TABLE with automatic field selection and buffer management."""

    def __init__(self, sap_client):
        self.sap_client = sap_client
        self.max_buffer_size = 512  # RFC buffer limit
        self.default_field_size = 20  # Default assumed field size

    def get_table_structure(
        self, table_name: str, language: str = "E"
    ) -> dict[str, Any]:
        """Get table structure with field information."""
        try:
            result = self.sap_client.call_rfc_function(
                "DDIF_FIELDINFO_GET", TABNAME=table_name, LANGU=language
            )

            fields_info = {}
            if "DFIES_TAB" in result:
                for field in result["DFIES_TAB"]:
                    field_name = field.get("FIELDNAME", "")
                    if field_name:
                        fields_info[field_name] = {
                            "name": field_name,
                            "type": field.get("DATATYPE", ""),
                            "length": int(field.get("LENG", self.default_field_size)),
                            "decimals": int(field.get("DECIMALS", 0)),
                            "description": field.get("FIELDTEXT", ""),
                            "key": field.get("KEYFLAG", "") == "X",
                        }

            return {
                "table_name": table_name,
                "fields": fields_info,
                "structure_available": len(fields_info) > 0,
            }

        except Exception as e:
            logger.warning(f"Could not get table structure for {table_name}: {e}")
            return {
                "table_name": table_name,
                "fields": {},
                "structure_available": False,
                "error": str(e),
            }

    def calculate_field_selection(
        self, fields_info: dict[str, Any], requested_fields: list[str] = None
    ) -> tuple[list[str], int]:
        """Calculate optimal field selection to avoid buffer overflow."""

        if not fields_info or not fields_info.get("structure_available", False):
            # Fallback: use common small fields for unknown table structure
            return ["MANDT"], 50  # Most SAP tables have MANDT (client) field

        available_fields = fields_info["fields"]

        # If specific fields requested, validate and calculate their size
        if requested_fields:
            selected_fields = []
            total_size = 0

            for field_name in requested_fields:
                if field_name in available_fields:
                    field_size = available_fields[field_name]["length"]
                    if total_size + field_size <= self.max_buffer_size:
                        selected_fields.append(field_name)
                        total_size += field_size
                    else:
                        logger.warning(
                            f"Field {field_name} ({field_size} chars) would exceed buffer limit"
                        )
                        break
                else:
                    logger.warning(f"Field {field_name} not found in table structure")

            return selected_fields, total_size

        # Auto-select fields starting with key fields, then shortest fields
        sorted_fields = sorted(
            available_fields.items(),
            key=lambda x: (
                not x[1]["key"],
                x[1]["length"],
                x[0],
            ),  # Key fields first, then by size
        )

        selected_fields = []
        total_size = 0

        for field_name, field_info in sorted_fields:
            field_size = field_info["length"]
            # Leave some buffer for delimiters and safety margin
            if total_size + field_size <= (self.max_buffer_size - 50):
                selected_fields.append(field_name)
                total_size += field_size
            else:
                break

        # Ensure we have at least one field
        if not selected_fields and sorted_fields:
            first_field = sorted_fields[0]
            selected_fields = [first_field[0]]
            total_size = first_field[1]["length"]

        return selected_fields, total_size

    def read_table_safe(
        self,
        table_name: str,
        fields: list[str] = None,
        where_conditions: list[str] = None,
        max_rows: int = 100,
        delimiter: str = "|",
    ) -> dict[str, Any]:
        """
        Safe RFC_READ_TABLE with automatic field selection to prevent DATA_BUFFER_EXCEEDED.

        Args:
            table_name: SAP table name
            fields: List of field names to read (optional)
            where_conditions: WHERE conditions (optional)
            max_rows: Maximum number of rows to read
            delimiter: Field delimiter

        Returns:
            Dict with table data and metadata
        """

        # Step 1: Get table structure
        structure_info = self.get_table_structure(table_name)

        # Step 2: Calculate optimal field selection
        selected_fields, estimated_size = self.calculate_field_selection(
            structure_info, fields
        )

        # Step 3: Prepare RFC_READ_TABLE parameters
        params = {
            "QUERY_TABLE": table_name,
            "DELIMITER": delimiter,
            "ROWCOUNT": max_rows,
        }

        # Add selected fields
        if selected_fields:
            params["FIELDS"] = [{"FIELDNAME": field} for field in selected_fields]

        # Add where conditions
        if where_conditions:
            params["OPTIONS"] = [{"TEXT": condition} for condition in where_conditions]

        # Step 4: Execute RFC_READ_TABLE with error handling
        try:
            result = self.sap_client.call_rfc_function("RFC_READ_TABLE", **params)

            # Step 5: Enhance result with metadata
            enhanced_result = {
                "success": True,
                "table_name": table_name,
                "selected_fields": selected_fields,
                "estimated_buffer_size": estimated_size,
                "parameters_used": params,
                "structure_info": structure_info,
                "raw_result": result,
                "parsed_data": [],
                "row_count": 0,
            }

            # Parse data
            if "DATA" in result:
                enhanced_result["row_count"] = len(result["DATA"])

                for row in result["DATA"]:
                    row_data = row.get("WA", "")
                    if delimiter in row_data:
                        values = row_data.split(delimiter)
                        parsed_row = {}
                        for i, value in enumerate(values):
                            if i < len(selected_fields):
                                parsed_row[selected_fields[i]] = value.strip()
                        enhanced_result["parsed_data"].append(parsed_row)
                    else:
                        # Single field or no delimiter
                        if len(selected_fields) == 1:
                            enhanced_result["parsed_data"].append(
                                {selected_fields[0]: row_data.strip()}
                            )
                        else:
                            enhanced_result["parsed_data"].append({"raw": row_data})

            return enhanced_result

        except Exception as e:
            error_msg = str(e)

            # Handle DATA_BUFFER_EXCEEDED specifically
            if "DATA_BUFFER_EXCEEDED" in error_msg:
                logger.warning(
                    f"Buffer exceeded for table {table_name}, trying with minimal fields"
                )

                # Retry with minimal field set (usually just key fields or first field)
                if structure_info.get("structure_available"):
                    key_fields = [
                        name
                        for name, info in structure_info["fields"].items()
                        if info.get("key", False)
                    ]

                    if key_fields:
                        minimal_fields = key_fields[:2]  # Max 2 key fields
                    else:
                        # Take the shortest field
                        shortest_field = min(
                            structure_info["fields"].items(),
                            key=lambda x: x[1]["length"],
                        )
                        minimal_fields = [shortest_field[0]]
                else:
                    minimal_fields = ["MANDT"]  # Common fallback

                # Recursive call with minimal fields
                try:
                    return self.read_table_safe(
                        table_name=table_name,
                        fields=minimal_fields,
                        where_conditions=where_conditions,
                        max_rows=max_rows,
                        delimiter=delimiter,
                    )
                except Exception as retry_error:
                    return {
                        "success": False,
                        "table_name": table_name,
                        "error": f"Buffer exceeded and retry failed: {str(retry_error)}",
                        "suggested_solution": "Table has very wide rows. Try specifying specific narrow fields.",
                        "original_error": error_msg,
                    }
            else:
                return {
                    "success": False,
                    "table_name": table_name,
                    "error": error_msg,
                    "selected_fields": selected_fields,
                    "estimated_buffer_size": estimated_size,
                }

    def read_table_iterative(
        self,
        table_name: str,
        all_fields: list[str] = None,
        where_conditions: list[str] = None,
        max_rows: int = 100,
        delimiter: str = "|",
    ) -> dict[str, Any]:
        """
        Read table with all requested fields by making multiple calls if necessary.

        This method splits wide tables into multiple RFC_READ_TABLE calls to avoid
        buffer overflow, then combines the results.
        """

        if not all_fields:
            # If no specific fields requested, use safe single call
            return self.read_table_safe(
                table_name, None, where_conditions, max_rows, delimiter
            )

        structure_info = self.get_table_structure(table_name)

        if not structure_info.get("structure_available"):
            logger.warning(
                f"Cannot do iterative read without table structure for {table_name}"
            )
            return self.read_table_safe(
                table_name, all_fields, where_conditions, max_rows, delimiter
            )

        # Split fields into chunks that fit in buffer
        field_chunks = []
        current_chunk = []
        current_size = 0

        available_fields = structure_info["fields"]

        for field_name in all_fields:
            if field_name in available_fields:
                field_size = available_fields[field_name]["length"]

                if current_size + field_size <= (self.max_buffer_size - 50):
                    current_chunk.append(field_name)
                    current_size += field_size
                else:
                    if current_chunk:
                        field_chunks.append(current_chunk)
                    current_chunk = [field_name]
                    current_size = field_size

        if current_chunk:
            field_chunks.append(current_chunk)

        if not field_chunks:
            return {
                "success": False,
                "table_name": table_name,
                "error": "No valid fields found for iterative read",
            }

        # Read each chunk
        combined_data = []
        all_results = []

        for i, chunk in enumerate(field_chunks):
            chunk_result = self.read_table_safe(
                table_name, chunk, where_conditions, max_rows, delimiter
            )

            all_results.append(chunk_result)

            if not chunk_result.get("success", False):
                return {
                    "success": False,
                    "table_name": table_name,
                    "error": f"Chunk {i+1} failed: {chunk_result.get('error', 'Unknown error')}",
                    "partial_results": all_results,
                }

            # Combine data (first chunk determines row structure)
            if i == 0:
                combined_data = chunk_result["parsed_data"]
            else:
                # Merge additional fields into existing rows
                chunk_data = chunk_result["parsed_data"]
                for j, row in enumerate(combined_data):
                    if j < len(chunk_data):
                        row.update(chunk_data[j])

        return {
            "success": True,
            "table_name": table_name,
            "method": "iterative",
            "field_chunks": field_chunks,
            "chunk_count": len(field_chunks),
            "combined_data": combined_data,
            "row_count": len(combined_data),
            "chunk_results": all_results,
        }
