"""
Browser Fingerprint Generation
Creates unique, realistic browser fingerprints to evade detection
"""

import logging
import random
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class BrowserFingerprint:
    """Complete browser fingerprint"""
    # User Agent
    user_agent: str
    
    # Browser properties
    browser_name: str
    browser_version: str
    platform: str
    platform_version: str
    
    # Screen properties
    screen_width: int
    screen_height: int
    screen_color_depth: int
    screen_pixel_ratio: float
    
    # WebGL fingerprint
    webgl_vendor: str
    webgl_renderer: str
    webgl_unmasked_vendor: str
    webgl_unmasked_renderer: str
    
    # Canvas fingerprint
    canvas_hash: str
    
    # Audio fingerprint
    audio_hash: str
    
    # Fonts
    available_fonts: List[str]
    
    # Plugins (deprecated but some sites still check)
    plugins: List[Dict[str, str]]
    
    # Language & timezone
    languages: List[str]
    timezone: str
    timezone_offset: int
    
    # Hardware
    hardware_concurrency: int
    device_memory: int
    
    # WebRTC
    webrtc_enabled: bool
    
    # Misc
    do_not_track: Optional[str]
    cookie_enabled: bool
    java_enabled: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for injection into browser"""
        return {
            'userAgent': self.user_agent,
            'platform': self.platform,
            'screen': {
                'width': self.screen_width,
                'height': self.screen_height,
                'colorDepth': self.screen_color_depth,
                'pixelRatio': self.screen_pixel_ratio
            },
            'webgl': {
                'vendor': self.webgl_vendor,
                'renderer': self.webgl_renderer,
                'unmaskedVendor': self.webgl_unmasked_vendor,
                'unmaskedRenderer': self.webgl_unmasked_renderer
            },
            'canvas': self.canvas_hash,
            'audio': self.audio_hash,
            'fonts': self.available_fonts,
            'languages': self.languages,
            'timezone': self.timezone,
            'timezoneOffset': self.timezone_offset,
            'hardwareConcurrency': self.hardware_concurrency,
            'deviceMemory': self.device_memory,
            'webrtc': self.webrtc_enabled,
            'doNotTrack': self.do_not_track,
            'cookieEnabled': self.cookie_enabled
        }


class FingerprintGenerator:
    """
    Generates realistic, unique browser fingerprints
    
    Features:
    - Consistent fingerprint sets (e.g., Chrome on Windows)
    - Randomized but realistic values
    - Canvas/WebGL/Audio fingerprinting
    - Font detection evasion
    """
    
    # Realistic browser/OS combinations
    BROWSER_PROFILES = [
        {
            'name': 'Chrome',
            'versions': ['120.0.6099.109', '120.0.6099.130', '121.0.6167.85', '121.0.6167.140'],
            'platforms': ['Windows', 'macOS', 'Linux'],
            'webgl_vendors': ['Google Inc. (NVIDIA)', 'Google Inc. (Intel)', 'Google Inc. (AMD)']
        },
        {
            'name': 'Firefox',
            'versions': ['122.0', '121.0', '120.0'],
            'platforms': ['Windows', 'macOS', 'Linux'],
            'webgl_vendors': ['Mozilla', 'Mozilla Foundation']
        },
        {
            'name': 'Edge',
            'versions': ['120.0.2210.121', '120.0.2210.144', '121.0.2277.83'],
            'platforms': ['Windows', 'macOS'],
            'webgl_vendors': ['Google Inc. (NVIDIA)', 'Google Inc. (Intel)']
        },
        {
            'name': 'Safari',
            'versions': ['17.2.1', '17.1', '16.6'],
            'platforms': ['macOS'],
            'webgl_vendors': ['Apple Inc.']
        }
    ]
    
    SCREEN_RESOLUTIONS = [
        (1920, 1080), (2560, 1440), (1366, 768), (1536, 864),
        (1440, 900), (1680, 1050), (3840, 2160), (2560, 1600)
    ]
    
    COMMON_FONTS = [
        'Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana',
        'Georgia', 'Palatino', 'Garamond', 'Bookman', 'Comic Sans MS',
        'Trebuchet MS', 'Impact', 'Lucida Console', 'Tahoma', 'Calibri',
        'Cambria', 'Segoe UI', 'Roboto', 'Open Sans', 'Lato'
    ]
    
    LANGUAGES = [
        ['en-US', 'en'], ['en-GB', 'en'], ['de-DE', 'de'], ['fr-FR', 'fr'],
        ['es-ES', 'es'], ['it-IT', 'it'], ['pt-BR', 'pt'], ['ru-RU', 'ru'],
        ['ja-JP', 'ja'], ['zh-CN', 'zh'], ['ko-KR', 'ko']
    ]
    
    TIMEZONES = [
        ('America/New_York', -300), ('America/Los_Angeles', -480),
        ('America/Chicago', -360), ('Europe/London', 0),
        ('Europe/Paris', 60), ('Europe/Berlin', 60),
        ('Asia/Tokyo', 540), ('Asia/Shanghai', 480),
        ('Australia/Sydney', 660)
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        logger.info("Fingerprint Generator initialized")
    
    def generate(self, profile: Optional[str] = None) -> BrowserFingerprint:
        """
        Generate a complete, realistic browser fingerprint
        
        Args:
            profile: Browser profile name (Chrome, Firefox, etc.) or None for random
        
        Returns:
            BrowserFingerprint instance
        """
        
        # Select browser profile
        if profile:
            browser_profile = next(
                (b for b in self.BROWSER_PROFILES if b['name'].lower() == profile.lower()),
                random.choice(self.BROWSER_PROFILES)
            )
        else:
            browser_profile = random.choice(self.BROWSER_PROFILES)
        
        browser_name = browser_profile['name']
        browser_version = random.choice(browser_profile['versions'])
        platform = random.choice(browser_profile['platforms'])
        
        # Generate platform-specific details
        if platform == 'Windows':
            platform_version = random.choice(['10.0', '11.0'])
            platform_string = f'Win32'
        elif platform == 'macOS':
            platform_version = random.choice(['10_15_7', '11_0', '12_0', '13_0'])
            platform_string = 'MacIntel'
        else:  # Linux
            platform_version = 'x86_64'
            platform_string = 'Linux x86_64'
        
        # Generate User-Agent
        user_agent = self._generate_user_agent(
            browser_name, browser_version, platform, platform_version
        )
        
        # Screen resolution
        screen_width, screen_height = random.choice(self.SCREEN_RESOLUTIONS)
        screen_color_depth = 24
        screen_pixel_ratio = random.choice([1.0, 1.25, 1.5, 2.0])
        
        # WebGL fingerprint
        webgl_vendor = random.choice(browser_profile['webgl_vendors'])
        webgl_renderer = self._generate_webgl_renderer(platform)
        
        # Canvas fingerprint (unique hash)
        canvas_hash = self._generate_canvas_hash()
        
        # Audio fingerprint
        audio_hash = self._generate_audio_hash()
        
        # Fonts (randomize subset)
        num_fonts = random.randint(30, 60)
        available_fonts = random.sample(self.COMMON_FONTS * 3, num_fonts)
        
        # Language & timezone
        languages = random.choice(self.LANGUAGES)
        timezone, timezone_offset = random.choice(self.TIMEZONES)
        
        # Hardware
        hardware_concurrency = random.choice([2, 4, 6, 8, 12, 16])
        device_memory = random.choice([4, 8, 16, 32])
        
        # Plugins (mostly empty for modern browsers)
        plugins = [] if browser_name in ['Chrome', 'Edge'] else [
            {'name': 'PDF Viewer', 'filename': 'internal-pdf-viewer'},
            {'name': 'Chrome PDF Viewer', 'filename': 'internal-pdf-viewer'}
        ]
        
        fingerprint = BrowserFingerprint(
            user_agent=user_agent,
            browser_name=browser_name,
            browser_version=browser_version,
            platform=platform_string,
            platform_version=platform_version,
            screen_width=screen_width,
            screen_height=screen_height,
            screen_color_depth=screen_color_depth,
            screen_pixel_ratio=screen_pixel_ratio,
            webgl_vendor=webgl_vendor,
            webgl_renderer=webgl_renderer,
            webgl_unmasked_vendor=webgl_vendor,
            webgl_unmasked_renderer=webgl_renderer,
            canvas_hash=canvas_hash,
            audio_hash=audio_hash,
            available_fonts=available_fonts,
            plugins=plugins,
            languages=languages,
            timezone=timezone,
            timezone_offset=timezone_offset,
            hardware_concurrency=hardware_concurrency,
            device_memory=device_memory,
            webrtc_enabled=random.choice([True, False]),
            do_not_track=random.choice([None, '1']),
            cookie_enabled=True,
            java_enabled=False
        )
        
        logger.debug(f"Generated fingerprint: {browser_name} on {platform}")
        
        return fingerprint
    
    def _generate_user_agent(
        self,
        browser: str,
        version: str,
        platform: str,
        platform_version: str
    ) -> str:
        """Generate a realistic User-Agent string"""
        
        if browser == 'Chrome':
            if platform == 'Windows':
                return (
                    f'Mozilla/5.0 (Windows NT {platform_version}; Win64; x64) '
                    f'AppleWebKit/537.36 (KHTML, like Gecko) '
                    f'Chrome/{version} Safari/537.36'
                )
            elif platform == 'macOS':
                return (
                    f'Mozilla/5.0 (Macintosh; Intel Mac OS X {platform_version}) '
                    f'AppleWebKit/537.36 (KHTML, like Gecko) '
                    f'Chrome/{version} Safari/537.36'
                )
            else:  # Linux
                return (
                    f'Mozilla/5.0 (X11; Linux x86_64) '
                    f'AppleWebKit/537.36 (KHTML, like Gecko) '
                    f'Chrome/{version} Safari/537.36'
                )
        
        elif browser == 'Firefox':
            if platform == 'Windows':
                return f'Mozilla/5.0 (Windows NT {platform_version}; Win64; x64; rv:{version.split(".")[0]}.0) Gecko/20100101 Firefox/{version}'
            elif platform == 'macOS':
                return f'Mozilla/5.0 (Macintosh; Intel Mac OS X {platform_version}; rv:{version.split(".")[0]}.0) Gecko/20100101 Firefox/{version}'
            else:  # Linux
                return f'Mozilla/5.0 (X11; Linux x86_64; rv:{version.split(".")[0]}.0) Gecko/20100101 Firefox/{version}'
        
        elif browser == 'Edge':
            if platform == 'Windows':
                return (
                    f'Mozilla/5.0 (Windows NT {platform_version}; Win64; x64) '
                    f'AppleWebKit/537.36 (KHTML, like Gecko) '
                    f'Chrome/{version.split(".")[0]}.0.0.0 Safari/537.36 Edg/{version}'
                )
            else:  # macOS
                return (
                    f'Mozilla/5.0 (Macintosh; Intel Mac OS X {platform_version}) '
                    f'AppleWebKit/537.36 (KHTML, like Gecko) '
                    f'Chrome/{version.split(".")[0]}.0.0.0 Safari/537.36 Edg/{version}'
                )
        
        elif browser == 'Safari':
            return (
                f'Mozilla/5.0 (Macintosh; Intel Mac OS X {platform_version}) '
                f'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15'
            )
        
        return 'Mozilla/5.0'
    
    def _generate_webgl_renderer(self, platform: str) -> str:
        """Generate realistic WebGL renderer string"""
        
        if platform == 'Windows':
            gpu_vendors = [
                'ANGLE (NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0)',
                'ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)',
                'ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)',
                'ANGLE (AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0)'
            ]
        elif platform == 'macOS':
            gpu_vendors = [
                'Apple M1',
                'Apple M2',
                'AMD Radeon Pro 5500M',
                'Intel Iris Plus Graphics'
            ]
        else:  # Linux
            gpu_vendors = [
                'Mesa DRI Intel(R) UHD Graphics 630',
                'NV136',
                'AMD RADEON RX 580'
            ]
        
        return random.choice(gpu_vendors)
    
    def _generate_canvas_hash(self) -> str:
        """Generate unique canvas fingerprint hash"""
        # In reality, this would come from actual canvas rendering
        # For now, generate a realistic-looking hash
        random_data = str(random.random()).encode()
        return hashlib.sha256(random_data).hexdigest()[:16]
    
    def _generate_audio_hash(self) -> str:
        """Generate unique audio fingerprint hash"""
        random_data = str(random.random()).encode()
        return hashlib.sha256(random_data).hexdigest()[:16]
    
    def get_playwright_config(self, fingerprint: BrowserFingerprint) -> Dict[str, Any]:
        """
        Get Playwright configuration to apply this fingerprint
        """
        
        return {
            'user_agent': fingerprint.user_agent,
            'viewport': {
                'width': fingerprint.screen_width,
                'height': fingerprint.screen_height
            },
            'device_scale_factor': fingerprint.screen_pixel_ratio,
            'locale': fingerprint.languages[0],
            'timezone_id': fingerprint.timezone,
            'geolocation': None,
            'permissions': [],
            'extra_http_headers': {
                'Accept-Language': ','.join(fingerprint.languages),
                'DNT': fingerprint.do_not_track or '0'
            }
        }
    
    def get_stealth_script(self, fingerprint: BrowserFingerprint) -> str:
        """
        Generate JavaScript to inject into page for additional stealth
        """
        
        fingerprint_data = json.dumps(fingerprint.to_dict())
        
        return f"""
        // Override navigator properties
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {fingerprint.hardware_concurrency}
        }});
        
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {fingerprint.device_memory}
        }});
        
        Object.defineProperty(navigator, 'languages', {{
            get: () => {json.dumps(fingerprint.languages)}
        }});
        
        // Override WebGL
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{fingerprint.webgl_vendor}';
            }}
            if (parameter === 37446) {{
                return '{fingerprint.webgl_renderer}';
            }}
            return getParameter.apply(this, arguments);
        }};
        
        // Timezone
        Date.prototype.getTimezoneOffset = function() {{
            return {fingerprint.timezone_offset};
        }};
        
        console.log('[Stealth] Fingerprint applied');
        """
