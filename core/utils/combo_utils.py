"""
ComboUtils Integration - Email/Combo List Processing
Features from https://comboutils.github.io/ComboUtils/
"""

import re
import asyncio
from typing import List, Dict, Set, Tuple
from pathlib import Path
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ComboUtils:
    """
    Complete combo list utility toolkit
    
    Features:
    - Email extraction
    - Domain sorting
    - Duplicate removal
    - Format validation
    - AI-powered sorting
    - Statistics
    """
    
    def __init__(self, ai_enabled: bool = True):
        self.ai_enabled = ai_enabled
        
        # Email pattern
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        
        # Common combo patterns
        self.combo_patterns = [
            r'(.+):(.+)',  # email:pass
            r'(.+)\|(.+)',  # email|pass
            r'(.+);(.+)',  # email;pass
            r'(.+)\t(.+)',  # email\tpass
            r'(.+) (.+)',  # email pass
        ]
    
    # ==================== EXTRACTION ====================
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract all emails from text"""
        emails = self.email_pattern.findall(text)
        return list(set(emails))  # Remove duplicates
    
    def extract_combos(self, text: str) -> List[Tuple[str, str]]:
        """Extract email:password combos"""
        combos = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Try each pattern
            for pattern in self.combo_patterns:
                match = re.match(pattern, line)
                if match:
                    email, password = match.groups()
                    email = email.strip()
                    password = password.strip()
                    
                    # Validate email
                    if self.email_pattern.match(email):
                        combos.append((email, password))
                    break
        
        return combos
    
    # ==================== VALIDATION ====================
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not self.email_pattern.match(email):
            return False
        
        # Additional checks
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        local, domain = parts
        
        # Check local part
        if not local or len(local) > 64:
            return False
        
        # Check domain
        if not domain or '.' not in domain:
            return False
        
        return True
    
    def validate_combo(self, combo: Tuple[str, str]) -> bool:
        """Validate combo format"""
        email, password = combo
        
        if not self.validate_email(email):
            return False
        
        if not password or len(password) < 1:
            return False
        
        return True
    
    # ==================== SORTING ====================
    
    def sort_by_domain(self, emails: List[str]) -> Dict[str, List[str]]:
        """Sort emails by domain"""
        sorted_emails = defaultdict(list)
        
        for email in emails:
            if '@' in email:
                domain = email.split('@')[1].lower()
                sorted_emails[domain].append(email)
        
        return dict(sorted_emails)
    
    def sort_combos_by_domain(self, combos: List[Tuple[str, str]]) -> Dict[str, List[Tuple[str, str]]]:
        """Sort combos by email domain"""
        sorted_combos = defaultdict(list)
        
        for email, password in combos:
            if '@' in email:
                domain = email.split('@')[1].lower()
                sorted_combos[domain].append((email, password))
        
        return dict(sorted_combos)
    
    def sort_by_provider(self, emails: List[str]) -> Dict[str, List[str]]:
        """Sort by email provider (gmail, yahoo, etc)"""
        providers = {
            'gmail': ['gmail.com', 'googlemail.com'],
            'yahoo': ['yahoo.com', 'yahoo.co.uk', 'ymail.com'],
            'outlook': ['outlook.com', 'hotmail.com', 'live.com', 'msn.com'],
            'icloud': ['icloud.com', 'me.com', 'mac.com'],
            'aol': ['aol.com', 'aim.com'],
            'protonmail': ['protonmail.com', 'protonmail.ch', 'pm.me'],
        }
        
        sorted_emails = defaultdict(list)
        sorted_emails['other'] = []
        
        for email in emails:
            if '@' not in email:
                continue
            
            domain = email.split('@')[1].lower()
            found = False
            
            for provider, domains in providers.items():
                if domain in domains:
                    sorted_emails[provider].append(email)
                    found = True
                    break
            
            if not found:
                sorted_emails['other'].append(email)
        
        return dict(sorted_emails)
    
    # ==================== DEDUPLICATION ====================
    
    def remove_duplicates(self, items: List) -> List:
        """Remove duplicates while preserving order"""
        seen = set()
        result = []
        
        for item in items:
            # Handle tuples (combos)
            if isinstance(item, tuple):
                key = item[0].lower()  # Use email as key
            else:
                key = item.lower()
            
            if key not in seen:
                seen.add(key)
                result.append(item)
        
        return result
    
    def remove_duplicate_emails(self, combos: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Remove combos with duplicate emails, keep first occurrence"""
        seen_emails = set()
        unique_combos = []
        
        for email, password in combos:
            email_lower = email.lower()
            if email_lower not in seen_emails:
                seen_emails.add(email_lower)
                unique_combos.append((email, password))
        
        return unique_combos
    
    # ==================== FILTERING ====================
    
    def filter_by_domain(self, emails: List[str], domains: List[str]) -> List[str]:
        """Filter emails by specific domains"""
        domains_lower = [d.lower() for d in domains]
        
        filtered = []
        for email in emails:
            if '@' in email:
                domain = email.split('@')[1].lower()
                if domain in domains_lower:
                    filtered.append(email)
        
        return filtered
    
    def filter_by_length(self, items: List[str], min_len: int = 0, max_len: int = 999) -> List[str]:
        """Filter by string length"""
        return [item for item in items if min_len <= len(item) <= max_len]
    
    def filter_valid_only(self, emails: List[str]) -> List[str]:
        """Filter to only valid emails"""
        return [email for email in emails if self.validate_email(email)]
    
    # ==================== FORMATTING ====================
    
    def format_combo(self, email: str, password: str, separator: str = ':') -> str:
        """Format combo with specified separator"""
        return f"{email}{separator}{password}"
    
    def convert_format(self, combos: List[Tuple[str, str]], 
                       from_sep: str = ':', to_sep: str = '|') -> List[str]:
        """Convert combo format (e.g., : to |)"""
        return [f"{email}{to_sep}{password}" for email, password in combos]
    
    def normalize_case(self, emails: List[str], case: str = 'lower') -> List[str]:
        """Normalize email case"""
        if case == 'lower':
            return [email.lower() for email in emails]
        elif case == 'upper':
            return [email.upper() for email in emails]
        else:
            return emails
    
    # ==================== STATISTICS ====================
    
    def get_stats(self, combos: List[Tuple[str, str]]) -> Dict:
        """Get comprehensive statistics"""
        if not combos:
            return {}
        
        emails = [email for email, _ in combos]
        domains = [email.split('@')[1] for email in emails if '@' in email]
        
        stats = {
            'total_combos': len(combos),
            'unique_emails': len(set(emails)),
            'unique_domains': len(set(domains)),
            'top_domains': self._get_top_items(domains, 10),
            'avg_password_length': sum(len(pwd) for _, pwd in combos) / len(combos),
            'domain_distribution': self.sort_by_domain(emails),
            'provider_distribution': self.sort_by_provider(emails),
        }
        
        return stats
    
    def _get_top_items(self, items: List[str], limit: int = 10) -> List[Tuple[str, int]]:
        """Get top N most common items"""
        from collections import Counter
        counter = Counter(items)
        return counter.most_common(limit)
    
    # ==================== AI-POWERED FEATURES ====================
    
    async def ai_smart_sort(self, combos: List[Tuple[str, str]], ollama_client) -> Dict[str, List[Tuple[str, str]]]:
        """AI-powered intelligent sorting"""
        if not self.ai_enabled:
            return self.sort_combos_by_domain(combos)
        
        # Get AI suggestions for categorization
        categories = await self._ai_categorize(combos, ollama_client)
        
        return categories
    
    async def _ai_categorize(self, combos: List[Tuple[str, str]], ollama_client) -> Dict:
        """Use AI to categorize combos intelligently"""
        # Sample for AI analysis
        sample = combos[:100]
        
        prompt = f"""
        Analyze these email:password combos and suggest smart categories:
        
        {[f"{e}:{p[:3]}..." for e, p in sample[:10]]}
        
        Suggest categories like:
        - By provider (gmail, yahoo, etc)
        - By domain type (corporate, personal, educational)
        - By security level (weak/strong passwords)
        - By pattern (numeric, alphanumeric, complex)
        
        Return JSON format.
        """
        
        try:
            response = await ollama_client.generate(
                model='mistral',
                prompt=prompt
            )
            
            # Parse AI response and categorize
            # For now, fallback to domain sorting
            return self.sort_combos_by_domain(combos)
        
        except Exception as e:
            logger.error(f"AI categorization failed: {e}")
            return self.sort_combos_by_domain(combos)
    
    # ==================== FILE OPERATIONS ====================
    
    def load_from_file(self, file_path: str) -> List[Tuple[str, str]]:
        """Load combos from file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return self.extract_combos(content)
    
    def save_to_file(self, combos: List[Tuple[str, str]], 
                     file_path: str, separator: str = ':'):
        """Save combos to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            for email, password in combos:
                f.write(f"{email}{separator}{password}\n")
    
    def save_sorted(self, sorted_combos: Dict[str, List[Tuple[str, str]]], 
                    output_dir: str, separator: str = ':'):
        """Save sorted combos to separate files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for category, combos in sorted_combos.items():
            file_path = output_path / f"{category}.txt"
            self.save_to_file(combos, str(file_path), separator)
    
    # ==================== BATCH PROCESSING ====================
    
    async def process_batch(self, input_file: str, output_dir: str, 
                           operations: List[str]) -> Dict:
        """
        Process combo list with multiple operations
        
        Operations:
        - extract: Extract combos from text
        - validate: Remove invalid combos
        - deduplicate: Remove duplicates
        - sort_domain: Sort by domain
        - sort_provider: Sort by provider
        - normalize: Normalize case
        - stats: Generate statistics
        """
        # Load combos
        combos = self.load_from_file(input_file)
        
        results = {
            'input_file': input_file,
            'original_count': len(combos),
            'operations_applied': [],
        }
        
        # Apply operations
        if 'validate' in operations:
            combos = [c for c in combos if self.validate_combo(c)]
            results['operations_applied'].append('validate')
            results['after_validation'] = len(combos)
        
        if 'deduplicate' in operations:
            combos = self.remove_duplicate_emails(combos)
            results['operations_applied'].append('deduplicate')
            results['after_deduplication'] = len(combos)
        
        if 'normalize' in operations:
            combos = [(email.lower(), password) for email, password in combos]
            results['operations_applied'].append('normalize')
        
        # Save results
        if 'sort_domain' in operations:
            sorted_combos = self.sort_combos_by_domain(combos)
            self.save_sorted(sorted_combos, f"{output_dir}/by_domain")
            results['operations_applied'].append('sort_domain')
            results['domains_found'] = len(sorted_combos)
        
        if 'sort_provider' in operations:
            sorted_combos = self.sort_combos_by_domain(combos)  # Simplified
            self.save_sorted(sorted_combos, f"{output_dir}/by_provider")
            results['operations_applied'].append('sort_provider')
        
        # Generate stats
        if 'stats' in operations:
            results['statistics'] = self.get_stats(combos)
        
        results['final_count'] = len(combos)
        
        return results


# ==================== USAGE EXAMPLE ====================

async def main():
    """Example usage"""
    utils = ComboUtils(ai_enabled=True)
    
    # Load combos
    combos = utils.load_from_file('combos.txt')
    print(f"Loaded: {len(combos)} combos")
    
    # Validate
    valid = [c for c in combos if utils.validate_combo(c)]
    print(f"Valid: {len(valid)} combos")
    
    # Remove duplicates
    unique = utils.remove_duplicate_emails(valid)
    print(f"Unique: {len(unique)} combos")
    
    # Sort by domain
    sorted_by_domain = utils.sort_combos_by_domain(unique)
    print(f"Domains: {len(sorted_by_domain)}")
    
    # Save sorted
    utils.save_sorted(sorted_by_domain, 'output/sorted')
    
    # Get stats
    stats = utils.get_stats(unique)
    print(f"Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
