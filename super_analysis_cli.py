"""
Command-Line Version of Superannuation Analysis Tool
"""

import yaml
from simulation_engine import SimulationEngine


def print_header():
    print("=" * 80)
    print("SUPERANNUATION ANALYSIS TOOL - COMMAND LINE VERSION")
    print("=" * 80)
    print()


def get_float_input(prompt, default=None):
    """Get float input from user with default value"""
    if default is not None:
        prompt_text = f"{prompt} [default: {default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    while True:
        try:
            value = input(prompt_text).strip()
            if value == "" and default is not None:
                return float(default)
            return float(value)
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_int_input(prompt, default=None, min_val=None, max_val=None):
    """Get integer input from user with default value and validation"""
    if default is not None:
        prompt_text = f"{prompt} [default: {default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    while True:
        try:
            value = input(prompt_text).strip()
            if value == "" and default is not None:
                return int(default)
            value = int(value)
            
            if min_val is not None and value < min_val:
                print(f"  Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"  Value must be at most {max_val}")
                continue
            
            return value
        except ValueError:
            print("  Invalid input. Please enter a whole number.")


def display_results(allocation, results, investment, timeperiod, iterations):
    """Display analysis results"""
    print("\n")
    print("=" * 80)
    print("SUPERANNUATION ANALYSIS RESULTS")
    print("=" * 80)
    print()
    print(f"Investment Amount: ${investment:,.2f}")
    print(f"Time Period: {timeperiod} years")
    print(f"Monte Carlo Iterations: {iterations:,}")
    print()
    print("-" * 80)
    print("OPTIMAL ALLOCATION")
    print("-" * 80)
    print()
    
    # Display allocation
    for option, percentage in sorted(allocation.items(), key=lambda x: x[1], reverse=True):
        if percentage > 0:
            amount = investment * (percentage / 100.0)
            print(f"  {option:25s}: {percentage:5.1f}%  (${amount:,.2f})")
    
    print()
    print("-" * 80)
    print("PROJECTED OUTCOMES")
    print("-" * 80)
    print()
    print(f"  Expected Value (Mean):        ${results['mean']:,.2f}")
    print(f"  Median Value:                 ${results['median']:,.2f}")
    print(f"  Standard Deviation:           ${results['std']:,.2f}")
    print()
    print(f"  Best Case (90th percentile):  ${results['percentile_90']:,.2f}")
    print(f"  Worst Case (10th percentile): ${results['percentile_10']:,.2f}")
    print()
    print(f"  Range: ${results['min']:,.2f} to ${results['max']:,.2f}")
    print()
    
    # Calculate returns
    mean_return = ((results['mean'] / investment) ** (1/timeperiod) - 1) * 100
    print(f"  Average Annual Return: {mean_return:.2f}%")
    
    total_return = ((results['mean'] - investment) / investment) * 100
    print(f"  Total Return: {total_return:.2f}%")
    print()
    print("=" * 80)


def main():
    print_header()
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("Configuration loaded successfully.\n")
    except Exception as e:
        print(f"Error loading config.yaml: {e}")
        return
    
    # Display investment options
    print("Available Investment Options:")
    for name, params in config['investment_options'].items():
        print(f"  - {name}: {params['return_target']}% return target, "
              f"negative return every {params['risk_measure']} years")
    print()
    
    # Get user inputs
    print("Please enter the following parameters:\n")
    
    investment = get_float_input("Investment Amount ($)", default=100000)
    if investment <= 0:
        print("Error: Investment must be positive")
        return
    
    timeperiod = get_int_input("Time Period (years)", default=10, min_val=1)
    
    iterations = get_int_input("Monte Carlo Iterations (higher = more accurate but slower)", 
                              default=config['global_parameters']['monte_carlo_iterations'],
                              min_val=100)
    
    step = get_int_input("Allocation Step Size (10-50, higher = faster but less precise)", 
                        default=20, min_val=10, max_val=50)
    
    print("\n" + "-" * 80)
    print("Starting analysis... This may take a minute or two.")
    print("-" * 80 + "\n")
    
    # Initialize engine
    engine = SimulationEngine(config)
    engine.iterations = iterations
    
    # Run optimization
    try:
        optimal_allocation, results = engine.find_optimal_allocation(investment, timeperiod, step)
        
        # Display results
        display_results(optimal_allocation, results, investment, timeperiod, iterations)
        
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
