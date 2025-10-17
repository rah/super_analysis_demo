"""
Unit tests for simulation_engine.py
"""

import unittest
import yaml
import numpy as np
from simulation_engine import SimulationEngine


class TestSimulationEngine(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load configuration once for all tests"""
        with open('config.yaml', 'r') as f:
            cls.config = yaml.safe_load(f)
    
    def setUp(self):
        """Create a fresh engine instance for each test"""
        self.engine = SimulationEngine(self.config)
        self.engine.iterations = 100  # Use fewer iterations for faster tests
    
    def test_engine_initialization(self):
        """Test that engine initializes correctly with config"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(len(self.engine.investment_options), 5)
        self.assertIn('Growth', self.engine.investment_options)
        self.assertIn('Balanced', self.engine.investment_options)
        self.assertEqual(self.engine.inflation_rate, 2.5)
        self.assertEqual(self.engine.negative_return, -10.0)
    
    def test_investment_options_structure(self):
        """Test that all investment options have required attributes"""
        for name, option in self.engine.investment_options.items():
            self.assertIn('return_target', option)
            self.assertIn('risk_measure', option)
            self.assertIsInstance(option['return_target'], (int, float))
            self.assertIsInstance(option['risk_measure'], (int, float))
            self.assertGreater(option['risk_measure'], 0)
    
    def test_generate_return_output_type(self):
        """Test that generate_return produces numeric output"""
        for option_name in self.engine.investment_options.keys():
            return_value = self.engine.generate_return(option_name)
            self.assertIsInstance(return_value, (int, float))
    
    def test_generate_return_distribution(self):
        """Test that returns follow expected distribution over many samples"""
        option_name = 'Balanced'
        returns = [self.engine.generate_return(option_name) for _ in range(1000)]
        
        # Check that we get both positive and negative returns
        positive_returns = [r for r in returns if r > 0]
        negative_returns = [r for r in returns if r < 0]
        
        self.assertGreater(len(positive_returns), 0, "Should have some positive returns")
        self.assertGreater(len(negative_returns), 0, "Should have some negative returns")
        
        # Check mean is positive (for balanced option with positive return target)
        mean_return = np.mean(returns)
        self.assertGreater(mean_return, 0, "Mean return should be positive for Balanced option")
    
    def test_simulate_portfolio_positive_investment(self):
        """Test portfolio simulation with valid inputs"""
        allocation = {'Growth': 50, 'Balanced': 50, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        investment = 100000
        timeperiod = 5
        
        final_value = self.engine.simulate_portfolio(allocation, investment, timeperiod)
        
        self.assertIsInstance(final_value, (int, float))
        self.assertGreater(final_value, 0, "Final value should be positive")
    
    def test_simulate_portfolio_growth_over_time(self):
        """Test that portfolio generally grows over time"""
        allocation = {'Growth': 0, 'Balanced': 100, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        investment = 100000
        timeperiod = 10
        
        # Run multiple simulations and check average
        results = [self.engine.simulate_portfolio(allocation, investment, timeperiod) 
                  for _ in range(100)]
        avg_result = np.mean(results)
        
        # With positive return target, average should exceed initial investment
        self.assertGreater(avg_result, investment, 
                          "Average final value should exceed initial investment")
    
    def test_run_monte_carlo_structure(self):
        """Test that Monte Carlo results have correct structure"""
        allocation = {'Growth': 60, 'Balanced': 40, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        investment = 100000
        timeperiod = 10
        
        results = self.engine.run_monte_carlo(allocation, investment, timeperiod)
        
        # Check all required keys are present
        required_keys = ['mean', 'median', 'std', 'min', 'max', 
                        'percentile_10', 'percentile_90']
        for key in required_keys:
            self.assertIn(key, results)
            self.assertIsInstance(results[key], (int, float))
    
    def test_run_monte_carlo_statistical_validity(self):
        """Test that Monte Carlo statistics are logically consistent"""
        allocation = {'Growth': 50, 'Balanced': 50, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        investment = 100000
        timeperiod = 10
        
        results = self.engine.run_monte_carlo(allocation, investment, timeperiod)
        
        # Min should be less than or equal to mean
        self.assertLessEqual(results['min'], results['mean'])
        
        # Max should be greater than or equal to mean
        self.assertGreaterEqual(results['max'], results['mean'])
        
        # 10th percentile should be less than median
        self.assertLess(results['percentile_10'], results['median'])
        
        # 90th percentile should be greater than median
        self.assertGreater(results['percentile_90'], results['median'])
        
        # Standard deviation should be positive
        self.assertGreater(results['std'], 0)
        
        # Min should be less than max
        self.assertLess(results['min'], results['max'])
    
    def test_generate_allocations_sum_to_100(self):
        """Test that all generated allocations sum to 100%"""
        step = 20
        allocations = self.engine.generate_allocations(step)
        
        self.assertGreater(len(allocations), 0, "Should generate at least one allocation")
        
        for allocation in allocations:
            total = sum(allocation.values())
            self.assertEqual(total, 100, f"Allocation {allocation} should sum to 100")
    
    def test_generate_allocations_within_bounds(self):
        """Test that allocations respect step size"""
        step = 25
        allocations = self.engine.generate_allocations(step)
        
        for allocation in allocations:
            for percentage in allocation.values():
                self.assertTrue(percentage % step == 0 or percentage == 0,
                              f"Percentage {percentage} should be multiple of step {step}")
                self.assertGreaterEqual(percentage, 0)
                self.assertLessEqual(percentage, 100)
    
    def test_generate_allocations_different_steps(self):
        """Test that different step sizes produce different numbers of allocations"""
        alloc_10 = self.engine.generate_allocations(10)
        alloc_20 = self.engine.generate_allocations(20)
        alloc_50 = self.engine.generate_allocations(50)
        
        # Smaller steps should produce more combinations
        self.assertGreater(len(alloc_10), len(alloc_20))
        self.assertGreater(len(alloc_20), len(alloc_50))
    
    def test_find_optimal_allocation_returns_valid_result(self):
        """Test that optimization returns a valid allocation and results"""
        investment = 50000
        timeperiod = 5
        step = 50  # Use large step for faster test
        
        optimal_allocation, results = self.engine.find_optimal_allocation(
            investment, timeperiod, step
        )
        
        # Check allocation is valid
        self.assertIsInstance(optimal_allocation, dict)
        self.assertEqual(len(optimal_allocation), 5)
        total = sum(optimal_allocation.values())
        self.assertEqual(total, 100)
        
        # Check results structure
        self.assertIsInstance(results, dict)
        self.assertIn('mean', results)
        self.assertGreater(results['mean'], 0)
    
    def test_find_optimal_allocation_single_option(self):
        """Test optimization with single option allocations"""
        investment = 100000
        timeperiod = 10
        step = 100  # Forces single-option allocations
        
        optimal_allocation, results = self.engine.find_optimal_allocation(
            investment, timeperiod, step
        )
        
        # Should find one option with 100%
        percentages = list(optimal_allocation.values())
        self.assertIn(100, percentages)
        self.assertEqual(sum(percentages), 100)
    
    def test_edge_case_zero_timeperiod(self):
        """Test behavior with edge case inputs"""
        allocation = {'Growth': 100, 'Balanced': 0, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        investment = 100000
        timeperiod = 0  # Edge case
        
        # With 0 timeperiod, should return initial investment
        final_value = self.engine.simulate_portfolio(allocation, investment, timeperiod)
        self.assertEqual(final_value, investment)
    
    def test_edge_case_small_investment(self):
        """Test with very small investment amount"""
        allocation = {'Growth': 100, 'Balanced': 0, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        investment = 1  # Very small
        timeperiod = 5
        
        final_value = self.engine.simulate_portfolio(allocation, investment, timeperiod)
        self.assertGreater(final_value, 0)
    
    def test_all_options_allocation(self):
        """Test portfolio with all options allocated equally"""
        allocation = {'Growth': 20, 'Balanced': 20, 'Conservative Balanced': 20, 
                     'Stable': 20, 'Secure': 20}
        investment = 100000
        timeperiod = 10
        
        results = self.engine.run_monte_carlo(allocation, investment, timeperiod)
        
        self.assertGreater(results['mean'], 0)
        self.assertIsInstance(results['std'], (int, float))
    
    def test_conservative_vs_aggressive_allocation(self):
        """Test that aggressive allocations have higher volatility"""
        investment = 100000
        timeperiod = 10
        self.engine.iterations = 500  # More iterations for better comparison
        
        # Conservative allocation
        conservative = {'Growth': 0, 'Balanced': 0, 'Conservative Balanced': 0, 
                       'Stable': 50, 'Secure': 50}
        conservative_results = self.engine.run_monte_carlo(
            conservative, investment, timeperiod
        )
        
        # Aggressive allocation
        aggressive = {'Growth': 100, 'Balanced': 0, 'Conservative Balanced': 0, 
                     'Stable': 0, 'Secure': 0}
        aggressive_results = self.engine.run_monte_carlo(
            aggressive, investment, timeperiod
        )
        
        # Aggressive should have higher standard deviation (more volatile)
        self.assertGreater(aggressive_results['std'], conservative_results['std'],
                          "Aggressive allocation should be more volatile")
        
        # Aggressive should have higher mean return
        self.assertGreater(aggressive_results['mean'], conservative_results['mean'],
                          "Aggressive allocation should have higher expected return")


class TestConfigurationLoading(unittest.TestCase):
    
    def test_config_file_exists(self):
        """Test that config.yaml exists and is readable"""
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            self.assertIsNotNone(config)
        except FileNotFoundError:
            self.fail("config.yaml file not found")
    
    def test_config_has_required_sections(self):
        """Test that config has all required sections"""
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        self.assertIn('investment_options', config)
        self.assertIn('global_parameters', config)
    
    def test_config_investment_options_valid(self):
        """Test that all investment options are properly configured"""
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        options = config['investment_options']
        expected_options = ['Growth', 'Balanced', 'Conservative Balanced', 
                           'Stable', 'Secure']
        
        for option_name in expected_options:
            self.assertIn(option_name, options)
            self.assertIn('return_target', options[option_name])
            self.assertIn('risk_measure', options[option_name])
    
    def test_config_global_parameters_valid(self):
        """Test that global parameters are properly configured"""
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        params = config['global_parameters']
        
        self.assertIn('inflation_rate', params)
        self.assertIn('negative_return', params)
        self.assertIn('monte_carlo_iterations', params)
        
        self.assertGreater(params['monte_carlo_iterations'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
