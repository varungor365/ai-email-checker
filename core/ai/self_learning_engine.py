"""
AI Self-Learning Engine with Reinforcement Learning
Continuously improves accuracy and adapts to new patterns
"""

import asyncio
import logging
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pickle
from collections import deque
import aiohttp

logger = logging.getLogger(__name__)


class ExperienceReplay:
    """Store and replay past experiences for learning"""
    
    def __init__(self, max_size: int = 10000):
        self.memory = deque(maxlen=max_size)
    
    def add(self, state: Dict, action: str, reward: float, next_state: Dict, done: bool):
        """Add experience to memory"""
        self.memory.append({
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'done': done,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def sample(self, batch_size: int = 32) -> List[Dict]:
        """Sample random batch from memory"""
        if len(self.memory) < batch_size:
            return list(self.memory)
        
        indices = np.random.choice(len(self.memory), batch_size, replace=False)
        return [self.memory[i] for i in indices]
    
    def save(self, filepath: str):
        """Save memory to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump(list(self.memory), f)
    
    def load(self, filepath: str):
        """Load memory from disk"""
        if Path(filepath).exists():
            with open(filepath, 'rb') as f:
                self.memory = deque(pickle.load(f), maxlen=self.memory.maxlen)


class PatternLearner:
    """Learn patterns from successful/failed attempts"""
    
    def __init__(self):
        self.patterns = {
            'successful_passwords': [],
            'failed_passwords': [],
            'successful_emails': [],
            'breach_patterns': {},
            'quality_indicators': {}
        }
        self.confidence_scores = {}
    
    def learn_from_result(self, email: str, password: str, result: Dict):
        """Learn from a check result"""
        success = result.get('success', False)
        quality_score = result.get('quality_score', 0)
        
        # Learn password patterns
        if success and quality_score > 70:
            self.patterns['successful_passwords'].append(self._extract_password_pattern(password))
        elif not success:
            self.patterns['failed_passwords'].append(self._extract_password_pattern(password))
        
        # Learn email patterns
        if success:
            domain = email.split('@')[1] if '@' in email else ''
            self.patterns['successful_emails'].append(domain)
        
        # Update confidence scores
        pattern_key = f"{self._extract_password_pattern(password)}_{email.split('@')[1] if '@' in email else ''}"
        if pattern_key not in self.confidence_scores:
            self.confidence_scores[pattern_key] = {'successes': 0, 'failures': 0}
        
        if success:
            self.confidence_scores[pattern_key]['successes'] += 1
        else:
            self.confidence_scores[pattern_key]['failures'] += 1
    
    def _extract_password_pattern(self, password: str) -> str:
        """Extract pattern from password"""
        pattern = []
        
        if any(c.isupper() for c in password):
            pattern.append('UPPER')
        if any(c.islower() for c in password):
            pattern.append('LOWER')
        if any(c.isdigit() for c in password):
            pattern.append('DIGIT')
        if any(not c.isalnum() for c in password):
            pattern.append('SPECIAL')
        
        pattern.append(f'LEN_{len(password)//4*4}')  # Group by length ranges
        
        return '_'.join(pattern)
    
    def predict_success_probability(self, email: str, password: str) -> float:
        """Predict probability of success based on learned patterns"""
        pattern_key = f"{self._extract_password_pattern(password)}_{email.split('@')[1] if '@' in email else ''}"
        
        if pattern_key not in self.confidence_scores:
            return 0.5  # Unknown pattern, 50% chance
        
        scores = self.confidence_scores[pattern_key]
        total = scores['successes'] + scores['failures']
        
        if total == 0:
            return 0.5
        
        # Add smoothing to avoid extreme probabilities
        return (scores['successes'] + 1) / (total + 2)
    
    def get_quality_prediction(self, email: str, password: str) -> Dict:
        """Predict quality score before checking"""
        probability = self.predict_success_probability(email, password)
        
        return {
            'success_probability': probability,
            'confidence_level': 'HIGH' if probability > 0.7 or probability < 0.3 else 'MEDIUM' if probability > 0.4 else 'LOW',
            'recommendation': 'CHECK' if probability > 0.3 else 'SKIP'
        }


class ReinforcementLearner:
    """Q-Learning based decision optimizer"""
    
    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.95):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.q_table = {}  # State-action values
        self.epsilon = 0.2  # Exploration rate
    
    def get_state_key(self, state: Dict) -> str:
        """Convert state dict to hashable key"""
        return json.dumps(state, sort_keys=True)
    
    def choose_action(self, state: Dict, possible_actions: List[str]) -> str:
        """Choose action using epsilon-greedy policy"""
        state_key = self.get_state_key(state)
        
        # Exploration: random action
        if np.random.random() < self.epsilon:
            return np.random.choice(possible_actions)
        
        # Exploitation: best known action
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0.0 for action in possible_actions}
        
        q_values = self.q_table[state_key]
        return max(q_values, key=q_values.get)
    
    def update_q_value(self, state: Dict, action: str, reward: float, next_state: Dict, done: bool):
        """Update Q-value using Q-learning algorithm"""
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Initialize Q-values if needed
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        if action not in self.q_table[state_key]:
            self.q_table[state_key][action] = 0.0
        
        # Get current Q-value
        current_q = self.q_table[state_key][action]
        
        # Get max Q-value for next state
        if done or next_state_key not in self.q_table:
            max_next_q = 0.0
        else:
            max_next_q = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0.0
        
        # Q-learning update rule
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state_key][action] = new_q
    
    def decay_epsilon(self, min_epsilon: float = 0.01):
        """Reduce exploration over time"""
        self.epsilon = max(min_epsilon, self.epsilon * 0.995)


class SelfLearningEngine:
    """
    Main AI self-learning engine
    
    Features:
    - Learns from every check result
    - Optimizes decision-making with RL
    - Improves accuracy over time
    - Adapts to new patterns
    - Predicts quality before checking
    """
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.pattern_learner = PatternLearner()
        self.rl_agent = ReinforcementLearner()
        self.experience_replay = ExperienceReplay(max_size=50000)
        
        # Performance metrics
        self.metrics = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'high_quality_hits': 0,
            'false_positives': 0,
            'accuracy': 0.0,
            'precision': 0.0,
            'learning_iterations': 0
        }
        
        # Load previous learning
        self._load_models()
    
    def _load_models(self):
        """Load previously learned models"""
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)
        
        try:
            # Load pattern learner
            pattern_file = models_dir / 'patterns.pkl'
            if pattern_file.exists():
                with open(pattern_file, 'rb') as f:
                    self.pattern_learner = pickle.load(f)
                logger.info("Loaded pattern learner model")
            
            # Load Q-table
            q_table_file = models_dir / 'q_table.pkl'
            if q_table_file.exists():
                with open(q_table_file, 'rb') as f:
                    self.rl_agent.q_table = pickle.load(f)
                logger.info("Loaded Q-learning model")
            
            # Load experience replay
            self.experience_replay.load(str(models_dir / 'experience.pkl'))
            logger.info("Loaded experience replay memory")
        
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def save_models(self):
        """Save learned models"""
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)
        
        try:
            # Save pattern learner
            with open(models_dir / 'patterns.pkl', 'wb') as f:
                pickle.dump(self.pattern_learner, f)
            
            # Save Q-table
            with open(models_dir / 'q_table.pkl', 'wb') as f:
                pickle.dump(self.rl_agent.q_table, f)
            
            # Save experience replay
            self.experience_replay.save(str(models_dir / 'experience.pkl'))
            
            logger.info("Saved all learning models")
        
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    async def predict_quality(self, email: str, password: str) -> Dict:
        """Predict quality before checking"""
        prediction = self.pattern_learner.get_quality_prediction(email, password)
        
        # Get AI insights
        ai_insights = await self._get_ai_insights(email, password)
        prediction['ai_insights'] = ai_insights
        
        return prediction
    
    async def _get_ai_insights(self, email: str, password: str) -> Dict:
        """Get AI model insights"""
        try:
            async with aiohttp.ClientSession() as session:
                prompt = f"""
Analyze this combo for quality:
Email: {email}
Password: {password[:3]}... (length: {len(password)})

Predict:
1. Success probability (0-1)
2. Quality score (0-100)
3. Risk factors

Be concise. Return JSON.
"""
                
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        'model': 'mistral',
                        'prompt': prompt,
                        'stream': False,
                        'options': {'temperature': 0.3, 'num_predict': 150}
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = data.get('response', '')
                        
                        # Try to parse JSON from response
                        try:
                            if '{' in response:
                                start = response.index('{')
                                end = response.rindex('}') + 1
                                return json.loads(response[start:end])
                        except:
                            pass
            
            return {'success_probability': 0.5, 'quality_score': 50}
        
        except Exception as e:
            logger.error(f"AI insights error: {e}")
            return {'success_probability': 0.5, 'quality_score': 50}
    
    async def learn_from_result(self, email: str, password: str, result: Dict, actual_quality: int):
        """Learn from check result"""
        # Update metrics
        self.metrics['total_checks'] += 1
        
        success = result.get('success', False)
        if success:
            self.metrics['successful_checks'] += 1
            if actual_quality >= 70:
                self.metrics['high_quality_hits'] += 1
        else:
            self.metrics['failed_checks'] += 1
        
        # Calculate accuracy
        if self.metrics['total_checks'] > 0:
            self.metrics['accuracy'] = self.metrics['successful_checks'] / self.metrics['total_checks']
        
        if self.metrics['successful_checks'] > 0:
            self.metrics['precision'] = self.metrics['high_quality_hits'] / self.metrics['successful_checks']
        
        # Pattern learning
        self.pattern_learner.learn_from_result(email, password, {
            'success': success,
            'quality_score': actual_quality
        })
        
        # Reinforcement learning
        state = self._create_state(email, password)
        action = 'check' if success else 'skip'
        reward = self._calculate_reward(success, actual_quality)
        next_state = self._create_state(email, password, checked=True)
        
        self.rl_agent.update_q_value(state, action, reward, next_state, done=True)
        
        # Store experience
        self.experience_replay.add(state, action, reward, next_state, done=True)
        
        # Periodic training
        if self.metrics['total_checks'] % 100 == 0:
            await self._train_from_experience()
    
    def _create_state(self, email: str, password: str, checked: bool = False) -> Dict:
        """Create state representation"""
        return {
            'domain': email.split('@')[1] if '@' in email else '',
            'password_length': len(password),
            'has_upper': any(c.isupper() for c in password),
            'has_lower': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(not c.isalnum() for c in password),
            'checked': checked
        }
    
    def _calculate_reward(self, success: bool, quality: int) -> float:
        """Calculate reward for RL"""
        if not success:
            return -1.0  # Penalty for failed check
        
        # Reward based on quality
        if quality >= 90:
            return 10.0  # Excellent hit
        elif quality >= 70:
            return 5.0   # Good hit
        elif quality >= 50:
            return 2.0   # Medium hit
        else:
            return -0.5  # Low quality hit (false positive)
    
    async def _train_from_experience(self):
        """Train from experience replay"""
        batch = self.experience_replay.sample(batch_size=32)
        
        for exp in batch:
            self.rl_agent.update_q_value(
                exp['state'],
                exp['action'],
                exp['reward'],
                exp['next_state'],
                exp['done']
            )
        
        # Decay exploration rate
        self.rl_agent.decay_epsilon()
        
        self.metrics['learning_iterations'] += 1
        
        # Save models periodically
        if self.metrics['learning_iterations'] % 10 == 0:
            self.save_models()
            logger.info(f"Models saved after {self.metrics['learning_iterations']} iterations")
    
    async def should_check(self, email: str, password: str) -> Tuple[bool, Dict]:
        """Decide if combo should be checked (intelligent filtering)"""
        prediction = await self.predict_quality(email, password)
        
        # Use RL agent to make decision
        state = self._create_state(email, password)
        possible_actions = ['check', 'skip']
        action = self.rl_agent.choose_action(state, possible_actions)
        
        should_check = action == 'check' or prediction['success_probability'] > 0.3
        
        return should_check, {
            'prediction': prediction,
            'rl_decision': action,
            'confidence': prediction['confidence_level']
        }
    
    def get_metrics(self) -> Dict:
        """Get current learning metrics"""
        return {
            **self.metrics,
            'exploration_rate': self.rl_agent.epsilon,
            'patterns_learned': len(self.pattern_learner.confidence_scores),
            'experience_size': len(self.experience_replay.memory),
            'q_table_size': len(self.rl_agent.q_table)
        }
    
    async def optimize_system(self) -> Dict:
        """Get optimization recommendations"""
        metrics = self.get_metrics()
        
        recommendations = []
        
        # Check accuracy
        if metrics['accuracy'] < 0.5:
            recommendations.append("Low accuracy - increase learning iterations")
        
        # Check precision
        if metrics['precision'] < 0.7:
            recommendations.append("Low precision - adjust quality threshold")
        
        # Check exploration
        if metrics['exploration_rate'] > 0.1 and metrics['total_checks'] > 1000:
            recommendations.append("Reduce exploration rate - enough data collected")
        
        # Check experience replay
        if metrics['experience_size'] < 1000:
            recommendations.append("Collect more training data")
        
        return {
            'current_performance': metrics,
            'recommendations': recommendations,
            'optimal_settings': self._get_optimal_settings()
        }
    
    def _get_optimal_settings(self) -> Dict:
        """Calculate optimal system settings based on learning"""
        return {
            'worker_count': min(10, max(2, int(self.metrics['accuracy'] * 15))),
            'concurrent_limit': min(100, max(20, int(self.metrics['precision'] * 150))),
            'quality_threshold': max(60, int(self.metrics['precision'] * 100)),
            'skip_low_probability': self.metrics['accuracy'] > 0.6
        }


# ==================== USAGE EXAMPLE ====================

async def main():
    """Example usage"""
    engine = SelfLearningEngine()
    
    # Predict quality before checking
    email = "user@example.com"
    password = "password123"
    
    should_check, decision_info = await engine.should_check(email, password)
    print(f"Should check: {should_check}")
    print(f"Decision info: {decision_info}")
    
    # Simulate check result
    result = {'success': True}
    actual_quality = 85
    
    # Learn from result
    await engine.learn_from_result(email, password, result, actual_quality)
    
    # Get metrics
    metrics = engine.get_metrics()
    print(f"Metrics: {metrics}")
    
    # Get optimization recommendations
    optimization = await engine.optimize_system()
    print(f"Optimization: {optimization}")


if __name__ == "__main__":
    asyncio.run(main())
