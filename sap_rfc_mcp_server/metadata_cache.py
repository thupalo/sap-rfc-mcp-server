"""RFC Function Metadata Cache Manager for MCP Server."""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib

logger = logging.getLogger(__name__)


class RFCMetadataCache:
    """Manages persistent caching of RFC function metadata."""
    
    def __init__(self, cache_dir: str = "cache", cache_ttl_hours: int = 24):
        """
        Initialize metadata cache.
        
        Args:
            cache_dir: Directory to store cache files
            cache_ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # Cache files
        self.metadata_file = self.cache_dir / "rfc_metadata.json"
        self.index_file = self.cache_dir / "rfc_index.json"
        self.search_file = self.cache_dir / "rfc_search.json"
        
        # Load existing cache
        self._metadata_cache: Dict[str, Any] = self._load_cache(self.metadata_file)
        self._index_cache: Dict[str, Any] = self._load_cache(self.index_file)
        self._search_cache: Dict[str, List[str]] = self._load_cache(self.search_file)
    
    def _load_cache(self, file_path: Path) -> Dict[str, Any]:
        """Load cache from JSON file."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache from {file_path}: {e}")
        return {}
    
    def _save_cache(self, data: Dict[str, Any], file_path: Path) -> None:
        """Save cache to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save cache to {file_path}: {e}")
    
    def _is_cache_valid(self, timestamp_str: str) -> bool:
        """Check if cache entry is still valid."""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            return datetime.now() - timestamp < self.cache_ttl
        except Exception:
            return False
    
    def get_function_metadata(self, func_name: str) -> Optional[Dict[str, Any]]:
        """Get cached metadata for a function."""
        entry = self._metadata_cache.get(func_name)
        if entry and self._is_cache_valid(entry.get('cached_at', '')):
            logger.debug(f"Cache hit for function: {func_name}")
            return entry['metadata']
        
        # Remove expired entry
        if entry:
            logger.debug(f"Cache expired for function: {func_name}")
            del self._metadata_cache[func_name]
        
        return None
    
    def store_function_metadata(self, func_name: str, metadata: Dict[str, Any]) -> None:
        """Store function metadata in cache."""
        entry = {
            'metadata': metadata,
            'cached_at': datetime.now().isoformat(),
            'func_name': func_name
        }
        
        self._metadata_cache[func_name] = entry
        self._save_cache(self._metadata_cache, self.metadata_file)
        
        # Update search index
        self._update_search_index(func_name, metadata)
        
        logger.debug(f"Cached metadata for function: {func_name}")
    
    def _update_search_index(self, func_name: str, metadata: Dict[str, Any]) -> None:
        """Update search index for RAG applications."""
        search_terms = set()
        
        # Extract searchable terms
        search_terms.add(func_name.lower())
        
        # From function metadata
        func_meta = metadata.get('_metadata', {})
        if 'STEXT' in func_meta:
            search_terms.update(func_meta['STEXT'].lower().split())
        if 'AREA' in func_meta:
            search_terms.add(func_meta['AREA'].lower())
        if 'DEVCLASS' in func_meta:
            search_terms.add(func_meta['DEVCLASS'].lower())
        
        # From parameters
        for param_type in ['inputs', 'outputs', 'tables']:
            params = metadata.get(param_type, {})
            for param_name, param_info in params.items():
                search_terms.add(param_name.lower())
                if isinstance(param_info, dict) and '_description' in param_info:
                    search_terms.update(param_info['_description'].lower().split())
        
        # Update reverse index
        for term in search_terms:
            if term not in self._search_cache:
                self._search_cache[term] = []
            if func_name not in self._search_cache[term]:
                self._search_cache[term].append(func_name)
        
        self._save_cache(self._search_cache, self.search_file)
    
    def search_functions(self, query: str, limit: int = 20) -> List[str]:
        """Search for functions by keywords."""
        query_terms = query.lower().split()
        function_scores = {}
        
        for term in query_terms:
            # Exact matches
            if term in self._search_cache:
                for func_name in self._search_cache[term]:
                    function_scores[func_name] = function_scores.get(func_name, 0) + 2
            
            # Partial matches
            for search_term, func_names in self._search_cache.items():
                if term in search_term or search_term in term:
                    for func_name in func_names:
                        function_scores[func_name] = function_scores.get(func_name, 0) + 1
        
        # Sort by score and return top results
        sorted_functions = sorted(function_scores.items(), key=lambda x: x[1], reverse=True)
        return [func_name for func_name, _ in sorted_functions[:limit]]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_functions = len(self._metadata_cache)
        valid_functions = sum(
            1 for entry in self._metadata_cache.values() 
            if self._is_cache_valid(entry.get('cached_at', ''))
        )
        
        return {
            'total_cached_functions': total_functions,
            'valid_cached_functions': valid_functions,
            'expired_functions': total_functions - valid_functions,
            'search_terms': len(self._search_cache),
            'cache_size_mb': self._get_cache_size_mb()
        }
    
    def _get_cache_size_mb(self) -> float:
        """Calculate total cache size in MB."""
        total_size = 0
        for file_path in [self.metadata_file, self.index_file, self.search_file]:
            if file_path.exists():
                total_size += file_path.stat().st_size
        return round(total_size / (1024 * 1024), 2)
    
    def clear_expired(self) -> int:
        """Remove expired cache entries."""
        expired_count = 0
        expired_functions = []
        
        for func_name, entry in list(self._metadata_cache.items()):
            if not self._is_cache_valid(entry.get('cached_at', '')):
                expired_functions.append(func_name)
                del self._metadata_cache[func_name]
                expired_count += 1
        
        if expired_count > 0:
            self._save_cache(self._metadata_cache, self.metadata_file)
            logger.info(f"Removed {expired_count} expired cache entries")
        
        return expired_count
    
    def export_for_rag(self, output_file: str) -> None:
        """Export metadata in RAG-friendly format."""
        rag_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'total_functions': len(self._metadata_cache),
                'schema_version': '1.0'
            },
            'functions': {}
        }
        
        for func_name, entry in self._metadata_cache.items():
            if self._is_cache_valid(entry.get('cached_at', '')):
                metadata = entry['metadata']
                
                # Create RAG-friendly representation
                rag_entry = {
                    'function_name': func_name,
                    'description': metadata.get('_metadata', {}).get('description', ''),
                    'area': metadata.get('_metadata', {}).get('area', ''),
                    'dev_class': metadata.get('_metadata', {}).get('dev_class', ''),
                    'parameters': {
                        'inputs': self._flatten_parameters(metadata.get('inputs', {})),
                        'outputs': self._flatten_parameters(metadata.get('outputs', {})),
                        'tables': self._flatten_parameters(metadata.get('tables', {}))
                    },
                    'search_text': self._generate_search_text(func_name, metadata)
                }
                
                rag_data['functions'][func_name] = rag_entry
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rag_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(rag_data['functions'])} functions to {output_file}")
    
    def _flatten_parameters(self, params: Dict[str, Any]) -> List[Dict[str, str]]:
        """Flatten parameter structure for RAG."""
        flattened = []
        for name, info in params.items():
            if isinstance(info, dict):
                flattened.append({
                    'name': name,
                    'type': info.get('type', 'UNKNOWN'),
                    'description': info.get('description', ''),
                    'default': info.get('default', '')
                })
            elif isinstance(info, list) and info:
                # Handle table parameters
                flattened.append({
                    'name': name,
                    'type': 'TABLE',
                    'description': f"Table with {len(info[0])} fields" if info[0] else "Table",
                    'default': ''
                })
        return flattened
    
    def _generate_search_text(self, func_name: str, metadata: Dict[str, Any]) -> str:
        """Generate searchable text for the function."""
        text_parts = [func_name]
        
        func_meta = metadata.get('_metadata', {})
        if func_meta.get('description'):
            text_parts.append(func_meta['description'])
        
        # Add parameter descriptions
        for param_type in ['inputs', 'outputs', 'tables']:
            params = metadata.get(param_type, {})
            for param_name, param_info in params.items():
                text_parts.append(param_name)
                if isinstance(param_info, dict) and 'description' in param_info:
                    text_parts.append(param_info['description'])
        
        return ' '.join(text_parts)
