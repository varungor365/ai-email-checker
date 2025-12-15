"""
OpenBullet Config Parser
Parses .loli and .anom config files into structured data
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """OpenBullet config types"""
    LOLI = "loli"  # LoliScript
    ANOM = "anom"  # C# Code
    LEGACY = "legacy"  # XML format


class BlockType(Enum):
    """LoliScript block types"""
    REQUEST = "REQUEST"
    PARSE = "PARSE"
    FUNCTION = "FUNCTION"
    KEYCHECK = "KEYCHECK"
    CAPTCHA = "CAPTCHA"
    NAVIGATE = "NAVIGATE"
    BROWSERACTION = "BROWSERACTION"
    UTILITY = "UTILITY"
    TCP = "TCP"
    RECAPTCHA = "RECAPTCHA"


@dataclass
class ConfigMetadata:
    """Config metadata"""
    name: str
    author: str = "Unknown"
    category: str = "Default"
    creation_date: str = ""
    version: str = "1.0"
    base64: bool = False
    needs_proxies: bool = True
    max_bots: int = 200
    timeout: int = 7000
    allowed_word_list: str = "Default"


@dataclass
class RequestBlock:
    """HTTP Request block"""
    url: str
    method: str = "GET"
    post_data: str = ""
    content_type: str = "application/x-www-form-urlencoded"
    custom_headers: Dict[str, str] = field(default_factory=dict)
    custom_cookies: Dict[str, str] = field(default_factory=dict)
    accept_encoding: bool = True
    auto_redirect: bool = True
    read_response_source: bool = True


@dataclass
class ParseBlock:
    """Parse/Extract block"""
    label: str
    prefix: str = ""
    left: str = ""
    right: str = ""
    regex: str = ""
    source: str = "SOURCE"
    recursive: bool = False
    case_sensitive: bool = True
    encode_output: bool = False


@dataclass
class KeycheckBlock:
    """Keycheck/Condition block"""
    keys: List[Dict[str, Any]]
    ban_on_tocheck: bool = False


@dataclass
class CaptchaBlock:
    """CAPTCHA solving block"""
    captcha_type: str  # recaptcha, hcaptcha, funcaptcha, etc.
    url: str
    site_key: str = ""
    action: str = ""
    variable_name: str = "CAPTCHA_SOLUTION"


@dataclass
class BrowserBlock:
    """Browser automation block"""
    action: str  # OPEN, ELEMENTACTION, ELEMENTSCROLL, etc.
    selector: str = ""
    selector_type: str = "CSS"  # CSS, XPATH, ID, etc.
    input: str = ""
    timeout: int = 10000


class OpenBulletConfigParser:
    """
    Parser for OpenBullet configuration files
    
    Supports:
    - LoliScript (.loli)
    - Anomaly (.anom)
    - Legacy XML configs
    """
    
    def __init__(self):
        self.metadata: Optional[ConfigMetadata] = None
        self.blocks: List[Any] = []
        self.custom_inputs: Dict[str, str] = {}
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse an OpenBullet config file
        
        Args:
            file_path: Path to .loli or .anom file
            
        Returns:
            Parsed config data
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        
        # Detect config type
        if path.suffix == '.loli':
            return self._parse_loli_script(content)
        elif path.suffix == '.anom':
            return self._parse_anom_config(content)
        elif path.suffix == '.xml':
            return self._parse_legacy_xml(content)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")
    
    def _parse_loli_script(self, content: str) -> Dict[str, Any]:
        """Parse LoliScript format"""
        
        lines = content.split('\n')
        
        # Parse metadata section
        metadata_section = self._extract_section(lines, '[SETTINGS]', '[SCRIPT]')
        self.metadata = self._parse_metadata(metadata_section)
        
        # Parse custom inputs
        if '[INPUTS]' in content:
            inputs_section = self._extract_section(lines, '[INPUTS]', '[SCRIPT]')
            self.custom_inputs = self._parse_custom_inputs(inputs_section)
        
        # Parse script blocks
        script_section = self._extract_section(lines, '[SCRIPT]', None)
        self.blocks = self._parse_script_blocks(script_section)
        
        return {
            'type': ConfigType.LOLI.value,
            'metadata': self.metadata,
            'custom_inputs': self.custom_inputs,
            'blocks': self.blocks
        }
    
    def _parse_metadata(self, lines: List[str]) -> ConfigMetadata:
        """Parse metadata section"""
        
        metadata = {}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('['):
                continue
            
            # Parse key = value
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"')
                
                # Map OpenBullet keys to our format
                key_map = {
                    'Name': 'name',
                    'Author': 'author',
                    'Category': 'category',
                    'CreationDate': 'creation_date',
                    'Version': 'version',
                    'Base64': 'base64',
                    'NeedsProxies': 'needs_proxies',
                    'MaxBots': 'max_bots',
                    'Timeout': 'timeout',
                    'AllowedWordlist': 'allowed_word_list'
                }
                
                if key in key_map:
                    # Convert boolean strings
                    if value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    # Convert numbers
                    elif value.isdigit():
                        value = int(value)
                    
                    metadata[key_map[key]] = value
        
        return ConfigMetadata(**metadata) if metadata else ConfigMetadata(name="Unknown")
    
    def _parse_custom_inputs(self, lines: List[str]) -> Dict[str, str]:
        """Parse custom input definitions"""
        
        inputs = {}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('['):
                continue
            
            # Format: VariableName = "Description"
            match = re.match(r'(\w+)\s*=\s*"([^"]*)"', line)
            if match:
                var_name, description = match.groups()
                inputs[var_name] = description
        
        return inputs
    
    def _parse_script_blocks(self, lines: List[str]) -> List[Any]:
        """Parse script blocks"""
        
        blocks = []
        current_block = None
        block_lines = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Check if line starts a new block
            if line.startswith('BLOCK:'):
                # Save previous block
                if current_block and block_lines:
                    parsed_block = self._parse_block(current_block, block_lines)
                    if parsed_block:
                        blocks.append(parsed_block)
                
                # Start new block
                block_type = line.replace('BLOCK:', '').strip()
                current_block = block_type
                block_lines = []
            
            elif line == 'ENDBLOCK':
                # End current block
                if current_block and block_lines:
                    parsed_block = self._parse_block(current_block, block_lines)
                    if parsed_block:
                        blocks.append(parsed_block)
                
                current_block = None
                block_lines = []
            
            else:
                # Add line to current block
                if current_block:
                    block_lines.append(line)
        
        return blocks
    
    def _parse_block(self, block_type: str, lines: List[str]) -> Optional[Any]:
        """Parse a specific block type"""
        
        # Remove label and disabled lines
        filtered_lines = []
        label = ""
        
        for line in lines:
            if line.startswith('LABEL:'):
                label = line.replace('LABEL:', '').strip()
            elif line.startswith('DISABLED'):
                continue
            else:
                filtered_lines.append(line)
        
        lines = filtered_lines
        
        if block_type == 'REQUEST':
            return self._parse_request_block(lines, label)
        elif block_type == 'PARSE':
            return self._parse_parse_block(lines, label)
        elif block_type == 'KEYCHECK':
            return self._parse_keycheck_block(lines)
        elif block_type in ['RECAPTCHA', 'CAPTCHA']:
            return self._parse_captcha_block(lines, label)
        elif block_type in ['NAVIGATE', 'BROWSERACTION', 'ELEMENTACTION']:
            return self._parse_browser_block(block_type, lines, label)
        else:
            # Generic block
            return {
                'type': block_type,
                'label': label,
                'lines': lines
            }
    
    def _parse_request_block(self, lines: List[str], label: str) -> RequestBlock:
        """Parse REQUEST block"""
        
        data = {'label': label}
        
        for line in lines:
            # URL
            if line.startswith('URL '):
                data['url'] = line.replace('URL ', '').strip().strip('"')
            
            # Method
            elif line in ['GET', 'POST', 'PUT', 'DELETE']:
                data['method'] = line
            
            # POST data
            elif line.startswith('POSTDATA '):
                data['post_data'] = line.replace('POSTDATA ', '').strip().strip('"')
            
            # Content Type
            elif line.startswith('CONTENT '):
                data['content_type'] = line.replace('CONTENT ', '').strip().strip('"')
            
            # Custom headers
            elif line.startswith('HEADER '):
                header_line = line.replace('HEADER ', '').strip()
                if ':' in header_line:
                    key, value = header_line.split(':', 1)
                    if 'custom_headers' not in data:
                        data['custom_headers'] = {}
                    data['custom_headers'][key.strip().strip('"')] = value.strip().strip('"')
            
            # Custom cookies
            elif line.startswith('COOKIE '):
                cookie_line = line.replace('COOKIE ', '').strip()
                if ':' in cookie_line:
                    key, value = cookie_line.split(':', 1)
                    if 'custom_cookies' not in data:
                        data['custom_cookies'] = {}
                    data['custom_cookies'][key.strip().strip('"')] = value.strip().strip('"')
        
        return RequestBlock(**data) if 'url' in data else None
    
    def _parse_parse_block(self, lines: List[str], label: str) -> ParseBlock:
        """Parse PARSE block"""
        
        data = {'label': label}
        
        for line in lines:
            # Left/Right string parsing
            if line.startswith('LR '):
                parts = line.replace('LR ', '').strip().strip('"').split('" "')
                if len(parts) >= 2:
                    data['left'] = parts[0].strip('"')
                    data['right'] = parts[1].strip('"')
                    if len(parts) >= 3:
                        data['source'] = parts[2].strip('"')
            
            # Regex parsing
            elif line.startswith('REGEX '):
                parts = line.replace('REGEX ', '').strip().strip('"').split('" "')
                if parts:
                    data['regex'] = parts[0].strip('"')
                    if len(parts) >= 2:
                        data['source'] = parts[1].strip('"')
            
            # JSON parsing
            elif line.startswith('JSON '):
                data['json_path'] = line.replace('JSON ', '').strip().strip('"')
            
            # Flags
            elif 'Recursive' in line:
                data['recursive'] = True
            elif 'CaseSensitive' in line:
                data['case_sensitive'] = 'False' not in line
        
        return ParseBlock(**data) if 'label' in data else None
    
    def _parse_keycheck_block(self, lines: List[str]) -> KeycheckBlock:
        """Parse KEYCHECK block"""
        
        keys = []
        
        for line in lines:
            if line.startswith('KEYCHAIN '):
                # Parse keychain condition
                condition = line.replace('KEYCHAIN ', '').strip()
                
                # Parse Success/Failure/Ban/Retry/Custom conditions
                if 'SUCCESS' in condition:
                    result = 'SUCCESS'
                elif 'FAIL' in condition:
                    result = 'FAILURE'
                elif 'BAN' in condition:
                    result = 'BAN'
                elif 'RETRY' in condition:
                    result = 'RETRY'
                else:
                    result = 'CUSTOM'
                
                # Extract key conditions
                # Format: Success OR Key Contains "text"
                keys.append({
                    'condition': condition,
                    'result': result
                })
        
        return KeycheckBlock(keys=keys)
    
    def _parse_captcha_block(self, lines: List[str], label: str) -> CaptchaBlock:
        """Parse CAPTCHA block"""
        
        data = {
            'variable_name': label or 'CAPTCHA_SOLUTION',
            'captcha_type': 'recaptcha'
        }
        
        for line in lines:
            if line.startswith('URL '):
                data['url'] = line.replace('URL ', '').strip().strip('"')
            elif line.startswith('SITEKEY '):
                data['site_key'] = line.replace('SITEKEY ', '').strip().strip('"')
            elif 'hCaptcha' in line:
                data['captcha_type'] = 'hcaptcha'
            elif 'FunCaptcha' in line:
                data['captcha_type'] = 'funcaptcha'
        
        return CaptchaBlock(**data)
    
    def _parse_browser_block(self, block_type: str, lines: List[str], label: str) -> BrowserBlock:
        """Parse browser automation block"""
        
        data = {'action': block_type}
        
        for line in lines:
            if line.startswith('URL '):
                data['url'] = line.replace('URL ', '').strip().strip('"')
            elif line.startswith('SELECTOR '):
                parts = line.replace('SELECTOR ', '').split()
                if len(parts) >= 2:
                    data['selector_type'] = parts[0]
                    data['selector'] = ' '.join(parts[1:]).strip('"')
            elif line.startswith('INPUT '):
                data['input'] = line.replace('INPUT ', '').strip().strip('"')
        
        return BrowserBlock(**data)
    
    def _parse_anom_config(self, content: str) -> Dict[str, Any]:
        """Parse Anomaly C# config format"""
        
        # Extract metadata from C# comments
        metadata = self._extract_anom_metadata(content)
        
        # Parse C# code structure
        # This is more complex and would require C# parsing
        # For now, we store the raw code
        
        return {
            'type': ConfigType.ANOM.value,
            'metadata': metadata,
            'code': content
        }
    
    def _parse_legacy_xml(self, content: str) -> Dict[str, Any]:
        """Parse legacy XML config format"""
        
        # This would use XML parsing
        # For now, basic implementation
        
        return {
            'type': ConfigType.LEGACY.value,
            'xml': content
        }
    
    def _extract_section(self, lines: List[str], start_marker: str, end_marker: Optional[str]) -> List[str]:
        """Extract section between markers"""
        
        section = []
        in_section = False
        
        for line in lines:
            if start_marker in line:
                in_section = True
                continue
            
            if end_marker and end_marker in line:
                break
            
            if in_section:
                section.append(line)
        
        return section
    
    def _extract_anom_metadata(self, content: str) -> ConfigMetadata:
        """Extract metadata from Anomaly C# comments"""
        
        metadata = {}
        
        # Look for comments at the top
        for line in content.split('\n')[:20]:
            if '//' in line:
                line = line.split('//', 1)[1].strip()
                
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'name' in key:
                        metadata['name'] = value
                    elif 'author' in key:
                        metadata['author'] = value
                    elif 'category' in key:
                        metadata['category'] = value
        
        return ConfigMetadata(**metadata) if metadata else ConfigMetadata(name="Anomaly Config")
