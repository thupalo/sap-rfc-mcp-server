"""
Client-side RFC Metadata Management
Handles caching, searching, and processing of SAP RFC metadata.

This moves complex metadata operations from the server to the client,
keeping the MCP server minimal and focused on core RFC connectivity.
"""

import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)


class RFCMetadataClient:
    """Client-side RFC metadata management with local caching and search."""
    
    def __init__(self, cache_dir: str = "cache", mcp_client=None):
        """
        Initialize metadata client.
        
        Args:
            cache_dir: Directory for cache storage
            mcp_client: MCP client instance for server communication
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.mcp_client = mcp_client
        self.db_path = self.cache_dir / "rfc_metadata.db"
        self._init_cache_db()
        
        # Configuration
        self.default_language = "EN"
        self.cache_expiry_days = 30
    
    def _init_cache_db(self):
        """Initialize SQLite cache database with proper schema."""
        conn = sqlite3.connect(self.db_path)
        
        # Function metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS function_metadata (
                function_name TEXT NOT NULL,
                language TEXT NOT NULL,
                metadata TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                PRIMARY KEY (function_name, language)
            )
        """)
        
        # Search index table for fast text search
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_index (
                function_name TEXT NOT NULL,
                language TEXT NOT NULL,
                search_text TEXT NOT NULL,
                FOREIGN KEY (function_name, language) 
                    REFERENCES function_metadata(function_name, language)
            )
        """)
        
        # Create full-text search index
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(
                function_name, 
                description, 
                parameters,
                content='search_index'
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Initialized metadata cache database: {self.db_path}")
    
    async def get_function_metadata(self, 
                                   function_name: str, 
                                   language: str = None,
                                   force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get function metadata with intelligent caching.
        
        Args:
            function_name: RFC function name
            language: Language for descriptions (defaults to EN)
            force_refresh: Force refresh from SAP system
            
        Returns:
            Processed function metadata
        """
        language = language or self.default_language
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached = self._get_cached_metadata(function_name, language)
            if cached and not self._is_cache_expired(cached):
                logger.debug(f"Using cached metadata for {function_name}")
                return cached["metadata"]
        
        # Fetch from server via minimal MCP call
        if self.mcp_client:
            logger.info(f"Fetching metadata for {function_name} from server")
            
            try:
                # Use minimal server to get raw RFC metadata
                raw_result = await self.mcp_client.call_tool("call_rfc_function", {
                    "function_name": "RFC_GET_FUNCTION_INTERFACE",
                    "parameters": {
                        "FUNCNAME": function_name,
                        "LANGUAGE": language
                    }
                })
                
                # Process raw result on client side
                processed = self._process_function_metadata(raw_result, function_name, language)
                
                # Cache the processed result
                self._cache_metadata(function_name, language, processed)
                
                return processed
                
            except Exception as e:
                logger.error(f"Failed to fetch metadata for {function_name}: {e}")
                # Return cached data if available, even if expired
                cached = self._get_cached_metadata(function_name, language)
                if cached:
                    logger.warning(f"Using expired cache for {function_name}")
                    return cached["metadata"]
                raise
        
        raise RuntimeError("No MCP client available for metadata retrieval")
    
    def search_functions(self, 
                        query: str, 
                        limit: int = 20,
                        language: str = None) -> List[Dict[str, Any]]:
        """
        Client-side function search using local FTS index.
        
        Args:
            query: Search query string
            limit: Maximum results to return
            language: Language preference
            
        Returns:
            List of matching functions with metadata
        """
        language = language or self.default_language
        
        conn = sqlite3.connect(self.db_path)
        
        # Use FTS for fast search
        results = conn.execute("""
            SELECT DISTINCT f.function_name, f.metadata, f.cached_at
            FROM function_metadata f
            JOIN search_fts s ON f.function_name = s.function_name
            WHERE search_fts MATCH ?
            AND f.language = ?
            ORDER BY rank
            LIMIT ?
        """, (query, language, limit)).fetchall()
        
        conn.close()
        
        search_results = []
        for function_name, metadata_json, cached_at in results:
            try:
                metadata = json.loads(metadata_json)
                search_results.append({
                    "function_name": function_name,
                    "description": metadata.get("description", ""),
                    "cached_at": cached_at,
                    "metadata": metadata
                })
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in cache for {function_name}")
        
        logger.info(f"Search '{query}' returned {len(search_results)} results")
        return search_results
    
    def bulk_load_metadata(self, 
                          function_names: List[str],
                          language: str = None,
                          batch_size: int = 10) -> Dict[str, Any]:
        """
        Efficiently load metadata for multiple functions.
        
        Args:
            function_names: List of function names
            language: Language for descriptions
            batch_size: Functions to process per batch
            
        Returns:
            Summary of bulk loading operation
        """
        language = language or self.default_language
        
        results = {
            "total_requested": len(function_names),
            "cached": 0,
            "fetched": 0,
            "failed": 0,
            "functions": {}
        }
        
        # Process in batches to avoid overwhelming server
        for i in range(0, len(function_names), batch_size):
            batch = function_names[i:i + batch_size]
            
            for function_name in batch:
                try:
                    # Check cache first
                    cached = self._get_cached_metadata(function_name, language)
                    if cached and not self._is_cache_expired(cached):
                        results["cached"] += 1
                        results["functions"][function_name] = "cached"
                    else:
                        # Fetch from server
                        metadata = await self.get_function_metadata(function_name, language)
                        results["fetched"] += 1 
                        results["functions"][function_name] = "fetched"
                        
                except Exception as e:
                    logger.error(f"Failed to load metadata for {function_name}: {e}")
                    results["failed"] += 1
                    results["functions"][function_name] = f"failed: {str(e)}"
        
        logger.info(f"Bulk load completed: {results['fetched']} fetched, "
                   f"{results['cached']} cached, {results['failed']} failed")
        
        return results
    
    def export_for_rag(self, 
                      output_file: str = "rfc_metadata_rag.json",
                      language: str = None) -> str:
        """
        Export metadata in RAG-friendly format.
        
        Args:
            output_file: Output file path
            language: Language preference
            
        Returns:
            Path to exported file
        """
        language = language or self.default_language
        
        conn = sqlite3.connect(self.db_path)
        results = conn.execute("""
            SELECT function_name, metadata 
            FROM function_metadata 
            WHERE language = ?
            ORDER BY function_name
        """, (language,)).fetchall()
        conn.close()
        
        # Process for RAG format
        rag_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "language": language,
                "total_functions": len(results),
                "format": "RAG-optimized"
            },
            "functions": []
        }
        
        for function_name, metadata_json in results:
            try:
                metadata = json.loads(metadata_json)
                
                # RAG-optimized format
                rag_entry = {
                    "function_name": function_name,
                    "description": metadata.get("description", ""),
                    "search_text": self._generate_search_text(metadata),
                    "parameters": metadata.get("parameters", []),
                    "usage_context": metadata.get("usage_context", ""),
                    "metadata": metadata
                }
                
                rag_data["functions"].append(rag_entry)
                
            except json.JSONDecodeError:
                logger.warning(f"Skipping invalid metadata for {function_name}")
        
        # Save to file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rag_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(rag_data['functions'])} functions to {output_path}")
        return str(output_path)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and health information."""
        conn = sqlite3.connect(self.db_path)
        
        # Basic stats
        total_functions = conn.execute(
            "SELECT COUNT(DISTINCT function_name) FROM function_metadata"
        ).fetchone()[0]
        
        total_entries = conn.execute(
            "SELECT COUNT(*) FROM function_metadata"
        ).fetchone()[0]
        
        # Language distribution
        lang_dist = conn.execute("""
            SELECT language, COUNT(*) 
            FROM function_metadata 
            GROUP BY language
        """).fetchall()
        
        # Cache age analysis
        expired_count = conn.execute("""
            SELECT COUNT(*) FROM function_metadata 
            WHERE datetime(expires_at) < datetime('now')
        """).fetchone()[0]
        
        conn.close()
        
        return {
            "cache_file": str(self.db_path),
            "total_functions": total_functions,
            "total_entries": total_entries,
            "languages": dict(lang_dist),
            "expired_entries": expired_count,
            "cache_hit_potential": f"{((total_entries - expired_count) / max(total_entries, 1)) * 100:.1f}%"
        }
    
    def _get_cached_metadata(self, function_name: str, language: str) -> Optional[Dict]:
        """Get metadata from cache with expiry check."""
        conn = sqlite3.connect(self.db_path)
        result = conn.execute("""
            SELECT metadata, cached_at, expires_at 
            FROM function_metadata 
            WHERE function_name = ? AND language = ?
        """, (function_name, language)).fetchone()
        conn.close()
        
        if not result:
            return None
        
        metadata_json, cached_at, expires_at = result
        try:
            return {
                "metadata": json.loads(metadata_json),
                "cached_at": cached_at,
                "expires_at": expires_at
            }
        except json.JSONDecodeError:
            logger.warning(f"Invalid cached metadata for {function_name}")
            return None
    
    def _is_cache_expired(self, cached_data: Dict) -> bool:
        """Check if cached data has expired."""
        if not cached_data.get("expires_at"):
            return False
        
        expires_at = datetime.fromisoformat(cached_data["expires_at"])
        return datetime.now() > expires_at
    
    def _cache_metadata(self, function_name: str, language: str, metadata: Dict):
        """Cache metadata with search index update."""
        conn = sqlite3.connect(self.db_path)
        
        # Calculate expiry date
        expires_at = datetime.now().replace(day=datetime.now().day + self.cache_expiry_days)
        
        # Cache metadata
        conn.execute("""
            INSERT OR REPLACE INTO function_metadata 
            (function_name, language, metadata, expires_at)
            VALUES (?, ?, ?, ?)
        """, (function_name, language, json.dumps(metadata), expires_at.isoformat()))
        
        # Update search index
        search_text = self._generate_search_text(metadata)
        
        conn.execute("""
            DELETE FROM search_index 
            WHERE function_name = ? AND language = ?
        """, (function_name, language))
        
        conn.execute("""
            INSERT INTO search_index (function_name, language, search_text)
            VALUES (?, ?, ?)
        """, (function_name, language, search_text))
        
        # Update FTS index
        conn.execute("""
            INSERT OR REPLACE INTO search_fts 
            (function_name, description, parameters)
            VALUES (?, ?, ?)
        """, (
            function_name,
            metadata.get("description", ""),
            " ".join(p.get("name", "") for p in metadata.get("parameters", []))
        ))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Cached metadata for {function_name} ({language})")
    
    def _process_function_metadata(self, 
                                  raw_result: Dict, 
                                  function_name: str, 
                                  language: str) -> Dict[str, Any]:
        """Process raw RFC metadata into structured client format."""
        # Client-side processing of raw SAP metadata
        try:
            # Parse the raw result (this would be actual SAP RFC result parsing)
            processed = {
                "function_name": function_name,
                "language": language,
                "description": f"Function {function_name}",  # Extract from raw_result
                "parameters": [],  # Extract from raw_result
                "processed_at": datetime.now().isoformat(),
                "processed_by": "client",
                "raw_data": raw_result  # Keep raw data for debugging
            }
            
            # TODO: Add actual SAP RFC result parsing logic here
            # This would parse the IMPORT_PARAMETER, EXPORT_PARAMETER, etc. tables
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process metadata for {function_name}: {e}")
            # Return minimal metadata
            return {
                "function_name": function_name,
                "language": language,
                "description": f"Error processing metadata: {str(e)}",
                "parameters": [],
                "error": str(e),
                "raw_data": raw_result
            }
    
    def _generate_search_text(self, metadata: Dict) -> str:
        """Generate searchable text from metadata."""
        search_parts = [
            metadata.get("function_name", ""),
            metadata.get("description", ""),
            " ".join(p.get("name", "") for p in metadata.get("parameters", [])),
            " ".join(p.get("description", "") for p in metadata.get("parameters", []))
        ]
        
        return " ".join(filter(None, search_parts)).lower()


# Example usage and testing
async def main():
    """Example usage of RFCMetadataClient."""
    # This would typically be used with an MCP client
    metadata_client = RFCMetadataClient(cache_dir="test_cache")
    
    # Get cache stats
    stats = metadata_client.get_cache_stats()
    print(f"Cache stats: {json.dumps(stats, indent=2)}")
    
    # Search functions (will be empty initially)
    results = metadata_client.search_functions("system", limit=5)
    print(f"Search results: {len(results)} found")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
