"""
Model Retraining Pipeline
Automatically retrains AI models with collected training data
"""

import json
import logging
import pickle
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Automated model retraining pipeline
    
    Features:
    - Load historical training data
    - Retrain pattern learning models
    - Retrain Q-learning models
    - Evaluate improvements
    - Auto-deploy if performance improves
    - Rollback on degradation
    """
    
    def __init__(self, 
                 models_dir: str = 'models',
                 training_data_dir: str = 'training_data'):
        self.models_dir = Path(models_dir)
        self.training_data_dir = Path(training_data_dir)
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Training history
        self.training_history = []
        self.load_training_history()
    
    def load_training_data(self, days: int = 30) -> pd.DataFrame:
        """Load training data from last N days"""
        try:
            all_records = []
            
            for json_file in (self.training_data_dir / 'raw').glob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        records = json.load(f)
                    all_records.extend(records)
                except Exception as e:
                    logger.error(f"Error loading {json_file}: {e}")
            
            if not all_records:
                logger.warning("No training data found")
                return pd.DataFrame()
            
            df = pd.json_normalize(all_records)
            
            # Filter by date
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
                df = df[df['timestamp'] >= cutoff]
            
            logger.info(f"Loaded {len(df)} training records")
            
            return df
        
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return pd.DataFrame()
    
    def train_pattern_learner(self, df: pd.DataFrame) -> Dict:
        """
        Retrain pattern learning model
        
        Returns metrics and updated model
        """
        try:
            logger.info("Training pattern learner...")
            
            # Initialize patterns
            password_patterns = defaultdict(lambda: {'count': 0, 'success': 0, 'total_quality': 0})
            domain_patterns = defaultdict(lambda: {'count': 0, 'success': 0, 'total_quality': 0})
            
            # Learn from data
            for _, row in df.iterrows():
                # Password pattern
                pattern = row.get('pattern', 'unknown')
                success = row.get('valid', False)
                quality = row.get('quality_score', 0)
                
                password_patterns[pattern]['count'] += 1
                if success:
                    password_patterns[pattern]['success'] += 1
                password_patterns[pattern]['total_quality'] += quality
                
                # Domain pattern
                domain = row.get('email_domain', 'unknown')
                domain_patterns[domain]['count'] += 1
                if success:
                    domain_patterns[domain]['success'] += 1
                domain_patterns[domain]['total_quality'] += quality
            
            # Calculate probabilities
            for pattern, stats in password_patterns.items():
                stats['success_rate'] = stats['success'] / stats['count'] if stats['count'] > 0 else 0
                stats['avg_quality'] = stats['total_quality'] / stats['count'] if stats['count'] > 0 else 0
                stats['confidence'] = min(1.0, stats['count'] / 100)  # Confidence increases with samples
            
            for domain, stats in domain_patterns.items():
                stats['success_rate'] = stats['success'] / stats['count'] if stats['count'] > 0 else 0
                stats['avg_quality'] = stats['total_quality'] / stats['count'] if stats['count'] > 0 else 0
                stats['confidence'] = min(1.0, stats['count'] / 100)
            
            # Save model
            model = {
                'password_patterns': dict(password_patterns),
                'domain_patterns': dict(domain_patterns),
                'training_samples': len(df),
                'trained_at': datetime.utcnow().isoformat()
            }
            
            model_path = self.models_dir / 'patterns_new.pkl'
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            logger.info(f"Pattern learner trained on {len(df)} samples")
            
            return {
                'patterns_learned': len(password_patterns) + len(domain_patterns),
                'training_samples': len(df),
                'model_path': str(model_path)
            }
        
        except Exception as e:
            logger.error(f"Error training pattern learner: {e}")
            return {}
    
    def train_q_learner(self, df: pd.DataFrame) -> Dict:
        """
        Retrain Q-learning model
        
        Returns metrics and updated Q-table
        """
        try:
            logger.info("Training Q-learner...")
            
            # Initialize Q-table
            q_table = defaultdict(lambda: defaultdict(float))
            
            # Hyperparameters
            learning_rate = 0.1
            discount_factor = 0.95
            
            # Learn from experiences
            experiences = []
            for _, row in df.iterrows():
                # State: (pattern, domain, predicted_quality_bucket)
                pattern = row.get('pattern', 'unknown')
                domain = row.get('email_domain', 'unknown')
                predicted_quality = row.get('predicted_quality', 0)
                quality_bucket = self._bucket_quality(predicted_quality)
                
                state = (pattern, domain, quality_bucket)
                
                # Action: check or skip
                action = 'check'  # We have data, so it was checked
                
                # Reward based on actual quality
                actual_quality = row.get('quality_score', 0)
                valid = row.get('valid', False)
                
                if valid and actual_quality >= 80:
                    reward = 10  # Excellent hit
                elif valid and actual_quality >= 60:
                    reward = 5   # Good hit
                elif valid:
                    reward = 2   # Acceptable hit
                else:
                    reward = -1  # Waste of time
                
                # Next state (simplified - same state after check)
                next_state = state
                
                experiences.append((state, action, reward, next_state))
            
            # Update Q-table
            for state, action, reward, next_state in experiences:
                # Q-learning update
                current_q = q_table[state][action]
                max_next_q = max(q_table[next_state].values()) if q_table[next_state] else 0
                new_q = current_q + learning_rate * (reward + discount_factor * max_next_q - current_q)
                q_table[state][action] = new_q
            
            # Save Q-table
            q_table_dict = {str(k): dict(v) for k, v in q_table.items()}
            model_path = self.models_dir / 'q_table_new.pkl'
            with open(model_path, 'wb') as f:
                pickle.dump(q_table_dict, f)
            
            logger.info(f"Q-learner trained with {len(experiences)} experiences")
            
            return {
                'states_learned': len(q_table),
                'experiences_processed': len(experiences),
                'model_path': str(model_path)
            }
        
        except Exception as e:
            logger.error(f"Error training Q-learner: {e}")
            return {}
    
    def _bucket_quality(self, quality: int) -> str:
        """Bucket quality scores for Q-learning states"""
        if quality >= 80:
            return 'high'
        elif quality >= 60:
            return 'medium'
        elif quality >= 40:
            return 'low'
        else:
            return 'very_low'
    
    def evaluate_models(self, df: pd.DataFrame) -> Dict:
        """
        Evaluate new models against test data
        
        Returns performance metrics
        """
        try:
            logger.info("Evaluating models...")
            
            # Load new pattern model
            with open(self.models_dir / 'patterns_new.pkl', 'rb') as f:
                pattern_model = pickle.load(f)
            
            # Evaluate on test set (last 20% of data)
            test_size = int(len(df) * 0.2)
            test_df = df.tail(test_size)
            
            correct_predictions = 0
            total_predictions = 0
            quality_errors = []
            
            for _, row in test_df.iterrows():
                pattern = row.get('pattern', 'unknown')
                domain = row.get('email_domain', 'unknown')
                actual_success = row.get('valid', False)
                actual_quality = row.get('quality_score', 0)
                
                # Predict using pattern model
                pattern_stats = pattern_model['password_patterns'].get(pattern, {})
                domain_stats = pattern_model['domain_patterns'].get(domain, {})
                
                predicted_success_rate = (
                    pattern_stats.get('success_rate', 0.5) * 0.6 +
                    domain_stats.get('success_rate', 0.5) * 0.4
                )
                
                predicted_quality = (
                    pattern_stats.get('avg_quality', 50) * 0.6 +
                    domain_stats.get('avg_quality', 50) * 0.4
                )
                
                # Check prediction accuracy
                predicted_success = predicted_success_rate > 0.5
                if predicted_success == actual_success:
                    correct_predictions += 1
                total_predictions += 1
                
                # Quality error
                quality_error = abs(predicted_quality - actual_quality)
                quality_errors.append(quality_error)
            
            accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
            mean_quality_error = np.mean(quality_errors) if quality_errors else 0
            
            metrics = {
                'accuracy': accuracy,
                'mean_quality_error': mean_quality_error,
                'test_samples': test_size,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Model evaluation: accuracy={accuracy:.2%}, quality_error={mean_quality_error:.1f}")
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error evaluating models: {e}")
            return {}
    
    def deploy_models(self, metrics: Dict) -> bool:
        """
        Deploy new models if they improve performance
        
        Returns True if deployed, False if rolled back
        """
        try:
            # Load previous training history
            if self.training_history:
                last_training = self.training_history[-1]
                last_accuracy = last_training.get('metrics', {}).get('accuracy', 0)
                new_accuracy = metrics.get('accuracy', 0)
                
                # Only deploy if accuracy improved
                if new_accuracy <= last_accuracy:
                    logger.warning(f"New model accuracy ({new_accuracy:.2%}) not better than previous ({last_accuracy:.2%}), rolling back")
                    return False
            
            # Deploy new models
            logger.info("Deploying new models...")
            
            # Backup old models
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.models_dir / 'backups' / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            for model_file in ['patterns.pkl', 'q_table.pkl']:
                old_path = self.models_dir / model_file
                if old_path.exists():
                    backup_path = backup_dir / model_file
                    old_path.rename(backup_path)
                    logger.info(f"Backed up {model_file} to {backup_path}")
            
            # Deploy new models
            for model_file in ['patterns_new.pkl', 'q_table_new.pkl']:
                new_path = self.models_dir / model_file
                deployed_path = self.models_dir / model_file.replace('_new', '')
                if new_path.exists():
                    new_path.rename(deployed_path)
                    logger.info(f"Deployed {model_file}")
            
            # Save training history
            training_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics,
                'deployed': True
            }
            self.training_history.append(training_record)
            self.save_training_history()
            
            logger.info("Model deployment successful")
            return True
        
        except Exception as e:
            logger.error(f"Error deploying models: {e}")
            return False
    
    def train_and_deploy(self, days: int = 30) -> Dict:
        """
        Full training pipeline: load data, train, evaluate, deploy
        
        Returns training report
        """
        try:
            logger.info(f"Starting full training pipeline (last {days} days)...")
            
            start_time = datetime.utcnow()
            
            # Step 1: Load training data
            df = self.load_training_data(days)
            if df.empty:
                return {'error': 'No training data available'}
            
            # Step 2: Train pattern learner
            pattern_metrics = self.train_pattern_learner(df)
            
            # Step 3: Train Q-learner
            q_metrics = self.train_q_learner(df)
            
            # Step 4: Evaluate models
            eval_metrics = self.evaluate_models(df)
            
            # Step 5: Deploy if improved
            deployed = self.deploy_models(eval_metrics)
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            report = {
                'training_samples': len(df),
                'pattern_learner': pattern_metrics,
                'q_learner': q_metrics,
                'evaluation': eval_metrics,
                'deployed': deployed,
                'training_time': f"{elapsed:.1f}s",
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Training pipeline complete in {elapsed:.1f}s")
            
            return report
        
        except Exception as e:
            logger.error(f"Error in training pipeline: {e}")
            return {'error': str(e)}
    
    def load_training_history(self):
        """Load training history from disk"""
        history_path = self.models_dir / 'training_history.json'
        if history_path.exists():
            try:
                with open(history_path, 'r') as f:
                    self.training_history = json.load(f)
                logger.info(f"Loaded {len(self.training_history)} training records")
            except Exception as e:
                logger.error(f"Error loading training history: {e}")
                self.training_history = []
    
    def save_training_history(self):
        """Save training history to disk"""
        history_path = self.models_dir / 'training_history.json'
        try:
            with open(history_path, 'w') as f:
                json.dump(self.training_history, f, indent=2)
            logger.info("Training history saved")
        except Exception as e:
            logger.error(f"Error saving training history: {e}")
    
    def get_improvement_trend(self) -> Dict:
        """Calculate model improvement trend"""
        if len(self.training_history) < 2:
            return {'trend': 'insufficient_data'}
        
        accuracies = [t['metrics'].get('accuracy', 0) for t in self.training_history]
        
        # Calculate trend
        recent_avg = np.mean(accuracies[-3:]) if len(accuracies) >= 3 else accuracies[-1]
        older_avg = np.mean(accuracies[-6:-3]) if len(accuracies) >= 6 else accuracies[0]
        
        improvement = recent_avg - older_avg
        
        return {
            'current_accuracy': accuracies[-1],
            'recent_average': recent_avg,
            'older_average': older_avg,
            'improvement': improvement,
            'trend': 'improving' if improvement > 0.01 else 'stable' if improvement > -0.01 else 'declining'
        }


# ==================== USAGE EXAMPLE ====================

def example_usage():
    """Example usage"""
    trainer = ModelTrainer()
    
    # Full training pipeline
    report = trainer.train_and_deploy(days=30)
    print(f"Training report: {json.dumps(report, indent=2)}")
    
    # Get improvement trend
    trend = trainer.get_improvement_trend()
    print(f"Improvement trend: {json.dumps(trend, indent=2)}")


if __name__ == "__main__":
    example_usage()
