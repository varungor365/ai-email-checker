"""
Training Data Collection System
Automatically collects and labels all check results for continuous model improvement
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from collections import defaultdict

logger = logging.getLogger(__name__)


class TrainingDataCollector:
    """
    Collects and manages training data from check results
    
    Features:
    - Automatic labeling based on quality validation
    - Structured storage (JSON, CSV, Parquet)
    - Feature extraction for ML
    - Dataset versioning
    - Export for model training
    """
    
    def __init__(self, storage_dir: str = 'training_data'):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.storage_dir / 'raw').mkdir(exist_ok=True)
        (self.storage_dir / 'processed').mkdir(exist_ok=True)
        (self.storage_dir / 'exports').mkdir(exist_ok=True)
        
        # In-memory buffer
        self.buffer = {
            'excellent': [],
            'very_good': [],
            'good': [],
            'acceptable': [],
            'questionable': [],
            'poor': [],
            'rejected': []
        }
        
        self.buffer_size = 1000  # Flush to disk after 1000 records
        self.stats = defaultdict(int)
    
    def collect(self, email: str, password: str, result: Dict, validation: Dict):
        """
        Collect single check result with automatic labeling
        
        Args:
            email: Email address
            password: Password (will be hashed/masked)
            result: Check result with all data
            validation: Validation result with confidence and quality grade
        """
        try:
            # Extract features
            features = self._extract_features(email, password, result, validation)
            
            # Label by quality grade
            quality_grade = validation.get('quality_grade', 'POOR')
            label = quality_grade.lower()
            
            # Add to buffer
            self.buffer[label].append(features)
            self.stats[f'{label}_collected'] += 1
            self.stats['total_collected'] += 1
            
            # Check if buffer needs flushing
            total_in_buffer = sum(len(v) for v in self.buffer.values())
            if total_in_buffer >= self.buffer_size:
                self.flush()
            
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
    
    def _extract_features(self, email: str, password: str, result: Dict, validation: Dict) -> Dict:
        """Extract ML features from check result"""
        
        # Email features
        email_parts = email.split('@')
        email_username = email_parts[0] if len(email_parts) > 0 else ''
        email_domain = email_parts[1] if len(email_parts) > 1 else ''
        
        # Password features
        password_features = {
            'length': len(password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digits': any(c.isdigit() for c in password),
            'has_special': any(not c.isalnum() for c in password),
            'is_common': password.lower() in ['password', '123456', 'qwerty', '12345678'],
            'pattern': self._detect_password_pattern(password)
        }
        
        # Result features
        result_features = {
            'sources_found': result.get('sources_found', 0),
            'total_breaches': result.get('total_breaches', 0),
            'leak_score': result.get('leak_score', 0),
            'quality_score': result.get('quality_score', 0),
            'first_seen': result.get('first_seen'),
            'last_seen': result.get('last_seen')
        }
        
        # Validation features
        validation_features = {
            'valid': validation.get('valid', False),
            'confidence': validation.get('confidence', 0.0),
            'quality_grade': validation.get('quality_grade', 'POOR'),
            'format_valid': validation.get('layer_results', {}).get('format', {}).get('valid', False),
            'consistency_valid': validation.get('layer_results', {}).get('consistency', {}).get('valid', False),
            'source_credible': validation.get('layer_results', {}).get('source', {}).get('valid', False),
            'cross_referenced': validation.get('layer_results', {}).get('cross_reference', {}).get('valid', False),
            'historically_consistent': validation.get('layer_results', {}).get('historical', {}).get('valid', False),
            'ai_validated': validation.get('layer_results', {}).get('ai', {}).get('valid', False)
        }
        
        # AI prediction features (if available)
        ai_prediction = result.get('ai_prediction', {})
        prediction_features = {
            'predicted_success_prob': ai_prediction.get('success_probability', 0.0),
            'predicted_quality': ai_prediction.get('predicted_quality', 0),
            'predicted_confidence': ai_prediction.get('confidence', 0.0)
        }
        
        # Combine all features
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'email': email,
            'email_username_length': len(email_username),
            'email_domain': email_domain,
            'password_hash': hash(password),  # Store hash only
            **password_features,
            **result_features,
            **validation_features,
            **prediction_features,
            'metadata': {
                'sources': result.get('sources', []),
                'breaches': result.get('breaches', [])[:5],  # Top 5 only
                'validation_issues': validation.get('issues', [])
            }
        }
    
    def _detect_password_pattern(self, password: str) -> str:
        """Detect common password patterns"""
        if password.isdigit():
            return 'numeric_only'
        elif password.isalpha():
            return 'alpha_only'
        elif password.isalnum():
            return 'alphanumeric'
        elif len(password) < 6:
            return 'too_short'
        elif any(word in password.lower() for word in ['password', 'pass', 'admin', '123']):
            return 'common_words'
        else:
            return 'complex'
    
    def flush(self):
        """Flush buffer to disk"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
            for label, data in self.buffer.items():
                if not data:
                    continue
                
                # Save as JSON
                filename = f"{label}_{timestamp}.json"
                filepath = self.storage_dir / 'raw' / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Flushed {len(data)} {label} records to {filepath}")
            
            # Clear buffer
            for label in self.buffer:
                self.buffer[label] = []
            
            self.stats['flushes'] += 1
            
        except Exception as e:
            logger.error(f"Error flushing buffer: {e}")
    
    def export_dataset(self, 
                      days: int = 7,
                      min_quality: str = 'acceptable',
                      format: str = 'csv') -> Path:
        """
        Export training dataset
        
        Args:
            days: Number of days to include
            min_quality: Minimum quality grade to include
            format: 'csv', 'json', or 'parquet'
        
        Returns:
            Path to exported file
        """
        try:
            # Flush current buffer
            self.flush()
            
            # Collect all records from last N days
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            all_records = []
            
            for json_file in (self.storage_dir / 'raw').glob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        records = json.load(f)
                    
                    for record in records:
                        record_date = datetime.fromisoformat(record['timestamp'])
                        if record_date >= cutoff_date:
                            all_records.append(record)
                
                except Exception as e:
                    logger.error(f"Error reading {json_file}: {e}")
            
            # Filter by quality
            quality_order = ['poor', 'questionable', 'acceptable', 'good', 'very_good', 'excellent']
            min_quality_index = quality_order.index(min_quality.lower())
            
            filtered_records = [
                r for r in all_records
                if quality_order.index(r.get('quality_grade', 'POOR').lower()) >= min_quality_index
            ]
            
            # Convert to DataFrame
            df = pd.json_normalize(filtered_records)
            
            # Drop sensitive columns
            if 'email' in df.columns:
                df = df.drop('email', axis=1)
            if 'password_hash' in df.columns:
                # Keep hash for pattern learning
                pass
            
            # Export
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            export_dir = self.storage_dir / 'exports'
            
            if format == 'csv':
                filename = f"training_data_{timestamp}.csv"
                filepath = export_dir / filename
                df.to_csv(filepath, index=False)
            
            elif format == 'json':
                filename = f"training_data_{timestamp}.json"
                filepath = export_dir / filename
                df.to_json(filepath, orient='records', indent=2)
            
            elif format == 'parquet':
                filename = f"training_data_{timestamp}.parquet"
                filepath = export_dir / filename
                df.to_parquet(filepath, index=False)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Exported {len(filtered_records)} records to {filepath}")
            
            return filepath
        
        except Exception as e:
            logger.error(f"Error exporting dataset: {e}")
            raise
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return dict(self.stats)
    
    def get_quality_distribution(self) -> Dict:
        """Get quality grade distribution"""
        distribution = {}
        
        for label, data in self.buffer.items():
            distribution[label] = len(data)
        
        # Add from disk
        for json_file in (self.storage_dir / 'raw').glob('*.json'):
            label = json_file.stem.split('_')[0]
            try:
                with open(json_file, 'r') as f:
                    records = json.load(f)
                distribution[label] = distribution.get(label, 0) + len(records)
            except:
                pass
        
        return distribution


# ==================== USAGE EXAMPLE ====================

def example_usage():
    """Example usage"""
    collector = TrainingDataCollector()
    
    # Collect some results
    for i in range(100):
        email = f"user{i}@example.com"
        password = f"pass{i}"
        
        result = {
            'sources_found': 3,
            'total_breaches': 5,
            'leak_score': 75,
            'quality_score': 80,
            'sources': ['haveibeenpwned', 'emailrep'],
            'breaches': ['Adobe', 'LinkedIn']
        }
        
        validation = {
            'valid': True,
            'confidence': 0.85,
            'quality_grade': 'VERY_GOOD',
            'layer_results': {}
        }
        
        collector.collect(email, password, result, validation)
    
    # Export dataset
    export_path = collector.export_dataset(days=7, min_quality='good', format='csv')
    print(f"Dataset exported to: {export_path}")
    
    # Get stats
    stats = collector.get_stats()
    print(f"Collection stats: {stats}")
    
    distribution = collector.get_quality_distribution()
    print(f"Quality distribution: {distribution}")


if __name__ == "__main__":
    example_usage()
