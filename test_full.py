"""
Automated test of the full analysis with preset parameters
"""

import yaml
from simulation_engine import SimulationEngine

print("=" * 80)
print("SUPERANNUATION ANALYSIS TOOL - AUTOMATED TEST")
print("=" * 80)
print()

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

print("Configuration loaded successfully.\n")

# Test parameters
investment = 100000
timeperiod = 10
iterations = 5000  # Reduced for faster testing
step = 20

print(f"Test Parameters:")
print(f"  Investment: ${investment:,.2f}")
print(f"  Time Period: {timeperiod} years")
print(f"  Iterations: {iterations:,}")
print(f"  Step Size: {step}%")
print()

# Initialize engine
engine = SimulationEngine(config)
engine.iterations = iterations

print("Running Monte Carlo optimization...")
print("This will test various allocation combinations.\n")

# Find optimal allocation
optimal_allocation, results = engine.find_optimal_allocation(investment, timeperiod, step)

# Display results
print("\n")
print("=" * 80)
print("RESULTS")
print("=" * 80)
print()
print("OPTIMAL ALLOCATION:")
for option, percentage in sorted(optimal_allocation.items(), key=lambda x: x[1], reverse=True):
    if percentage > 0:
        amount = investment * (percentage / 100.0)
        print(f"  {option:25s}: {percentage:5.1f}%  (${amount:,.2f})")

print()
print("PROJECTED OUTCOMES:")
print(f"  Expected Value (Mean):        ${results['mean']:,.2f}")
print(f"  Median Value:                 ${results['median']:,.2f}")
print(f"  Standard Deviation:           ${results['std']:,.2f}")
print(f"  Best Case (90th percentile):  ${results['percentile_90']:,.2f}")
print(f"  Worst Case (10th percentile): ${results['percentile_10']:,.2f}")
print()

mean_return = ((results['mean'] / investment) ** (1/timeperiod) - 1) * 100
total_return = ((results['mean'] - investment) / investment) * 100
print(f"  Average Annual Return: {mean_return:.2f}%")
print(f"  Total Return: {total_return:.2f}%")
print()
print("=" * 80)
print("\nTest completed successfully!")
