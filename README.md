# Superannuation Analysis Tool

A sophisticated Monte Carlo simulation application that determines the optimal investment allocation strategy for superannuation portfolios. The tool analyzes various combinations of investment options to maximize returns while managing risk over your specified investment timeframe.

## Overview

This application uses advanced statistical modeling to simulate thousands of possible investment outcomes across different portfolio allocations. By testing various combinations of five investment options (Growth, Balanced, Conservative Balanced, Stable, and Secure), it identifies the optimal mix that balances expected returns against risk exposure.

## Key Features

- **Monte Carlo Simulation Engine**: Runs thousands of simulations to model realistic investment outcomes
- **Portfolio Optimization**: Automatically finds the best allocation mix across five investment types
- **Risk-Adjusted Analysis**: Balances return potential with downside risk protection
- **Dual Interface**: Choose between graphical (GUI) or command-line (CLI) interfaces
- **Flexible Configuration**: Customize simulation parameters via YAML configuration file
- **Comprehensive Results**: Detailed statistics including mean, median, percentiles, and risk measures
- **Performance Tuning**: Adjust speed vs accuracy trade-offs based on your needs

## Investment Options

The tool analyzes allocations across five pre-configured investment types, each with distinct risk/return characteristics:

| Option | Return Target* | Risk Profile | Negative Returns Expected |
|--------|---------------|--------------|---------------------------|
| **Growth** | 5.5% | Highest return, highest volatility | Every 4 years (over 20-year period) |
| **Balanced** | 4.0% | Moderate return and risk | Every 5 years |
| **Conservative Balanced** | 3.0% | Lower risk, stable growth | Every 6 years |
| **Stable** | 2.0% | Low volatility, predictable | Every 8 years |
| **Secure** | 1.0% | Lowest risk, capital preservation | Every 12 years |

*Return targets are percentage returns above inflation on a 10-year rolling average

## Installation

### Prerequisites

- Python 3.10 or higher
- Conda package manager (recommended)
- Windows operating system

### Setup Instructions

1. **Clone or download this repository** to your local machine

2. **Create a conda environment**:
   ```bash
   conda create -n super_analysis python=3.10 -y
   ```

3. **Activate the environment**:
   ```bash
   conda activate super_analysis
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

The required packages are:
- `numpy` - For numerical computations and statistical analysis
- `PyYAML` - For configuration file parsing

## Usage

### GUI Application (Recommended)

Launch the graphical user interface for an intuitive, interactive experience:

```bash
conda activate super_analysis
python super_analysis_app.py
```

**GUI Features:**
- Visual input forms for all parameters
- Real-time progress updates during analysis
- Formatted results display with scrollable output
- Easy-to-read allocation breakdown
- All statistics presented in clear tables

**Using the GUI:**
1. Enter your investment amount (default: $100,000)
2. Specify the investment timeframe in years (default: 10 years)
3. Set the number of Monte Carlo iterations (default: 10,000)
4. Choose allocation step size for optimization granularity (default: 20%)
5. Click "Run Analysis" and wait for results
6. Review the optimal allocation and projected outcomes

### Command-Line Application

For headless systems, automation, or if the GUI doesn't work:

```bash
conda activate super_analysis
python super_analysis_cli.py
```

The CLI version prompts for each parameter with sensible defaults. Simply press Enter to accept the default value or type a custom value.

### Automated Testing

Run a quick test with preset parameters to verify the installation:

```bash
conda activate super_analysis
python test_full.py
```

This executes a complete analysis with predefined settings and displays results in approximately 30-60 seconds.

## Input Parameters

### Investment Amount
- **Description**: Total amount to invest in your superannuation
- **Format**: Dollar amount (e.g., 100000)
- **Typical Range**: $50,000 - $500,000+
- **Default**: $100,000

### Time Period
- **Description**: Investment horizon in years
- **Format**: Whole number of years
- **Typical Range**: 5 - 30 years
- **Default**: 10 years
- **Note**: Longer timeframes generally favor higher-growth allocations

### Monte Carlo Iterations
- **Description**: Number of simulation runs to perform
- **Format**: Positive integer
- **Typical Range**: 1,000 - 50,000
- **Default**: 10,000
- **Impact**: 
  - Lower values (1,000-5,000): Faster execution, less precise
  - Higher values (20,000-50,000): Slower execution, more accurate

### Allocation Step Size
- **Description**: Granularity of portfolio allocation combinations tested
- **Format**: Percentage (10, 20, 25, 33, or 50)
- **Default**: 20%
- **Impact**:
  - 10%: Most precise (1,001 combinations) but slowest
  - 20%: Balanced precision (126 combinations)
  - 50%: Fastest (21 combinations) but least precise

## Understanding Results

### Optimal Allocation

The tool displays the recommended percentage allocation to each investment option. Only options with non-zero allocations are shown.

**Example Output:**
```
OPTIMAL ALLOCATION
--------------------------------------------------
  Balanced                 :  60.0%  ($60,000.00)
  Growth                   :  40.0%  ($40,000.00)
```

This suggests investing 60% in Balanced and 40% in Growth options for optimal risk-adjusted returns.

### Projected Outcomes

**Expected Value (Mean)**: Average outcome across all simulations - the most likely result

**Median Value**: Middle value when all outcomes are sorted - less affected by extreme outliers

**Standard Deviation**: Measure of volatility - higher values indicate more variable outcomes

**90th Percentile**: Best-case scenario (you have a 10% chance of doing better than this)

**10th Percentile**: Worst-case scenario (you have a 90% chance of doing better than this)

**Range**: Minimum and maximum values observed across all simulations

**Average Annual Return**: Compound annual growth rate over the investment period

**Total Return**: Overall percentage gain from start to finish

### Example Results Interpretation

```
PROJECTED OUTCOMES
--------------------------------------------------
  Expected Value (Mean):        $154,950.82
  Median Value:                 $153,759.87
  Standard Deviation:           $22,261.96
  Best Case (90th percentile):  $184,192.39
  Worst Case (10th percentile): $126,929.60
  Average Annual Return:         4.48%
  Total Return:                  54.95%
```

**Interpretation**: With a $100,000 investment over 10 years, you can expect around $155,000 on average (4.48% annual growth). There's a 90% chance you'll have at least $127,000, and a 10% chance you'll exceed $184,000. The standard deviation suggests moderate volatility.

## Configuration

The `config.yaml` file controls investment characteristics and simulation parameters:

### Customizing Investment Options

```yaml
investment_options:
  Growth:
    return_target: 5.5  # % return above inflation
    risk_measure: 4     # negative return every X years
```

Modify these values to reflect different market conditions or investment products.

### Global Parameters

```yaml
global_parameters:
  inflation_rate: 2.5        # expected annual inflation %
  negative_return: -10.0     # typical negative return magnitude %
  monte_carlo_iterations: 10000  # default simulation count
```

Adjust these to match economic forecasts or change default settings.

## Technical Architecture

### Simulation Engine (`simulation_engine.py`)

**Core Components:**
1. **Return Generation**: Models realistic returns based on historical risk measures
2. **Portfolio Simulation**: Tracks value evolution over the investment period
3. **Monte Carlo Runner**: Executes thousands of independent simulations
4. **Optimization Algorithm**: Tests all allocation combinations to find the optimal mix

**Methodology:**
- Returns follow probability distributions based on risk profiles
- Negative returns occur at frequencies matching historical patterns
- Positive returns use normal distributions with volatility scaling
- Portfolio optimization uses mean-variance approach with risk penalty
- Scoring formula: `score = mean_return - 0.5 * standard_deviation`

### Performance Characteristics

| Iterations | Step Size | Combinations | Typical Runtime |
|------------|-----------|--------------|-----------------|
| 1,000 | 20% | 126 | 5-10 seconds |
| 5,000 | 20% | 126 | 20-30 seconds |
| 10,000 | 20% | 126 | 40-60 seconds |
| 10,000 | 10% | 1,001 | 5-8 minutes |
| 50,000 | 20% | 126 | 3-5 minutes |

**Optimization Tips:**
- For quick estimates: Use 1,000 iterations with 20% step
- For final decisions: Use 10,000+ iterations with 10% step
- For very large investments: Consider 50,000 iterations with 10% step

## Troubleshooting

### GUI Won't Launch

**Symptoms**: Window doesn't appear, immediate crash, or tkinter errors

**Solutions:**
1. Use the CLI version instead: `python super_analysis_cli.py`
2. Verify tkinter installation: `python -c "import tkinter"`
3. Check conda environment is activated: `conda activate super_analysis`
4. Try the automated test: `python test_full.py`

### Slow Performance

**Symptoms**: Analysis takes longer than expected

**Solutions:**
1. Reduce iterations (try 5,000 or 1,000)
2. Increase allocation step size (try 25% or 50%)
3. Close other resource-intensive applications
4. Check CPU usage - simulation is computationally intensive

### Unexpected Results

**Symptoms**: Allocations seem counterintuitive or results vary between runs

**Explanations:**
1. Monte Carlo methods have inherent randomness - run more iterations for stability
2. Optimal allocation depends heavily on timeframe - longer periods favor growth
3. Risk-adjusted optimization balances returns against volatility
4. Small differences in step size can lead to different local optima

### Configuration Errors

**Symptoms**: Errors loading config.yaml or invalid parameters

**Solutions:**
1. Verify YAML syntax (indentation must be consistent)
2. Check all required fields are present
3. Ensure numeric values don't have units or symbols
4. Validate percentage values are positive numbers

## File Structure

```
super_analysis_demo/
├── config.yaml                 # Configuration file
├── super_analysis_app.py       # GUI application
├── super_analysis_cli.py       # Command-line application
├── simulation_engine.py        # Monte Carlo engine
├── test_full.py               # Automated test script
├── requirements.txt           # Python dependencies
├── README.md                  # This documentation
└── super_analysis_spec.md     # Original specification
```

## Example Workflow

1. **Initial Exploration**: Run `test_full.py` to see example output
2. **Quick Analysis**: Use GUI with default settings for rapid results
3. **Refinement**: Adjust iterations to 20,000 and step to 10% for precision
4. **Scenario Testing**: Try different investment amounts and timeframes
5. **Decision Making**: Compare results across multiple analyses

## Limitations and Considerations

- **Historical Performance**: Past risk measures may not predict future results
- **Market Conditions**: Assumes relatively stable economic environment
- **Inflation**: Uses fixed inflation rate; actual inflation varies
- **Fees**: Does not account for management fees or transaction costs
- **Tax**: Results are pre-tax; consult a tax professional
- **Simplifications**: Real markets have complexities not captured in the model
- **Rebalancing**: Assumes allocations remain constant over time

## Best Practices

1. **Run Multiple Scenarios**: Test different timeframes and amounts
2. **Use High Iterations**: For final decisions, use 20,000+ iterations
3. **Consider Your Risk Tolerance**: Optimal allocation may not match your comfort level
4. **Regular Review**: Rerun analysis annually or when circumstances change
5. **Professional Advice**: Use results as input for discussions with financial advisors
6. **Diversification**: Remember that real diversification includes assets beyond superannuation

## Support and Contribution

This tool is provided as-is for educational and planning purposes. For questions or issues:

1. Check this README thoroughly
2. Review the troubleshooting section
3. Examine the configuration file syntax
4. Run test scripts to isolate problems

## License and Disclaimer

This software is provided for informational and educational purposes only. It does not constitute financial advice. Investment decisions should be made in consultation with qualified financial professionals. Past performance and simulated results do not guarantee future returns. The authors assume no liability for financial decisions made based on this tool's output.

## Version History

**Current Version**: 1.0.0
- Initial release with GUI and CLI interfaces
- Monte Carlo simulation with five investment options
- Configurable parameters via YAML
- Comprehensive statistical output
