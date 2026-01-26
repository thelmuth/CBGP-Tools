import argparse
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# --- Publication Style Settings ---
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

def plot_single_series(df, col_name, mode, scale_factor, style):
    """
    Helper function to plot a single line + error band.
    """
    if col_name not in df:
        return

    generations = df.index
    
    # Calculate Center, Lower, and Upper bounds based on mode
    if mode == 'mean':
        center = df[col_name]['mean'] / scale_factor
        std_dev = df[col_name]['std'] / scale_factor
        lower = center - std_dev
        upper = center + std_dev
    else: # median
        center = df[col_name]['median'] / scale_factor
        # The quartiles are stored in columns with lambda names by pandas aggregation
        lower = df[col_name]['<lambda_0>'] / scale_factor
        upper = df[col_name]['<lambda_1>'] / scale_factor

    # Plot Line
    plt.plot(generations, center, 
             color=style['color'], 
             linestyle=style['linestyle'], 
             label=style['label'])
    
    # Plot Band
    plt.fill_between(generations, lower, upper, 
                     color=style['color'], 
                     alpha=style['fill_alpha'], 
                     linewidth=style['linewidth'])

def plot_and_save(file1, file2, label1, label2, prefix, mode):
    
    # 1. Process Data
    df1 = load_stats(file1, mode)
    df2 = load_stats(file2, mode)

    metrics = [
        ('codeSizeMean', 'Mean Size', 'mean_code_size'),
        ('codeSizeMedian', 'Median Size', 'median_code_size'),
        ('uniqueBehaviors', 'Diversity (Unique Behaviors / 1000)', 'diversity') 
    ]

    # 2. Define Styles
    # I added 'fill_alpha' here so you can keep your specific transparency settings
    style1 = {'color': 'black', 'linestyle': '-', 'label': label1, 'fill_alpha': 0.2, 'linewidth': 1}
    style2 = style1.copy()
    style2['color'] = "#00AAFF"
    style2['label'] = label2
    style2['linewidth'] = 1

    for col_name, title, suffix in metrics:
        plt.figure(figsize=(10, 6))
        
        # Determine scaling
        scale_factor = 1000.0 if col_name == 'uniqueBehaviors' else 1.0

        # --- Plot Both Series using Helper ---
        plot_single_series(df1, col_name, mode, scale_factor, style1)
        plot_single_series(df2, col_name, mode, scale_factor, style2)

        # Styling
        plt.xlabel("Generation")
        plt.ylabel(title)
        
        if col_name == 'uniqueBehaviors':
            plt.ylim(0, 1)

        plt.grid(True, linestyle=':', color='gray', alpha=0.5)
        plt.legend(frameon=True, framealpha=1, edgecolor='black')
        plt.tight_layout()
        
        output_filename = f"images/{prefix}_{suffix}.pdf"
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
    parser.add_argument("--stats", type=str, choices=['mean', 'median'], default='mean', 
                        help="Choose 'mean' or 'median'")

    args = parser.parse_args()
    
    plot_and_save(args.csv1, args.csv2, args.label1, args.label2, args.prefix, args.stats)