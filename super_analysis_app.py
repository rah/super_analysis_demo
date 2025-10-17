"""
Superannuation Analysis Application - Main GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import yaml
import threading
from simulation_engine import SimulationEngine


class SuperAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Superannuation Analysis Tool")
        self.root.geometry("800x700")
        
        # Load configuration
        self.load_config()
        
        # Initialize simulation engine
        self.engine = SimulationEngine(self.config)
        
        # Create GUI
        self.create_widgets()
        
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open('config.yaml', 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config.yaml: {str(e)}")
            self.root.destroy()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Superannuation Analysis Tool", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Investment Amount
        ttk.Label(input_frame, text="Investment Amount ($):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.investment_var = tk.StringVar(value="100000")
        investment_entry = ttk.Entry(input_frame, textvariable=self.investment_var, width=20)
        investment_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Time Period
        ttk.Label(input_frame, text="Time Period (years):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.timeperiod_var = tk.StringVar(value="10")
        timeperiod_entry = ttk.Entry(input_frame, textvariable=self.timeperiod_var, width=20)
        timeperiod_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Monte Carlo Iterations
        ttk.Label(input_frame, text="Iterations (speed vs accuracy):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.iterations_var = tk.StringVar(value=str(self.config['global_parameters']['monte_carlo_iterations']))
        iterations_entry = ttk.Entry(input_frame, textvariable=self.iterations_var, width=20)
        iterations_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Allocation Step Size
        ttk.Label(input_frame, text="Allocation Step (10-50%):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.step_var = tk.StringVar(value="20")
        step_entry = ttk.Entry(input_frame, textvariable=self.step_var, width=20)
        step_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Label(input_frame, text="(Higher = faster but less precise)", 
                 font=('Arial', 8, 'italic')).grid(row=3, column=2, sticky=tk.W, pady=5, padx=5)
        
        # Run Analysis Button
        self.run_button = ttk.Button(main_frame, text="Run Analysis", 
                                     command=self.run_analysis, style='Accent.TButton')
        self.run_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Progress Label
        self.progress_label = ttk.Label(main_frame, text="", foreground="blue")
        self.progress_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Results Section
        results_frame = ttk.LabelFrame(main_frame, text="Optimal Allocation Results", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Results Text Area
        self.results_text = scrolledtext.ScrolledText(results_frame, width=90, height=25, 
                                                      font=('Courier', 10))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def validate_inputs(self):
        """Validate user inputs"""
        try:
            investment = float(self.investment_var.get())
            if investment <= 0:
                raise ValueError("Investment must be positive")
            
            timeperiod = int(self.timeperiod_var.get())
            if timeperiod <= 0:
                raise ValueError("Time period must be positive")
            
            iterations = int(self.iterations_var.get())
            if iterations < 100:
                raise ValueError("Iterations must be at least 100")
            
            step = int(self.step_var.get())
            if step < 10 or step > 50:
                raise ValueError("Step size must be between 10 and 50")
            
            return investment, timeperiod, iterations, step
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return None
    
    def run_analysis(self):
        """Run the Monte Carlo analysis"""
        # Validate inputs
        validated = self.validate_inputs()
        if not validated:
            return
        
        investment, timeperiod, iterations, step = validated
        
        # Update engine iterations
        self.engine.iterations = iterations
        
        # Disable button during analysis
        self.run_button.config(state='disabled')
        self.progress_label.config(text="Running analysis... Please wait.")
        self.results_text.delete(1.0, tk.END)
        
        # Run analysis in separate thread to keep GUI responsive
        thread = threading.Thread(target=self.run_analysis_thread, 
                                 args=(investment, timeperiod, step))
        thread.daemon = True
        thread.start()
    
    def run_analysis_thread(self, investment, timeperiod, step):
        """Run analysis in separate thread"""
        try:
            # Find optimal allocation
            optimal_allocation, results = self.engine.find_optimal_allocation(
                investment, timeperiod, step
            )
            
            # Display results in main thread
            self.root.after(0, self.display_results, 
                          optimal_allocation, results, investment, timeperiod)
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", 
                          f"Analysis failed: {str(e)}")
            self.root.after(0, self.reset_ui)
    
    def display_results(self, allocation, results, investment, timeperiod):
        """Display analysis results"""
        self.results_text.delete(1.0, tk.END)
        
        output = []
        output.append("=" * 80)
        output.append("SUPERANNUATION ANALYSIS RESULTS")
        output.append("=" * 80)
        output.append("")
        output.append(f"Investment Amount: ${investment:,.2f}")
        output.append(f"Time Period: {timeperiod} years")
        output.append(f"Monte Carlo Iterations: {self.engine.iterations:,}")
        output.append("")
        output.append("-" * 80)
        output.append("OPTIMAL ALLOCATION")
        output.append("-" * 80)
        output.append("")
        
        # Display allocation
        for option, percentage in sorted(allocation.items(), key=lambda x: x[1], reverse=True):
            if percentage > 0:
                amount = investment * (percentage / 100.0)
                output.append(f"  {option:25s}: {percentage:5.1f}%  (${amount:,.2f})")
        
        output.append("")
        output.append("-" * 80)
        output.append("PROJECTED OUTCOMES")
        output.append("-" * 80)
        output.append("")
        output.append(f"  Expected Value (Mean):        ${results['mean']:,.2f}")
        output.append(f"  Median Value:                 ${results['median']:,.2f}")
        output.append(f"  Standard Deviation:           ${results['std']:,.2f}")
        output.append("")
        output.append(f"  Best Case (90th percentile):  ${results['percentile_90']:,.2f}")
        output.append(f"  Worst Case (10th percentile): ${results['percentile_10']:,.2f}")
        output.append("")
        output.append(f"  Range: ${results['min']:,.2f} to ${results['max']:,.2f}")
        output.append("")
        
        # Calculate returns
        mean_return = ((results['mean'] / investment) ** (1/timeperiod) - 1) * 100
        output.append(f"  Average Annual Return: {mean_return:.2f}%")
        
        total_return = ((results['mean'] - investment) / investment) * 100
        output.append(f"  Total Return: {total_return:.2f}%")
        output.append("")
        output.append("=" * 80)
        
        # Insert results
        self.results_text.insert(1.0, "\n".join(output))
        
        # Reset UI
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI after analysis"""
        self.run_button.config(state='normal')
        self.progress_label.config(text="Analysis complete!")


def main():
    root = tk.Tk()
    app = SuperAnalysisApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
