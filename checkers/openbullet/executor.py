"""
OpenBullet LoliScript Executor
Executes LoliScript blocks in runtime without conversion
"""

import logging
import asyncio
import aiohttp
import re
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Page

from .parser import (
    OpenBulletConfigParser, RequestBlock, ParseBlock,
    KeycheckBlock, CaptchaBlock, BrowserBlock
)
from ..base import CheckResult, CheckerResult

logger = logging.getLogger(__name__)


class LoliScriptExecutor:
    """
    Runtime executor for LoliScript blocks
    
    Executes OpenBullet configs directly without conversion to Python code.
    Provides runtime interpretation of LoliScript commands.
    """
    
    def __init__(self, captcha_solver=None):
        self.parser = OpenBulletConfigParser()
        self.captcha_solver = captcha_solver
        self.variables: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}
    
    async def execute_config(
        self,
        config_path: str,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """
        Execute an OpenBullet config file
        
        Args:
            config_path: Path to .loli or .anom file
            email: Email to check
            password: Password to check
            proxy: Optional proxy object
            fingerprint: Optional fingerprint object
            
        Returns:
            CheckResult with outcome
        """
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Parse the config
            parsed = self.parser.parse_file(config_path)
            
            if parsed['type'] != 'loli':
                raise ValueError("Only LoliScript configs are supported for execution")
            
            metadata = parsed['metadata']
            blocks = parsed['blocks']
            custom_inputs = parsed.get('custom_inputs', {})
            
            # Initialize variables
            self._init_variables(email, password, custom_inputs)
            
            # Determine execution mode (HTTP vs Browser)
            needs_browser = any(
                isinstance(block, (BrowserBlock, dict)) and
                (isinstance(block, BrowserBlock) or block.get('type') in ['NAVIGATE', 'BROWSERACTION'])
                for block in blocks
            )
            
            if needs_browser:
                result = await self._execute_browser_blocks(
                    blocks, email, metadata.name, proxy, fingerprint
                )
            else:
                result = await self._execute_http_blocks(
                    blocks, email, metadata.name, proxy, metadata.timeout
                )
            
            # Add response time
            result.response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return result
        
        except Exception as e:
            logger.error(f"Config execution error: {e}", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service="openbullet",
                message=f"Execution error: {str(e)}"
            )
    
    def _init_variables(self, email: str, password: str, custom_inputs: Dict[str, str]):
        """Initialize standard variables"""
        
        self.variables = {
            'INPUT': f'{email}:{password}',
            'EMAIL': email,
            'USER': email,
            'PASS': password,
            'PASSWORD': password
        }
        
        # Add custom inputs
        for var_name in custom_inputs.keys():
            self.variables[var_name] = ''  # Default empty, user should set
        
        self.cookies = {}
    
    async def _execute_http_blocks(
        self,
        blocks: List[Any],
        email: str,
        service_name: str,
        proxy: Optional[Any],
        timeout: int
    ) -> CheckResult:
        """Execute blocks using HTTP requests"""
        
        proxy_url = proxy.get_url() if proxy else None
        timeout_config = aiohttp.ClientTimeout(total=timeout / 1000)
        
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            for i, block in enumerate(blocks):
                try:
                    if isinstance(block, RequestBlock):
                        await self._execute_request_block(session, block, proxy_url)
                    
                    elif isinstance(block, ParseBlock):
                        self._execute_parse_block(block)
                    
                    elif isinstance(block, KeycheckBlock):
                        result = self._execute_keycheck_block(block, email, service_name)
                        if result:
                            return result
                    
                    elif isinstance(block, CaptchaBlock):
                        await self._execute_captcha_block(block)
                
                except Exception as e:
                    logger.error(f"Block {i} execution error: {e}")
                    # Continue to next block unless it's critical
            
            # If no keycheck returned success, it's a failure
            return CheckResult(
                status=CheckerResult.FAILURE,
                email=email,
                service=service_name,
                message="No success condition met"
            )
    
    async def _execute_browser_blocks(
        self,
        blocks: List[Any],
        email: str,
        service_name: str,
        proxy: Optional[Any],
        fingerprint: Optional[Any]
    ) -> CheckResult:
        """Execute blocks using browser automation"""
        
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
            
            try:
                for i, block in enumerate(blocks):
                    try:
                        if isinstance(block, BrowserBlock):
                            await self._execute_browser_block(page, block)
                        
                        elif isinstance(block, ParseBlock):
                            await self._execute_browser_parse_block(page, block)
                        
                        elif isinstance(block, KeycheckBlock):
                            result = self._execute_keycheck_block(block, email, service_name)
                            if result:
                                return result
                        
                        elif isinstance(block, CaptchaBlock):
                            await self._execute_captcha_block(block)
                    
                    except Exception as e:
                        logger.error(f"Browser block {i} error: {e}")
                
                return CheckResult(
                    status=CheckerResult.FAILURE,
                    email=email,
                    service=service_name,
                    message="No success condition met"
                )
            
            finally:
                await browser.close()
    
    async def _execute_request_block(
        self,
        session: aiohttp.ClientSession,
        block: RequestBlock,
        proxy_url: Optional[str]
    ):
        """Execute HTTP request block"""
        
        # Replace variables in URL
        url = self._replace_variables(block.url)
        
        # Prepare POST data
        post_data = None
        if block.post_data:
            post_data = self._replace_variables(block.post_data)
        
        # Prepare headers
        headers = {}
        if block.custom_headers:
            headers = {
                k: self._replace_variables(v)
                for k, v in block.custom_headers.items()
            }
        
        # Prepare cookies
        if block.custom_cookies:
            cookie_str = '; '.join([
                f'{k}={self._replace_variables(v)}'
                for k, v in block.custom_cookies.items()
            ])
            headers['Cookie'] = cookie_str
        
        # Execute request
        async with session.request(
            method=block.method,
            url=url,
            data=post_data,
            headers=headers,
            proxy=proxy_url
        ) as response:
            response_text = await response.text()
            
            # Store response in variables
            self.variables['SOURCE'] = response_text
            self.variables['RESPONSECODE'] = str(response.status)
            self.variables['ADDRESS'] = str(response.url)
            
            # Store cookies
            for cookie in response.cookies:
                cookie_name = cookie.key
                cookie_value = cookie.value
                self.cookies[cookie_name] = cookie_value
                self.variables[f'COOKIE_{cookie_name}'] = cookie_value
            
            logger.debug(f"REQUEST: {block.method} {url} -> {response.status}")
    
    def _execute_parse_block(self, block: ParseBlock):
        """Execute parse block"""
        
        # Get source data
        source_data = self.variables.get(block.source, '')
        
        parsed_value = ''
        
        # Left-Right parsing
        if block.left and block.right:
            parsed_value = self._parse_between(
                source_data,
                block.left,
                block.right,
                block.recursive
            )
        
        # Regex parsing
        elif block.regex:
            match = re.search(block.regex, source_data)
            if match:
                parsed_value = match.group(1) if len(match.groups()) > 0 else match.group(0)
        
        # JSON parsing
        elif block.json_path:
            try:
                import json
                data = json.loads(source_data)
                # Simple JSON path support (e.g., "user.id")
                keys = block.json_path.split('.')
                value = data
                for key in keys:
                    if isinstance(value, dict):
                        value = value.get(key, '')
                    else:
                        value = ''
                        break
                parsed_value = str(value)
            except:
                parsed_value = ''
        
        # Store result
        self.variables[block.label] = parsed_value
        
        logger.debug(f"PARSE: {block.label} = '{parsed_value[:50]}'")
    
    def _execute_keycheck_block(
        self,
        block: KeycheckBlock,
        email: str,
        service_name: str
    ) -> Optional[CheckResult]:
        """
        Execute keycheck block
        
        Returns CheckResult if a condition matches, None otherwise
        """
        
        for key_condition in block.keys:
            condition = key_condition['condition']
            result = key_condition['result']
            
            # Evaluate condition
            if self._evaluate_condition(condition):
                # Map OpenBullet result to CheckerResult
                if result == 'SUCCESS':
                    return CheckResult(
                        status=CheckerResult.SUCCESS,
                        email=email,
                        password=self.variables.get('PASSWORD', ''),
                        service=service_name,
                        message="Login successful",
                        session_data={
                            'cookies': self.cookies.copy(),
                            'variables': self.variables.copy()
                        }
                    )
                
                elif result == 'BAN':
                    return CheckResult(
                        status=CheckerResult.IP_BLOCKED,
                        email=email,
                        service=service_name,
                        message="IP banned or blocked"
                    )
                
                elif result == 'RETRY':
                    return CheckResult(
                        status=CheckerResult.RATE_LIMITED,
                        email=email,
                        service=service_name,
                        message="Rate limited, retry needed"
                    )
                
                elif result == 'CUSTOM':
                    # Custom result - treat as info
                    custom_msg = key_condition.get('custom', 'Custom condition met')
                    logger.info(f"Custom keycheck: {custom_msg}")
                    # Don't return, continue checking
        
        return None
    
    async def _execute_captcha_block(self, block: CaptchaBlock):
        """Execute CAPTCHA solving block"""
        
        if not self.captcha_solver:
            logger.warning("CAPTCHA detected but no solver configured")
            return
        
        # Solve CAPTCHA
        solution = await self.captcha_solver.solve(
            captcha_type=block.captcha_type,
            site_key=block.site_key,
            page_url=block.url
        )
        
        # Store solution
        self.variables[block.variable_name] = solution
        
        logger.debug(f"CAPTCHA: Solved {block.captcha_type}")
    
    async def _execute_browser_block(self, page: Page, block: BrowserBlock):
        """Execute browser action block"""
        
        action = block.action.upper()
        
        if action == 'OPEN' or action == 'NAVIGATE':
            url = self._replace_variables(block.url)
            await page.goto(url, wait_until='networkidle')
            
            # Store page content
            content = await page.content()
            self.variables['SOURCE'] = content
            
            logger.debug(f"BROWSER: Navigate to {url}")
        
        elif action == 'ELEMENTACTION':
            selector = block.selector
            input_value = self._replace_variables(block.input) if block.input else ''
            
            if 'click' in input_value.lower() or not input_value:
                await page.click(selector)
                logger.debug(f"BROWSER: Click {selector}")
            
            elif input_value:
                await page.fill(selector, input_value)
                logger.debug(f"BROWSER: Fill {selector}")
        
        elif action == 'WAIT':
            wait_time = int(block.input) if block.input else 1000
            await asyncio.sleep(wait_time / 1000)
            logger.debug(f"BROWSER: Wait {wait_time}ms")
        
        elif action == 'SCREENSHOT':
            screenshot = await page.screenshot()
            self.variables['SCREENSHOT'] = screenshot.hex()
            logger.debug("BROWSER: Screenshot taken")
    
    async def _execute_browser_parse_block(self, page: Page, block: ParseBlock):
        """Execute parse block in browser context"""
        
        # Get page content
        if block.source == 'SOURCE' or not block.source:
            source_data = await page.content()
        else:
            source_data = self.variables.get(block.source, '')
        
        # Use standard parsing logic
        self.variables[block.source] = source_data
        self._execute_parse_block(block)
    
    def _replace_variables(self, text: str) -> str:
        """Replace <VARIABLE> syntax with actual values"""
        
        if not text:
            return text
        
        # Replace all <VARIABLE> patterns
        pattern = r'<([A-Z_][A-Z0-9_]*)>'
        
        def replace_func(match):
            var_name = match.group(1)
            return self.variables.get(var_name, '')
        
        return re.sub(pattern, replace_func, text)
    
    def _parse_between(
        self,
        text: str,
        left: str,
        right: str,
        recursive: bool = False
    ) -> str:
        """Parse text between left and right delimiters"""
        
        try:
            # Replace variables in delimiters
            left = self._replace_variables(left)
            right = self._replace_variables(right)
            
            if not left:
                # No left delimiter - parse from start
                end = text.index(right)
                return text[:end]
            
            if not right:
                # No right delimiter - parse to end
                start = text.index(left) + len(left)
                return text[start:]
            
            # Both delimiters present
            start = text.index(left) + len(left)
            end = text.index(right, start)
            result = text[start:end]
            
            if recursive:
                # Continue parsing
                remaining = text[end + len(right):]
                if left in remaining:
                    result += ',' + self._parse_between(remaining, left, right, True)
            
            return result
        
        except (ValueError, IndexError):
            return ''
    
    def _evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate OpenBullet keycheck condition
        
        Supports:
        - Key Contains "text"
        - Source Contains "text"
        - ResponseCode Equals 200
        - Variable Exists
        """
        
        # Replace variables
        condition = self._replace_variables(condition)
        
        # Parse condition type
        if 'Contains' in condition:
            parts = condition.split('Contains', 1)
            if len(parts) != 2:
                return False
            
            var_name = parts[0].strip()
            search_text = parts[1].strip().strip('"\'')
            
            # Get variable value
            if var_name.upper() == 'SOURCE':
                var_value = self.variables.get('SOURCE', '')
            elif var_name.upper() == 'KEY':
                # Key is alias for any captured variable
                var_value = ' '.join(self.variables.values())
            else:
                var_value = self.variables.get(var_name, '')
            
            return search_text in var_value
        
        elif 'Equals' in condition:
            parts = condition.split('Equals', 1)
            if len(parts) != 2:
                return False
            
            var_name = parts[0].strip()
            expected_value = parts[1].strip().strip('"\'')
            
            var_value = self.variables.get(var_name, '')
            
            return var_value == expected_value
        
        elif 'Exists' in condition:
            var_name = condition.replace('Exists', '').strip()
            return var_name in self.variables and bool(self.variables[var_name])
        
        elif 'DoesNotContain' in condition:
            parts = condition.split('DoesNotContain', 1)
            if len(parts) != 2:
                return False
            
            var_name = parts[0].strip()
            search_text = parts[1].strip().strip('"\'')
            
            var_value = self.variables.get(var_name, '')
            
            return search_text not in var_value
        
        else:
            logger.warning(f"Unknown condition format: {condition}")
            return False
