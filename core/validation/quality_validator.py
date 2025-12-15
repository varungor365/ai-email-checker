"""
Quality Validation System
Multi-layer validation to ensure only high-quality, correct hits
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import aiohttp
import re

logger = logging.getLogger(__name__)


class ValidationLayer:
    """Base validation layer"""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
    
    async def validate(self, result: Dict) -> Tuple[bool, float, str]:
        """
        Validate result
        Returns: (is_valid, confidence_score, reason)
        """
        raise NotImplementedError


class FormatValidator(ValidationLayer):
    """Validate result format and structure"""
    
    def __init__(self):
        super().__init__("FormatValidator", weight=0.5)
    
    async def validate(self, result: Dict) -> Tuple[bool, float, str]:
        """Check if result has valid format"""
        required_fields = ['email', 'success', 'timestamp']
        
        # Check required fields
        for field in required_fields:
            if field not in result:
                return False, 0.0, f"Missing required field: {field}"
        
        # Validate email format
        email = result.get('email', '')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, 0.0, "Invalid email format"
        
        # Check timestamp
        try:
            datetime.fromisoformat(result.get('timestamp', ''))
        except:
            return False, 0.0, "Invalid timestamp"
        
        return True, 1.0, "Format valid"


class ConsistencyValidator(ValidationLayer):
    """Validate result consistency"""
    
    def __init__(self):
        super().__init__("ConsistencyValidator", weight=0.8)
    
    async def validate(self, result: Dict) -> Tuple[bool, float, str]:
        """Check if result is internally consistent"""
        success = result.get('success', False)
        quality_score = result.get('quality_score', 0)
        
        # If success=True but quality_score=0, suspicious
        if success and quality_score == 0:
            return False, 0.3, "Success flag inconsistent with quality score"
        
        # If success=False but quality_score>50, suspicious
        if not success and quality_score > 50:
            return False, 0.4, "Quality score inconsistent with failure"
        
        # Check for impossible values
        if quality_score < 0 or quality_score > 100:
            return False, 0.0, "Quality score out of range"
        
        # Check breach data consistency
        breaches = result.get('breaches', [])
        sources_found = result.get('sources_found', 0)
        
        if len(breaches) > sources_found:
            return False, 0.5, "More breaches than sources found"
        
        return True, 1.0, "Result consistent"


class SourceValidator(ValidationLayer):
    """Validate source credibility"""
    
    def __init__(self):
        super().__init__("SourceValidator", weight=1.0)
        self.trusted_sources = {
            'hibp': 1.0,
            'firefox_monitor': 0.95,
            'emailrep': 0.9,
            'cybernews': 0.9,
            'breach_directory': 0.85,
            'intelx': 0.95,
            'ghostproject': 0.8
        }
    
    async def validate(self, result: Dict) -> Tuple[bool, float, str]:
        """Validate based on source credibility"""
        sources = result.get('sources', [])
        
        if not sources:
            return False, 0.0, "No sources provided"
        
        # Calculate weighted credibility
        total_weight = 0.0
        total_credibility = 0.0
        
        for source in sources:
            source_name = source.get('name', '').lower()
            credibility = self.trusted_sources.get(source_name, 0.5)
            
            total_weight += 1.0
            total_credibility += credibility
        
        avg_credibility = total_credibility / total_weight if total_weight > 0 else 0.0
        
        if avg_credibility < 0.5:
            return False, avg_credibility, "Low source credibility"
        
        return True, avg_credibility, f"Source credibility: {avg_credibility:.2f}"


class CrossReferenceValidator(ValidationLayer):
    """Cross-reference with multiple sources"""
    
    def __init__(self):
        super().__init__("CrossReferenceValidator", weight=1.2)
    
    async def validate(self, result: Dict) -> Tuple[bool, float, str]:
        """Validate by cross-referencing sources"""
        sources = result.get('sources', [])
        
        if len(sources) < 2:
            return True, 0.6, "Single source - cannot cross-reference"
        
        # Check if multiple sources agree
        agreements = 0
        for i, source1 in enumerate(sources):
            for source2 in sources[i+1:]:
                if self._sources_agree(source1, source2):
                    agreements += 1
        
        max_agreements = (len(sources) * (len(sources) - 1)) // 2
        agreement_ratio = agreements / max_agreements if max_agreements > 0 else 0.0
        
        if agreement_ratio < 0.3:
            return False, agreement_ratio, "Sources disagree significantly"
        
        confidence = 0.6 + (agreement_ratio * 0.4)
        return True, confidence, f"Cross-reference confidence: {confidence:.2f}"
    
    def _sources_agree(self, source1: Dict, source2: Dict) -> bool:
        """Check if two sources agree"""
        # Both found or both not found
        found1 = source1.get('found', False)
        found2 = source2.get('found', False)
        
        return found1 == found2


class HistoricalValidator(ValidationLayer):
    """Validate against historical data"""
    
    def __init__(self):
        super().__init__("HistoricalValidator", weight=0.7)
        self.history = {}  # email -> [results]
    
    async def validate(self, result: Dict) -> Tuple[bool, float, str]:
        """Validate against past results for same email"""
        email = result.get('email', '')
        
        if email not in self.history:
            self.history[email] = []
            return True, 0.8, "No historical data"
        
        past_results = self.history[email]
        
        # Check consistency with past results
        current_success = result.get('success', False)
        past_successes = [r.get('success', False) for r in past_results[-5:]]
        
        if len(past_successes) >= 3:
            majority_success = sum(past_successes) > len(past_successes) / 2
            
            if current_success != majority_success:
                return False, 0.4, "Inconsistent with historical data"
        
        # Add to history
        self.history[email].append(result)
        
        return True, 0.9, "Consistent with history"


class AIValidator(ValidationLayer):
    """AI-powered validation"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        super().__init__("AIValidator", weight=1.5)
        self.ollama_host = ollama_host
    
    async def validate(self, result: Dict) -> Tuple[bool, float, str]:
        """Use AI to validate result quality"""
        try:
            async with aiohttp.ClientSession() as session:
                prompt = f"""
Validate this email check result:

Email: {result.get('email', 'N/A')}
Success: {result.get('success', False)}
Quality Score: {result.get('quality_score', 0)}
Sources Found: {result.get('sources_found', 0)}/{result.get('total_sources', 0)}
Breaches: {len(result.get('breaches', []))}

Analyze if this result is:
1. Legitimate (not false positive)
2. High quality
3. Trustworthy

Return JSON: {{"valid": true/false, "confidence": 0.0-1.0, "reason": "..."}}
Be strict. Only validate high-quality results.
"""
                
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        'model': 'mistral',
                        'prompt': prompt,
                        'stream': False,
                        'options': {'temperature': 0.2, 'num_predict': 100}
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = data.get('response', '')
                        
                        # Parse JSON response
                        try:
                            if '{' in response:
                                start = response.index('{')
                                end = response.rindex('}') + 1
                                import json
                                ai_result = json.loads(response[start:end])
                                
                                return (
                                    ai_result.get('valid', True),
                                    ai_result.get('confidence', 0.7),
                                    ai_result.get('reason', 'AI validation')
                                )
                        except:
                            pass
            
            return True, 0.7, "AI validation inconclusive"
        
        except Exception as e:
            logger.error(f"AI validation error: {e}")
            return True, 0.6, "AI validation unavailable"


class QualityValidator:
    """
    Multi-layer quality validation system
    
    Layers:
    1. Format validation
    2. Consistency checks
    3. Source credibility
    4. Cross-reference verification
    5. Historical validation
    6. AI-powered validation
    """
    
    def __init__(self, ollama_host: str = "http://localhost:11434", min_confidence: float = 0.7):
        self.min_confidence = min_confidence
        
        # Initialize validation layers
        self.layers = [
            FormatValidator(),
            ConsistencyValidator(),
            SourceValidator(),
            CrossReferenceValidator(),
            HistoricalValidator(),
            AIValidator(ollama_host)
        ]
        
        # Statistics
        self.stats = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'by_layer': {layer.name: {'passed': 0, 'failed': 0} for layer in self.layers}
        }
    
    async def validate(self, result: Dict) -> Dict:
        """
        Validate result through all layers
        
        Returns:
        {
            'valid': bool,
            'confidence': float,
            'quality_grade': str,
            'layer_results': [...],
            'issues': [...]
        }
        """
        self.stats['total_validations'] += 1
        
        layer_results = []
        issues = []
        total_weight = 0.0
        weighted_confidence = 0.0
        
        # Run through all validation layers
        for layer in self.layers:
            is_valid, confidence, reason = await layer.validate(result)
            
            layer_result = {
                'layer': layer.name,
                'valid': is_valid,
                'confidence': confidence,
                'reason': reason,
                'weight': layer.weight
            }
            layer_results.append(layer_result)
            
            # Update statistics
            if is_valid:
                self.stats['by_layer'][layer.name]['passed'] += 1
            else:
                self.stats['by_layer'][layer.name]['failed'] += 1
                issues.append(f"{layer.name}: {reason}")
            
            # Calculate weighted confidence
            total_weight += layer.weight
            weighted_confidence += confidence * layer.weight
        
        # Calculate overall confidence
        overall_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.0
        
        # Determine if result is valid
        is_valid = overall_confidence >= self.min_confidence and len(issues) <= 1
        
        # Determine quality grade
        quality_grade = self._get_quality_grade(overall_confidence)
        
        # Update statistics
        if is_valid:
            self.stats['passed_validations'] += 1
        else:
            self.stats['failed_validations'] += 1
        
        return {
            'valid': is_valid,
            'confidence': overall_confidence,
            'quality_grade': quality_grade,
            'layer_results': layer_results,
            'issues': issues,
            'recommendation': self._get_recommendation(is_valid, overall_confidence, issues)
        }
    
    def _get_quality_grade(self, confidence: float) -> str:
        """Convert confidence to quality grade"""
        if confidence >= 0.95:
            return 'EXCELLENT'
        elif confidence >= 0.85:
            return 'VERY_GOOD'
        elif confidence >= 0.75:
            return 'GOOD'
        elif confidence >= 0.65:
            return 'ACCEPTABLE'
        elif confidence >= 0.50:
            return 'QUESTIONABLE'
        else:
            return 'POOR'
    
    def _get_recommendation(self, is_valid: bool, confidence: float, issues: List[str]) -> str:
        """Get recommendation based on validation"""
        if not is_valid:
            return f"REJECT - Confidence too low ({confidence:.2f})"
        
        if confidence >= 0.9:
            return "ACCEPT - High confidence result"
        elif confidence >= 0.75:
            return "ACCEPT - Good quality result"
        elif len(issues) > 0:
            return f"REVIEW - Minor issues: {', '.join(issues[:2])}"
        else:
            return "ACCEPT - Meets minimum threshold"
    
    async def batch_validate(self, results: List[Dict], max_concurrent: int = 20) -> List[Dict]:
        """Validate multiple results concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def validate_with_semaphore(result):
            async with semaphore:
                validation = await self.validate(result)
                return {**result, 'validation': validation}
        
        tasks = [validate_with_semaphore(result) for result in results]
        validated_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        return [r for r in validated_results if not isinstance(r, Exception)]
    
    def get_stats(self) -> Dict:
        """Get validation statistics"""
        return {
            **self.stats,
            'pass_rate': self.stats['passed_validations'] / self.stats['total_validations'] if self.stats['total_validations'] > 0 else 0.0
        }
    
    def get_high_quality_only(self, results: List[Dict]) -> List[Dict]:
        """Filter to only high-quality validated results"""
        return [
            r for r in results
            if r.get('validation', {}).get('valid', False)
            and r.get('validation', {}).get('confidence', 0) >= 0.8
        ]


# ==================== USAGE EXAMPLE ====================

async def main():
    """Example usage"""
    validator = QualityValidator(min_confidence=0.7)
    
    # Example result to validate
    result = {
        'email': 'test@example.com',
        'success': True,
        'quality_score': 85,
        'sources_found': 12,
        'total_sources': 30,
        'breaches': [
            {'name': 'LinkedIn', 'date': '2012-05-05'},
            {'name': 'Adobe', 'date': '2013-10-04'}
        ],
        'sources': [
            {'name': 'hibp', 'found': True},
            {'name': 'emailrep', 'found': True}
        ],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Validate
    validation = await validator.validate(result)
    
    print(f"Valid: {validation['valid']}")
    print(f"Confidence: {validation['confidence']:.2f}")
    print(f"Quality Grade: {validation['quality_grade']}")
    print(f"Recommendation: {validation['recommendation']}")
    
    if validation['issues']:
        print(f"Issues: {validation['issues']}")
    
    # Get stats
    stats = validator.get_stats()
    print(f"\nValidation Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
