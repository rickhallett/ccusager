"""Data source integration for bunx ccusage"""

import json
import subprocess
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class CCUsageDataSource:
    """Handles integration with bunx ccusage"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.last_fetch: float = 0
        self.fetch_interval: float = 5.0  # Minimum seconds between fetches
        self.mock_mode: bool = False  # For testing without bunx
        self.metric_history: Dict[str, List[float]] = {
            'cost': [],
            'tokens': [],
            'burn_rate': [],
            'efficiency': [],
            'context_util': []
        }
        self.history_size = 50  # Keep last 50 data points for each metric
    
    def fetch_current_data(self) -> Dict[str, Any]:
        """Get latest usage data from bunx ccusage"""
        current_time = time.time()
        
        # Check if we should use cached data
        if current_time - self.last_fetch < self.fetch_interval:
            return self.cache.get('last_valid', self._get_mock_data())
        
        try:
            # Try to fetch real data
            if not self.mock_mode:
                result = subprocess.run(
                    ["bunx", "ccusage", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    self._update_cache(data)
                    self.last_fetch = current_time
                    return self._process_data(data)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            # Fall back to mock data for Phase 1 testing
            self.mock_mode = True
        
        # Use mock data if real data unavailable
        mock_data = self._get_mock_data()
        self._update_cache(mock_data)
        self.last_fetch = current_time
        return self._process_data(mock_data)
    
    def get_trend_data(self, metric: str, period: str = "daily") -> List[float]:
        """Get trend data for a specific metric"""
        trends = self.cache.get('trends', [])
        
        if not trends:
            return []
        
        # Filter by period
        now = time.time()
        if period == "daily":
            cutoff = now - (24 * 60 * 60)
        elif period == "weekly":
            cutoff = now - (7 * 24 * 60 * 60)
        elif period == "monthly":
            cutoff = now - (30 * 24 * 60 * 60)
        else:
            cutoff = 0
        
        filtered_trends = [
            t for t in trends 
            if t.get('timestamp', 0) > cutoff
        ]
        
        # Extract metric values
        if metric == "cost":
            return [t.get('cost', 0) for t in filtered_trends]
        elif metric == "tokens":
            return [t.get('tokens', 0) for t in filtered_trends]
        else:
            return []
    
    def calculate_burn_rate(self) -> float:
        """Calculate current burn rate in dollars per hour"""
        trends = self.cache.get('trends', [])
        
        if len(trends) < 2:
            return 0.0
        
        # Get last hour of data
        now = time.time()
        hour_ago = now - 3600
        
        recent_trends = [
            t for t in trends 
            if t.get('timestamp', 0) > hour_ago
        ]
        
        if len(recent_trends) < 2:
            return 0.0
        
        # Calculate rate
        first = recent_trends[0]
        last = recent_trends[-1]
        
        cost_diff = last.get('cost', 0) - first.get('cost', 0)
        time_diff = (last.get('timestamp', 0) - first.get('timestamp', 0)) / 3600
        
        if time_diff > 0:
            return cost_diff / time_diff
        
        return 0.0
    
    def get_model_distribution(self) -> Dict[str, float]:
        """Get distribution of usage across different models"""
        model_usage = self.cache.get('model_usage', {})
        
        total = sum(model_usage.values())
        if total == 0:
            return {}
        
        return {
            model: (count / total) * 100
            for model, count in model_usage.items()
        }
    
    def get_context_utilization(self) -> float:
        """Get current context window utilization percentage"""
        current_tokens = self.cache.get('current_session_tokens', 0)
        max_context = self.cache.get('max_context_window', 200000)
        
        if max_context > 0:
            return (current_tokens / max_context) * 100
        
        return 0.0
    
    def _update_cache(self, data: Dict[str, Any]):
        """Update local cache with new data"""
        current_time = time.time()
        
        # Store last valid data
        self.cache['last_valid'] = data
        self.cache['timestamp'] = current_time
        
        # Update model usage statistics
        if 'model' in data:
            if 'model_usage' not in self.cache:
                self.cache['model_usage'] = {}
            
            model = data['model']
            self.cache['model_usage'][model] = \
                self.cache['model_usage'].get(model, 0) + 1
        
        # Maintain trend history
        if 'trends' not in self.cache:
            self.cache['trends'] = []
        
        self.cache['trends'].append({
            'timestamp': current_time,
            'cost': data.get('total_cost', 0),
            'tokens': data.get('total_tokens', 0)
        })
        
        # Keep only last 1000 data points for trends
        self.cache['trends'] = self.cache['trends'][-1000:]
        
        # Update metric history for sparklines
        self._update_metric_history('cost', data.get('total_cost', 0))
        self._update_metric_history('tokens', data.get('total_tokens', 0))
        self._update_metric_history('burn_rate', self.calculate_burn_rate())
        self._update_metric_history('context_util', self.get_context_utilization())
        
        # Calculate and store efficiency score
        efficiency = self._calculate_efficiency_score(data)
        self._update_metric_history('efficiency', efficiency)
        
        # Update session data
        if 'session' in data:
            self.cache['current_session_tokens'] = \
                data['session'].get('tokens', 0)
    
    def _process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw data into dashboard-ready format"""
        processed = {
            'total_cost': raw_data.get('total_cost', 0),
            'total_tokens': raw_data.get('total_tokens', 0),
            'burn_rate': self.calculate_burn_rate(),
            'model_distribution': self.get_model_distribution(),
            'context_utilization': self.get_context_utilization(),
            'trend_data': self.get_trend_data('cost', 'daily')[-20:],  # Last 20 points
        }
        
        # Calculate trends
        if len(self.cache.get('trends', [])) > 1:
            prev = self.cache['trends'][-2]
            curr = self.cache['trends'][-1]
            
            cost_change = curr['cost'] - prev['cost']
            token_change = curr['tokens'] - prev['tokens']
            
            if prev['cost'] > 0:
                processed['cost_trend'] = (cost_change / prev['cost']) * 100
            else:
                processed['cost_trend'] = 0
            
            if prev['tokens'] > 0:
                processed['token_trend'] = (token_change / prev['tokens']) * 100
            else:
                processed['token_trend'] = 0
        else:
            processed['cost_trend'] = 0
            processed['token_trend'] = 0
        
        return processed
    
    def _update_metric_history(self, metric: str, value: float):
        """Update history for a specific metric"""
        if metric in self.metric_history:
            self.metric_history[metric].append(value)
            # Keep only last N data points
            if len(self.metric_history[metric]) > self.history_size:
                self.metric_history[metric] = self.metric_history[metric][-self.history_size:]
    
    def _calculate_efficiency_score(self, data: Dict[str, Any]) -> float:
        """Calculate efficiency score based on tokens per dollar"""
        cost = data.get('total_cost', 0)
        tokens = data.get('total_tokens', 0)
        
        if cost > 0:
            # Efficiency: tokens per dollar (normalized to 0-100)
            tokens_per_dollar = tokens / cost
            # Normalize assuming 10000 tokens/dollar is 100% efficient
            efficiency = min(100, (tokens_per_dollar / 10000) * 100)
            return efficiency
        
        return 0.0
    
    def get_metric_sparkline(self, metric: str) -> List[float]:
        """Get sparkline data for a specific metric"""
        return self.metric_history.get(metric, [])[-20:]  # Last 20 points
    
    def _get_mock_data(self) -> Dict[str, Any]:
        """Generate mock data for testing"""
        import random
        
        # Generate realistic-looking mock data
        base_cost = 42.50
        base_tokens = 125000
        
        # Add some randomness
        cost_variance = random.uniform(-2, 5)
        token_variance = random.randint(-5000, 10000)
        
        return {
            'total_cost': base_cost + cost_variance,
            'total_tokens': base_tokens + token_variance,
            'model': random.choice(['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']),
            'session': {
                'tokens': random.randint(1000, 50000),
                'cost': random.uniform(0.1, 5.0)
            },
            'daily': {
                'cost': random.uniform(10, 50),
                'tokens': random.randint(20000, 100000)
            },
            'weekly': {
                'cost': random.uniform(50, 200),
                'tokens': random.randint(100000, 500000)
            },
            'monthly': {
                'cost': random.uniform(200, 1000),
                'tokens': random.randint(500000, 2000000)
            }
        }