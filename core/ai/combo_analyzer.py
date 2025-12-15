"""
AI-Powered Combo Analyzer using Ollama
Local AI model for intelligent pattern recognition and sorting
"""

import asyncio
import logging
import json
from typing import List, Dict, Tuple
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for local Ollama AI model"""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "mistral"):
        self.host = host
        self.model = model
        self.session = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def generate(self, prompt: str, context: str = None, 
                      temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate AI response"""
        await self._ensure_session()
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if context:
            payload["context"] = context
        
        try:
            async with self.session.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('response', '')
                else:
                    logger.error(f"Ollama API error: {resp.status}")
                    return ""
        
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()


class ComboAnalyzer:
    """
    AI-powered combo list analyzer
    
    Features:
    - Password strength analysis
    - Pattern detection
    - Breach risk prediction
    - Smart categorization
    - Quality scoring
    """
    
    def __init__(self, ollama_host: str = "http://localhost:11434", 
                 ollama_model: str = "mistral"):
        self.ollama = OllamaClient(host=ollama_host, model=ollama_model)
        self.analysis_cache = {}
    
    # ==================== PASSWORD ANALYSIS ====================
    
    async def analyze_password_strength(self, password: str) -> Dict:
        """Analyze password strength using AI"""
        # Quick local analysis
        strength = {
            'length': len(password),
            'has_upper': any(c.isupper() for c in password),
            'has_lower': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(not c.isalnum() for c in password),
        }
        
        # Calculate score
        score = 0
        if strength['length'] >= 8:
            score += 20
        if strength['length'] >= 12:
            score += 10
        if strength['length'] >= 16:
            score += 10
        
        if strength['has_upper']:
            score += 15
        if strength['has_lower']:
            score += 15
        if strength['has_digit']:
            score += 15
        if strength['has_special']:
            score += 15
        
        strength['score'] = min(score, 100)
        strength['level'] = self._score_to_level(score)
        
        return strength
    
    def _score_to_level(self, score: int) -> str:
        """Convert score to level"""
        if score >= 80:
            return "STRONG"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "WEAK"
        else:
            return "VERY_WEAK"
    
    async def detect_patterns(self, passwords: List[str]) -> Dict:
        """Detect common patterns in passwords"""
        patterns = {
            'numeric_only': 0,
            'alphabetic_only': 0,
            'alphanumeric': 0,
            'with_special': 0,
            'common_patterns': [],
        }
        
        for pwd in passwords:
            if pwd.isdigit():
                patterns['numeric_only'] += 1
            elif pwd.isalpha():
                patterns['alphabetic_only'] += 1
            elif pwd.isalnum():
                patterns['alphanumeric'] += 1
            else:
                patterns['with_special'] += 1
        
        # Use AI to detect semantic patterns
        sample = passwords[:50]
        ai_patterns = await self._ai_detect_patterns(sample)
        patterns['common_patterns'] = ai_patterns
        
        return patterns
    
    async def _ai_detect_patterns(self, passwords: List[str]) -> List[str]:
        """Use AI to detect semantic patterns"""
        prompt = f"""
        Analyze these passwords and identify common patterns:
        
        {passwords[:20]}
        
        Look for:
        - Common words (password, admin, user, etc)
        - Dates or years
        - Keyboard patterns (qwerty, 12345, etc)
        - Name + number combinations
        - Sequential patterns
        
        Return a JSON list of detected patterns.
        """
        
        try:
            response = await self.ollama.generate(prompt, temperature=0.3)
            
            # Try to parse JSON from response
            if '[' in response and ']' in response:
                start = response.index('[')
                end = response.rindex(']') + 1
                patterns_json = response[start:end]
                patterns = json.loads(patterns_json)
                return patterns
            else:
                return []
        
        except Exception as e:
            logger.error(f"AI pattern detection failed: {e}")
            return []
    
    # ==================== COMBO ANALYSIS ====================
    
    async def analyze_combo(self, email: str, password: str) -> Dict:
        """Comprehensive combo analysis"""
        analysis = {
            'email': email,
            'timestamp': datetime.utcnow().isoformat(),
            'password_strength': await self.analyze_password_strength(password),
            'breach_risk': await self.predict_breach_risk(email, password),
            'quality_score': 0,
        }
        
        # Calculate quality score
        pwd_score = analysis['password_strength']['score']
        breach_risk = analysis['breach_risk']
        
        quality = (pwd_score * 0.6) + ((100 - breach_risk) * 0.4)
        analysis['quality_score'] = round(quality, 2)
        analysis['quality_level'] = self._score_to_level(quality)
        
        return analysis
    
    async def analyze_batch(self, combos: List[Tuple[str, str]], 
                           max_concurrent: int = 50) -> List[Dict]:
        """Analyze multiple combos concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(email, password):
            async with semaphore:
                return await self.analyze_combo(email, password)
        
        tasks = [
            analyze_with_semaphore(email, password)
            for email, password in combos
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        return valid_results
    
    # ==================== RISK PREDICTION ====================
    
    async def predict_breach_risk(self, email: str, password: str) -> int:
        """Predict breach risk score (0-100)"""
        risk = 0
        
        # Check password strength
        strength = await self.analyze_password_strength(password)
        if strength['score'] < 40:
            risk += 40
        elif strength['score'] < 60:
            risk += 20
        elif strength['score'] < 80:
            risk += 10
        
        # Check for common passwords
        common_passwords = [
            'password', '123456', 'qwerty', 'abc123', 'letmein',
            'admin', 'welcome', 'monkey', 'dragon', 'master'
        ]
        if password.lower() in common_passwords:
            risk += 50
        
        # Check email in password
        email_local = email.split('@')[0].lower()
        if email_local in password.lower():
            risk += 20
        
        # Check for keyboard patterns
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', '123456', '098765']
        if any(pattern in password.lower() for pattern in keyboard_patterns):
            risk += 15
        
        return min(risk, 100)
    
    # ==================== SMART SORTING ====================
    
    async def smart_sort(self, combos: List[Tuple[str, str]]) -> Dict[str, List[Tuple[str, str]]]:
        """AI-powered intelligent sorting"""
        logger.info(f"AI smart sorting {len(combos)} combos...")
        
        # Analyze all combos
        analyses = await self.analyze_batch(combos, max_concurrent=100)
        
        # Create analysis map
        analysis_map = {a['email']: a for a in analyses}
        
        # Sort into categories
        sorted_combos = {
            'high_quality': [],      # Strong passwords, low risk
            'medium_quality': [],    # Medium passwords, medium risk
            'low_quality': [],       # Weak passwords, high risk
            'premium': [],           # Very strong, very low risk
        }
        
        for email, password in combos:
            analysis = analysis_map.get(email)
            if not analysis:
                continue
            
            quality = analysis['quality_score']
            
            if quality >= 80:
                sorted_combos['premium'].append((email, password))
            elif quality >= 60:
                sorted_combos['high_quality'].append((email, password))
            elif quality >= 40:
                sorted_combos['medium_quality'].append((email, password))
            else:
                sorted_combos['low_quality'].append((email, password))
        
        logger.info(f"Sorted: premium={len(sorted_combos['premium'])}, "
                   f"high={len(sorted_combos['high_quality'])}, "
                   f"medium={len(sorted_combos['medium_quality'])}, "
                   f"low={len(sorted_combos['low_quality'])}")
        
        return sorted_combos
    
    async def categorize_by_ai(self, combos: List[Tuple[str, str]]) -> Dict[str, List[Tuple[str, str]]]:
        """Use AI to categorize combos intelligently"""
        # Sample for AI analysis
        sample = combos[:100]
        
        prompt = f"""
        Analyze these email:password combinations and suggest intelligent categories:
        
        Sample combos:
        {[f"{e}:{p[:5]}..." for e, p in sample[:15]]}
        
        Consider:
        - Password strength patterns
        - Email domains (corporate vs personal)
        - Security levels
        - Potential use cases
        - Risk factors
        
        Suggest 5-8 meaningful categories that would help organize these combos.
        Return as JSON list: ["category1", "category2", ...]
        """
        
        try:
            response = await self.ollama.generate(prompt, temperature=0.5)
            
            # Try to extract JSON
            if '[' in response and ']' in response:
                start = response.index('[')
                end = response.rindex(']') + 1
                categories_json = response[start:end]
                categories = json.loads(categories_json)
                
                # Now categorize combos using AI suggestions
                return await self._apply_ai_categories(combos, categories)
            else:
                # Fallback to quality-based sorting
                return await self.smart_sort(combos)
        
        except Exception as e:
            logger.error(f"AI categorization failed: {e}")
            return await self.smart_sort(combos)
    
    async def _apply_ai_categories(self, combos: List[Tuple[str, str]], 
                                   categories: List[str]) -> Dict:
        """Apply AI-suggested categories to combos"""
        # For now, use quality-based sorting
        # This can be enhanced with more sophisticated AI logic
        return await self.smart_sort(combos)
    
    # ==================== RECOMMENDATIONS ====================
    
    async def get_recommendations(self, analysis: Dict) -> List[str]:
        """Get AI-powered recommendations"""
        recommendations = []
        
        pwd_strength = analysis['password_strength']
        breach_risk = analysis['breach_risk']
        
        if pwd_strength['score'] < 60:
            recommendations.append("⚠️ Password is weak - consider changing it")
        
        if breach_risk > 60:
            recommendations.append("🚨 High breach risk detected")
        
        if not pwd_strength['has_special']:
            recommendations.append("Add special characters to password")
        
        if pwd_strength['length'] < 12:
            recommendations.append("Use a longer password (12+ characters)")
        
        # Use AI for additional insights
        ai_recommendation = await self._ai_recommend(analysis)
        if ai_recommendation:
            recommendations.append(f"💡 AI Insight: {ai_recommendation}")
        
        return recommendations
    
    async def _ai_recommend(self, analysis: Dict) -> str:
        """Get AI-powered recommendation"""
        prompt = f"""
        Based on this password analysis:
        - Strength: {analysis['password_strength']['level']}
        - Breach Risk: {analysis['breach_risk']}%
        - Quality: {analysis['quality_score']}
        
        Provide ONE specific, actionable security recommendation in under 15 words.
        """
        
        try:
            response = await self.ollama.generate(prompt, temperature=0.3, max_tokens=50)
            return response.strip()
        except Exception as e:
            logger.error(f"AI recommendation failed: {e}")
            return ""
    
    # ==================== STATISTICS ====================
    
    async def get_comprehensive_stats(self, combos: List[Tuple[str, str]]) -> Dict:
        """Generate comprehensive statistics with AI insights"""
        analyses = await self.analyze_batch(combos[:1000])  # Limit for performance
        
        stats = {
            'total_combos': len(combos),
            'analyzed_combos': len(analyses),
            'password_strength_distribution': {
                'STRONG': 0,
                'MEDIUM': 0,
                'WEAK': 0,
                'VERY_WEAK': 0,
            },
            'quality_distribution': {
                'premium': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
            },
            'average_password_length': 0,
            'average_quality_score': 0,
            'average_breach_risk': 0,
        }
        
        total_length = 0
        total_quality = 0
        total_risk = 0
        
        for analysis in analyses:
            # Strength distribution
            level = analysis['password_strength']['level']
            stats['password_strength_distribution'][level] += 1
            
            # Quality distribution
            quality = analysis['quality_score']
            if quality >= 80:
                stats['quality_distribution']['premium'] += 1
            elif quality >= 60:
                stats['quality_distribution']['high'] += 1
            elif quality >= 40:
                stats['quality_distribution']['medium'] += 1
            else:
                stats['quality_distribution']['low'] += 1
            
            # Averages
            total_length += analysis['password_strength']['length']
            total_quality += quality
            total_risk += analysis['breach_risk']
        
        if analyses:
            stats['average_password_length'] = round(total_length / len(analyses), 2)
            stats['average_quality_score'] = round(total_quality / len(analyses), 2)
            stats['average_breach_risk'] = round(total_risk / len(analyses), 2)
        
        return stats
    
    async def close(self):
        """Close connections"""
        await self.ollama.close()


# ==================== USAGE EXAMPLE ====================

async def main():
    """Example usage"""
    analyzer = ComboAnalyzer(
        ollama_host="http://localhost:11434",
        ollama_model="mistral"
    )
    
    # Analyze single combo
    analysis = await analyzer.analyze_combo("user@example.com", "MyPassword123!")
    print(f"Analysis: {analysis}")
    
    # Get recommendations
    recommendations = await analyzer.get_recommendations(analysis)
    print(f"Recommendations: {recommendations}")
    
    # Analyze batch
    combos = [
        ("user1@gmail.com", "password123"),
        ("user2@yahoo.com", "MySecureP@ssw0rd!"),
        ("user3@outlook.com", "123456"),
    ]
    
    results = await analyzer.analyze_batch(combos)
    print(f"Batch results: {len(results)}")
    
    # Smart sort
    sorted_combos = await analyzer.smart_sort(combos)
    print(f"Sorted categories: {list(sorted_combos.keys())}")
    
    # Stats
    stats = await analyzer.get_comprehensive_stats(combos)
    print(f"Stats: {stats}")
    
    await analyzer.close()


if __name__ == "__main__":
    asyncio.run(main())
