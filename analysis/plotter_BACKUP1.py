import argparse
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# --- Publication Style Settings ---
# These settings make the text larger and the lines thicker for readability
plt.rcParams.update({
    'font.size': 14,
    'axes.labelsize': 16,
    'axes.titlesize': 18,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'lines.linewidth': 2.5,
    'grid.alpha': 0.4
})

def parse_fraction(val):
    """Handle values that might be floats, ints, or Clojure fractions."""
    try:
        val = str(val).strip()
        if '/' in val:
            num, den = val.split('/')
            return float(num) / float(den)
        return float(val)
    except (ValueError, TypeError):
        return None

def load_stats(filepath, mode='mean'):
    """
    Loads CSV and returns a dataframe grouped by generation.
    mode='mean' -> calculates mean and std
    mode='median' -> calculates median, 25%, and 75% quantiles
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        sys.exit(1)

    metric_cols = ['codeSizeMean', 'codeSizeMedian', 'uniqueBehaviors']
    
    for col in metric_cols:
        if col in df.columns:
            df[col] = df[col].apply(parse_fraction)

    # Group by generation
    grouped = df.groupby('generation')[metric_cols]

    if mode == 'mean':
        return grouped.agg(['mean', 'std'])
    elif mode == 'median':
        # Lambda functions for quartiles
        q25 = lambda x: x.quantile(0.25)
        q75 = lambda x: x.quantile(0.75)
        return grouped.agg(['median', q25, q75])
    else:
        raise ValueError("Invalid mode. Use 'mean' or 'median'.")

def plot_and_save(file1, file2, label1, label2, prefix, mode):
    
    # 1. Process Data
    df1 = load_stats(file1, mode)
    df2 = load_stats(file2, mode)

    metrics = [
        ('codeSizeMean', 'Mean Size', 'mean_code_size'),
        ('codeSizeMedian', 'Median Size', 'median_code_size'),
        ('uniqueBehaviors', 'Unique Behaviors', 'unique_behaviors')
    ]

    # 2. Define Styles for B&W Contrast
    # Setting 1: Black, Solid Line
    style1 = {'color': 'black', 'linestyle': '-', 'label': label1}
    # Setting 2: Dark Gray, Dashed Line (distinguishable even in grayscale)
    style2 = {'color': "#0088FF", 'linestyle': '-', 'label': label2}

    for col_name, title, suffix in metrics:
        plt.figure(figsize=(10, 6))
        
        # --- Plot Setting 1 ---
        if col_name in df1:
            generations = df1.index
            if mode == 'mean':
                center = df1[col_name]['mean']
                lower = center - df1[col_name]['std']
                upper = center + df1[col_name]['std']
            else: # median
                center = df1[col_name]['median']
                lower = df1[col_name]['<lambda_0>'] # 25%
                upper = df1[col_name]['<lambda_1>'] # 75%
            
            plt.plot(generations, center, **style1)
            plt.fill_between(generations, lower, upper, color=style1['color'], alpha=0.2, linewidth=2)
        
        # --- Plot Setting 2 ---
        if col_name in df2:
            generations = df2.index
            if mode == 'mean':
                center = df2[col_name]['mean']
                lower = center - df2[col_name]['std']
                upper = center + df2[col_name]['std']
            else: # median
                center = df2[col_name]['median']
                lower = df2[col_name]['<lambda_0>'] # 25%
                upper = df2[col_name]['<lambda_1>'] # 75%
            
            plt.plot(generations, center, **style2)
            plt.fill_between(generations, lower, upper, color=style2['color'], alpha=0.3, linewidth=2)

        # Styling
        stats_label = "Mean ± Std Dev" if mode == 'mean' else "Median ± Quartiles"
        
        # plt.title(f"{title}\n({stats_label})")
        plt.xlabel("Generation")
        plt.ylabel(title)
        
        # Subtle grid
        plt.grid(True, linestyle=':', color='gray', alpha=0.5)
        
        # Legend with a frame to block out data lines underneath it
        plt.legend(frameon=True, framealpha=1, edgecolor='black')
        
        # Tight layout ensures labels aren't cut off
        plt.tight_layout()
        
        # Save
        output_filename = f"{prefix}_{suffix}.pdf"
        plt.savefig(output_filename, format='pdf', dpi=300)
        print(f"Saved: {os.path.abspath(output_filename)}")
        plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot GP logs for publication.")
    parser.add_argument("csv1", type=str, help="First CSV file")
    parser.add_argument("csv2", type=str, help="Second CSV file")
    parser.add_argument("--label1", type=str, default="Setting 1", help="Label for first file")
    parser.add_argument("--label2", type=str, default="Setting 2", help="Label for second file")
    parser.add_argument("--prefix", type=str, default="plot", help="Output filename prefix")
    
    # New argument for statistical mode
    parser.add_argument("--stats", type=str, choices=['mean', 'median'], default='mean', 
                        help="Choose 'mean' (Mean +/- Std) or 'median' (Median +/- Quartiles)")

    args = parser.parse_args()
    
    plot_and_save(args.csv1, args.csv2, args.label1, args.label2, args.prefix, args.stats)