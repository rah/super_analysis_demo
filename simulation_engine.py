"""
Monte Carlo Simulation Engine for Superannuation Analysis
"""

import numpy as np
from typing import Dict, List, Tuple
import itertools


class SimulationEngine:
    def __init__(self, config: Dict):
        self.investment_options = config['investment_options']
        self.global_params = config['global_parameters']
        self.inflation_rate = self.global_params['inflation_rate']
        self.negative_return = self.global_params['negative_return']
        self.iterations = self.global_params['monte_carlo_iterations']
    
    def generate_return(self, option_name: str) -> float:
        """
        Generate a random return for an investment option based on its characteristics.
        """
        option = self.investment_options[option_name]
        target_return = option['return_target'] + self.inflation_rate
        risk_measure = option['risk_measure']
        
        # Calculate probability of negative return based on risk measure
        # risk_measure is "negative returns expected every X years over 20 year period"
        prob_negative = 1.0 / risk_measure if risk_measure > 0 else 0
        
        # Calculate volatility based on risk measure (higher risk = higher volatility)
        volatility = target_return * (20.0 / risk_measure) * 0.15
        
        # Generate return
        if np.random.random() < prob_negative:
            # Negative return
            return np.random.uniform(self.negative_return, 0)
        else:
            # Positive return with normal distribution around target
            return np.random.normal(target_return, volatility)
    
    def simulate_portfolio(self, allocation: Dict[str, float], 
                          investment: float, timeperiod: int) -> float:
        """
        Simulate a single portfolio outcome over the timeperiod.
        """
        value = investment
        
        for year in range(timeperiod):
            portfolio_return = 0
            for option_name, percentage in allocation.items():
                if percentage > 0:
                    option_return = self.generate_return(option_name)
                    portfolio_return += (percentage / 100.0) * option_return
            
            value *= (1 + portfolio_return / 100.0)
        
        return value
    
    def run_monte_carlo(self, allocation: Dict[str, float], 
                       investment: float, timeperiod: int) -> Dict:
        """
        Run Monte Carlo simulation for a given allocation.
        """
        results = []
        
        for _ in range(self.iterations):
            final_value = self.simulate_portfolio(allocation, investment, timeperiod)
            results.append(final_value)
        
        results = np.array(results)
        
        return {
            'mean': np.mean(results),
            'median': np.median(results),
            'std': np.std(results),
            'min': np.min(results),
            'max': np.max(results),
            'percentile_10': np.percentile(results, 10),
            'percentile_90': np.percentile(results, 90)
        }
    
    def generate_allocations(self, step: int = 10) -> List[Dict[str, float]]:
        """
        Generate all possible allocation combinations.
        Step size determines granularity (10 = 0%, 10%, 20%, ..., 100%)
        """
        option_names = list(self.investment_options.keys())
        n_options = len(option_names)
        
        # Generate all combinations that sum to 100
        allocations = []
        
        # For efficiency, we'll use a step size
        percentages = list(range(0, 101, step))
        
        # Generate all combinations
        for combo in itertools.product(percentages, repeat=n_options):
            if sum(combo) == 100:
                allocation = {name: pct for name, pct in zip(option_names, combo)}
                allocations.append(allocation)
        
        return allocations
    
    def find_optimal_allocation(self, investment: float, timeperiod: int, 
                               step: int = 20) -> Tuple[Dict[str, float], Dict]:
        """
        Find the optimal allocation by testing various combinations.
        """
        allocations = self.generate_allocations(step)
        
        best_allocation = None
        best_result = None
        best_score = -float('inf')
        
        print(f"Testing {len(allocations)} allocation combinations...")
        
        for i, allocation in enumerate(allocations):
            # Skip empty allocations
            if all(v == 0 for v in allocation.values()):
                continue
            
            result = self.run_monte_carlo(allocation, investment, timeperiod)
            
            # Score based on mean return with penalty for risk (std deviation)
            # Higher mean is better, lower std is better
            score = result['mean'] - 0.5 * result['std']
            
            if score > best_score:
                best_score = score
                best_allocation = allocation
                best_result = result
            
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"Progress: {i + 1}/{len(allocations)} combinations tested")
        
        return best_allocation, best_result
