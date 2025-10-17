"""
Integration tests for the complete Superannuation Analysis application
"""

import unittest
import yaml
import sys
import numpy as np
from io import StringIO
from simulation_engine import SimulationEngine


class TestEndToEndAnalysis(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load configuration once for all tests"""
        with open('config.yaml', 'r') as f:
            cls.config = yaml.safe_load(f)
    
    def test_complete_analysis_workflow(self):
        """Test a complete analysis from start to finish"""
        # Initialize engine
        engine = SimulationEngine(self.config)
        engine.iterations = 1000  # Reasonable for integration test
        
        # Set parameters
        investment = 100000
        timeperiod = 10
        step = 20
        
        # Run optimization
        optimal_allocation, results = engine.find_optimal_allocation(
            investment, timeperiod, step
        )
        
        # Verify complete workflow produces valid outputs
        self.assertIsNotNone(optimal_allocation)
        self.assertIsNotNone(results)
        
        # Verify allocation
        self.assertEqual(sum(optimal_allocation.values()), 100)
        
        # Verify results completeness
        self.assertIn('mean', results)
        self.assertIn('median', results)
        self.assertIn('std', results)
        self.assertIn('percentile_10', results)
        self.assertIn('percentile_90', results)
        
        # Verify reasonable outcomes
        self.assertGreater(results['mean'], investment * 0.8)  # Not too pessimistic
        self.assertLess(results['mean'], investment * 5)  # Not too optimistic
    
    def test_multiple_timeperiods(self):
        """Test that analysis works correctly for different timeperiods"""
        engine = SimulationEngine(self.config)
        engine.iterations = 500
        investment = 100000
        step = 50
        
        results_5yr = {}
        results_15yr = {}
        
        # Test short timeperiod
        _, results_5yr = engine.find_optimal_allocation(investment, 5, step)
        self.assertGreater(results_5yr['mean'], 0)
        
        # Test long timeperiod
        _, results_15yr = engine.find_optimal_allocation(investment, 15, step)
        self.assertGreater(results_15yr['mean'], 0)
        
        # Longer timeperiod should generally produce higher returns
        self.assertGreater(results_15yr['mean'], results_5yr['mean'])
    
    def test_multiple_investment_amounts(self):
        """Test that analysis scales properly with different investment amounts"""
        engine = SimulationEngine(self.config)
        engine.iterations = 500
        timeperiod = 10
        step = 50
        
        # Small investment
        _, results_small = engine.find_optimal_allocation(10000, timeperiod, step)
        
        # Large investment
        _, results_large = engine.find_optimal_allocation(100000, timeperiod, step)
        
        # Returns should scale proportionally (approximately)
        ratio = results_large['mean'] / results_small['mean']
        self.assertAlmostEqual(ratio, 10.0, delta=2.0)  # Allow some variance
    
    def test_reproducibility_with_seed(self):
        """Test that results are consistent when using same random seed"""
        import numpy as np
        
        engine = SimulationEngine(self.config)
        engine.iterations = 1000
        investment = 100000
        timeperiod = 10
        
        allocation = {'Growth': 50, 'Balanced': 50, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        
        # Run with seed
        np.random.seed(42)
        results1 = engine.run_monte_carlo(allocation, investment, timeperiod)
        
        # Run again with same seed
        np.random.seed(42)
        results2 = engine.run_monte_carlo(allocation, investment, timeperiod)
        
        # Results should be very similar (allowing for floating point differences)
        self.assertAlmostEqual(results1['mean'], results2['mean'], places=2)
        self.assertAlmostEqual(results1['median'], results2['median'], places=2)
    
    def test_sensitivity_to_iterations(self):
        """Test that more iterations produce more stable results"""
        engine = SimulationEngine(self.config)
        investment = 100000
        timeperiod = 10
        
        allocation = {'Growth': 60, 'Balanced': 40, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        
        # Run with few iterations multiple times
        engine.iterations = 100
        results_low = [engine.run_monte_carlo(allocation, investment, timeperiod)['mean'] 
                      for _ in range(10)]
        std_low = np.std(results_low)
        
        # Run with many iterations multiple times
        engine.iterations = 5000
        results_high = [engine.run_monte_carlo(allocation, investment, timeperiod)['mean'] 
                       for _ in range(10)]
        std_high = np.std(results_high)
        
        # Higher iterations should have lower variance across runs
        self.assertLess(std_high, std_low,
                       "More iterations should produce more consistent results")
    
    def test_extreme_allocations(self):
        """Test that extreme allocations (100% in one option) work correctly"""
        engine = SimulationEngine(self.config)
        engine.iterations = 1000
        investment = 100000
        timeperiod = 10
        
        # Test 100% allocation to each option
        for option_name in engine.investment_options.keys():
            allocation = {name: (100 if name == option_name else 0) 
                         for name in engine.investment_options.keys()}
            
            results = engine.run_monte_carlo(allocation, investment, timeperiod)
            
            self.assertGreater(results['mean'], 0)
            self.assertGreater(results['std'], 0)
            self.assertLess(results['percentile_10'], results['percentile_90'])


class TestErrorHandling(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load configuration once for all tests"""
        with open('config.yaml', 'r') as f:
            cls.config = yaml.safe_load(f)
    
    def test_invalid_allocation_sum(self):
        """Test handling of allocation that doesn't sum to 100"""
        engine = SimulationEngine(self.config)
        
        # Allocation sums to 80 (invalid but should still work)
        allocation = {'Growth': 50, 'Balanced': 30, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        
        # Should still execute without crashing
        result = engine.simulate_portfolio(allocation, 100000, 10)
        self.assertIsInstance(result, (int, float))
    
    def test_negative_investment(self):
        """Test that negative investment is handled"""
        engine = SimulationEngine(self.config)
        allocation = {'Growth': 100, 'Balanced': 0, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        
        # Negative investment should still compute (mathematically valid)
        result = engine.simulate_portfolio(allocation, -100000, 10)
        self.assertIsInstance(result, (int, float))
    
    def test_very_long_timeperiod(self):
        """Test with unusually long timeperiod"""
        engine = SimulationEngine(self.config)
        engine.iterations = 100  # Keep test fast
        allocation = {'Growth': 100, 'Balanced': 0, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        
        # 50 year timeperiod
        result = engine.simulate_portfolio(allocation, 100000, 50)
        self.assertGreater(result, 0)
        self.assertIsInstance(result, (int, float))


class TestPerformance(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load configuration once for all tests"""
        with open('config.yaml', 'r') as f:
            cls.config = yaml.safe_load(f)
    
    def test_simulation_speed(self):
        """Test that simulations complete in reasonable time"""
        import time
        
        engine = SimulationEngine(self.config)
        engine.iterations = 1000
        
        allocation = {'Growth': 50, 'Balanced': 50, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        
        start_time = time.time()
        engine.run_monte_carlo(allocation, 100000, 10)
        elapsed_time = time.time() - start_time
        
        # 1000 iterations should complete in under 5 seconds
        self.assertLess(elapsed_time, 5.0,
                       f"Simulation took {elapsed_time:.2f}s, should be under 5s")
    
    def test_optimization_speed(self):
        """Test that optimization completes in reasonable time"""
        import time
        
        engine = SimulationEngine(self.config)
        engine.iterations = 500
        step = 50  # Large step for speed
        
        start_time = time.time()
        engine.find_optimal_allocation(100000, 10, step)
        elapsed_time = time.time() - start_time
        
        # With small iterations and large step, should be fast
        self.assertLess(elapsed_time, 30.0,
                       f"Optimization took {elapsed_time:.2f}s, should be under 30s")


class TestStatisticalProperties(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load configuration once for all tests"""
        with open('config.yaml', 'r') as f:
            cls.config = yaml.safe_load(f)
    
    def test_return_distributions(self):
        """Test that return distributions match expected properties"""
        engine = SimulationEngine(self.config)
        
        # Generate many returns for each option
        for option_name, option_data in engine.investment_options.items():
            returns = [engine.generate_return(option_name) for _ in range(5000)]
            
            mean_return = np.mean(returns)
            
            # Mean should be positive (though possibly small for conservative options)
            # Account for inflation adjustment
            expected_return = option_data['return_target'] + engine.inflation_rate
            
            # Allow reasonable variance from expected (wider tolerance for Monte Carlo randomness)
            self.assertGreater(mean_return, expected_return - 4.0,
                             f"{option_name} mean return too low: {mean_return} vs expected {expected_return}")
            self.assertLess(mean_return, expected_return + 4.0,
                          f"{option_name} mean return too high: {mean_return} vs expected {expected_return}")
    
    def test_percentile_accuracy(self):
        """Test that percentiles are calculated correctly"""
        engine = SimulationEngine(self.config)
        engine.iterations = 10000  # More iterations for accurate percentiles
        
        allocation = {'Growth': 50, 'Balanced': 50, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        
        results = engine.run_monte_carlo(allocation, 100000, 10)
        
        # 10th percentile should be roughly 10% of the way from min to max
        # 90th percentile should be roughly 90% of the way
        range_span = results['max'] - results['min']
        
        # These are rough checks - exact percentiles can vary
        self.assertGreater(results['percentile_10'], results['min'])
        self.assertLess(results['percentile_10'], results['median'])
        self.assertGreater(results['percentile_90'], results['median'])
        self.assertLess(results['percentile_90'], results['max'])


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
