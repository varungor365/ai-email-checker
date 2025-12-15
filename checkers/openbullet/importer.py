"""
OpenBullet Config Importer
Handles file uploads, validation, storage, and registration
"""

import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import hashlib
from datetime import datetime

from .parser import OpenBulletConfigParser
from .converter import ConfigConverter
from .executor import LoliScriptExecutor

logger = logging.getLogger(__name__)


class ConfigImporter:
    """
    Manages OpenBullet config imports
    
    Handles:
    - File upload and validation
    - Config storage and indexing
    - Dynamic checker registration
    - Config updates and versioning
    """
    
    def __init__(self, storage_dir: str = "configs/openbullet"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.parser = OpenBulletConfigParser()
        self.converter = ConfigConverter()
        self.executor = LoliScriptExecutor()
        
        # Index of installed configs
        self.index_file = self.storage_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load config index from disk"""
        
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
        
        return {'configs': {}, 'categories': {}, 'last_updated': None}
    
    def _save_index(self):
        """Save config index to disk"""
        
        self.index['last_updated'] = datetime.utcnow().isoformat()
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2)
    
    async def import_config(
        self,
        file_path: str,
        mode: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Import an OpenBullet config file
        
        Args:
            file_path: Path to .loli, .anom, or .xml file
            mode: 'auto', 'convert', or 'execute'
                  - auto: Choose best mode based on config complexity
                  - convert: Convert to native Python checker
                  - execute: Use runtime executor
        
        Returns:
            Import result with status and details
        """
        
        try:
            # Validate file
            file_path = Path(file_path)
            if not file_path.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            # Parse config
            parsed = self.parser.parse_file(str(file_path))
            metadata = parsed['metadata']
            
            # Check if already imported
            config_hash = self._calculate_hash(file_path)
            if config_hash in self.index['configs']:
                existing = self.index['configs'][config_hash]
                return {
                    'success': False,
                    'error': f'Config already imported',
                    'existing': existing
                }
            
            # Determine import mode
            if mode == 'auto':
                mode = self._choose_mode(parsed)
            
            # Copy file to storage
            stored_path = self._store_config(file_path, config_hash)
            
            # Import based on mode
            if mode == 'convert':
                result = await self._import_as_converted(
                    parsed, stored_path, config_hash
                )
            else:
                result = await self._import_as_executable(
                    parsed, stored_path, config_hash
                )
            
            # Update index
            self.index['configs'][config_hash] = {
                'name': metadata.name,
                'author': metadata.author,
                'category': metadata.category,
                'mode': mode,
                'file_path': str(stored_path),
                'imported_at': datetime.utcnow().isoformat(),
                'hash': config_hash,
                **result
            }
            
            # Update category index
            if metadata.category not in self.index['categories']:
                self.index['categories'][metadata.category] = []
            self.index['categories'][metadata.category].append(config_hash)
            
            self._save_index()
            
            return {
                'success': True,
                'config_hash': config_hash,
                'mode': mode,
                'metadata': {
                    'name': metadata.name,
                    'author': metadata.author,
                    'category': metadata.category
                },
                **result
            }
        
        except Exception as e:
            logger.error(f"Import error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def import_multiple(
        self,
        file_paths: List[str],
        mode: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Import multiple config files
        
        Args:
            file_paths: List of config file paths
            mode: Import mode for all files
            
        Returns:
            Summary of imports
        """
        
        results = []
        
        for file_path in file_paths:
            result = await self.import_config(file_path, mode)
            results.append({
                'file': file_path,
                **result
            })
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return {
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }
    
    def list_configs(
        self,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List installed configs
        
        Args:
            category: Filter by category (optional)
            
        Returns:
            List of config info
        """
        
        configs = list(self.index['configs'].values())
        
        if category:
            configs = [c for c in configs if c['category'] == category]
        
        return configs
    
    def get_config(self, config_hash: str) -> Optional[Dict[str, Any]]:
        """Get config details by hash"""
        
        return self.index['configs'].get(config_hash)
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        
        return list(self.index['categories'].keys())
    
    async def execute_config(
        self,
        config_hash: str,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ):
        """
        Execute a config by hash
        
        Args:
            config_hash: Config identifier
            email: Email to check
            password: Password to check
            proxy: Optional proxy
            fingerprint: Optional fingerprint
            
        Returns:
            CheckResult
        """
        
        config = self.get_config(config_hash)
        if not config:
            raise ValueError(f"Config not found: {config_hash}")
        
        if config['mode'] == 'convert':
            # Use converted checker
            checker_class = config['checker_class']
            # Dynamically import and execute
            # (This would require dynamic module loading)
            raise NotImplementedError("Converted checker execution not yet implemented")
        
        else:
            # Use executor
            return await self.executor.execute_config(
                config['file_path'],
                email,
                password,
                proxy,
                fingerprint
            )
    
    async def delete_config(self, config_hash: str) -> bool:
        """
        Delete an imported config
        
        Args:
            config_hash: Config identifier
            
        Returns:
            True if deleted, False if not found
        """
        
        config = self.get_config(config_hash)
        if not config:
            return False
        
        # Remove from index
        category = config['category']
        if category in self.index['categories']:
            self.index['categories'][category].remove(config_hash)
            if not self.index['categories'][category]:
                del self.index['categories'][category]
        
        del self.index['configs'][config_hash]
        
        # Delete file
        try:
            Path(config['file_path']).unlink()
            
            # Delete converted checker if exists
            if config['mode'] == 'convert' and 'checker_file' in config:
                Path(config['checker_file']).unlink()
        except Exception as e:
            logger.warning(f"Failed to delete files: {e}")
        
        self._save_index()
        
        return True
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _store_config(self, file_path: Path, config_hash: str) -> Path:
        """Copy config to storage directory"""
        
        # Create storage path
        stored_path = self.storage_dir / f"{config_hash}{file_path.suffix}"
        
        # Copy file
        import shutil
        shutil.copy2(file_path, stored_path)
        
        return stored_path
    
    def _choose_mode(self, parsed: Dict[str, Any]) -> str:
        """
        Automatically choose import mode
        
        Simple configs -> convert
        Complex configs -> execute
        """
        
        if parsed['type'] == 'anom':
            # C# configs must be executed or manually converted
            return 'execute'
        
        blocks = parsed.get('blocks', [])
        
        # Check complexity
        has_browser = any(
            b.__class__.__name__ == 'BrowserBlock'
            for b in blocks
        )
        
        has_captcha = any(
            b.__class__.__name__ == 'CaptchaBlock'
            for b in blocks
        )
        
        block_count = len(blocks)
        
        # Simple HTTP-only configs can be converted
        if not has_browser and not has_captcha and block_count < 10:
            return 'convert'
        else:
            return 'execute'
    
    async def _import_as_converted(
        self,
        parsed: Dict[str, Any],
        stored_path: Path,
        config_hash: str
    ) -> Dict[str, Any]:
        """Import config by converting to Python"""
        
        # Generate Python code
        python_code = self.converter.convert_file(str(stored_path))
        
        # Save generated checker
        checker_dir = self.storage_dir / 'generated'
        checker_dir.mkdir(exist_ok=True)
        
        checker_file = checker_dir / f"{config_hash}.py"
        
        with open(checker_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        # Extract class name
        import re
        class_match = re.search(r'class\s+(\w+)', python_code)
        class_name = class_match.group(1) if class_match else 'UnknownChecker'
        
        return {
            'checker_file': str(checker_file),
            'checker_class': class_name,
            'python_code': python_code
        }
    
    async def _import_as_executable(
        self,
        parsed: Dict[str, Any],
        stored_path: Path,
        config_hash: str
    ) -> Dict[str, Any]:
        """Import config for runtime execution"""
        
        # No conversion needed
        return {
            'execution_mode': 'runtime',
            'block_count': len(parsed.get('blocks', []))
        }
    
    def export_stats(self) -> Dict[str, Any]:
        """Get statistics about imported configs"""
        
        total_configs = len(self.index['configs'])
        
        by_category = {}
        by_mode = {'convert': 0, 'execute': 0}
        
        for config in self.index['configs'].values():
            # Count by category
            cat = config['category']
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # Count by mode
            mode = config.get('mode', 'execute')
            by_mode[mode] += 1
        
        return {
            'total': total_configs,
            'by_category': by_category,
            'by_mode': by_mode,
            'categories': list(self.index['categories'].keys()),
            'last_updated': self.index.get('last_updated')
        }


# API Integration Helper

class ConfigAPI:
    """FastAPI integration for config management"""
    
    def __init__(self, importer: ConfigImporter):
        self.importer = importer
    
    async def upload_config(
        self,
        file_content: bytes,
        filename: str,
        mode: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Handle config file upload
        
        Args:
            file_content: File bytes
            filename: Original filename
            mode: Import mode
            
        Returns:
            Import result
        """
        
        # Save to temp file
        import tempfile
        
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix=Path(filename).suffix,
            delete=False
        ) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        try:
            # Import config
            result = await self.importer.import_config(tmp_path, mode)
            
            return result
        
        finally:
            # Clean up temp file
            try:
                Path(tmp_path).unlink()
            except:
                pass
    
    async def bulk_upload(
        self,
        files: List[tuple],  # [(filename, content), ...]
        mode: str = 'auto'
    ) -> Dict[str, Any]:
        """Upload multiple config files"""
        
        import tempfile
        import shutil
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Save all files
            file_paths = []
            for filename, content in files:
                file_path = temp_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(content)
                file_paths.append(str(file_path))
            
            # Import all
            result = await self.importer.import_multiple(file_paths, mode)
            
            return result
        
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
