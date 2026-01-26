import argparse
import csv
import os
import re
import sys

def print_progress_bar(iteration, total, length=40):
    """
    Helper function to print a text-based progress bar to the console.
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {percent}% Complete ({iteration}/{total})')
    sys.stdout.flush()

def parse_logs(folder_path, output_filename):
    """
    Scrapes genetic programming logs for run number, generation, 
    code size stats, and unique behaviors.
    """
    
    # 1. Compile Regex Patterns
    filename_pattern = re.compile(r'run(\d+)\.txt$')
    generation_start_pattern = re.compile(r'STARTING\s+(\d+)')
    code_size_line_check = re.compile(r':code-size\s+\{')
    mean_pattern = re.compile(r':mean\s+([^,\}\s]+)')
    median_pattern = re.compile(r':50%\s+([^,\}\s]+)')
    unique_behaviors_pattern = re.compile(r':unique-behaviors\s+(\d+)')

    rows = []

    # 2. Check directory existence
    if not os.path.isdir(folder_path):
        print(f"Error: The directory '{folder_path}' does not exist.")
        sys.exit(1)

    print(f"Scanning directory: {os.path.abspath(folder_path)}...")

    # 3. Identify valid files first
    all_entries = []
    try:
        with os.scandir(folder_path) as it:
            for entry in it:
                if entry.is_file() and filename_pattern.search(entry.name):
                    all_entries.append(entry.path)
    except OSError as e:
        print(f"Error accessing directory: {e}")
        sys.exit(1)

    total_files = len(all_entries)
    if total_files == 0:
        print("No matching 'runN.txt' files found.")
        sys.exit(0)

    print(f"Found {total_files} logs. Starting processing...")
    print_progress_bar(0, total_files)

    # 4. Process files
    for i, file_path in enumerate(all_entries):
        
        # Extract run number
        filename = os.path.basename(file_path)
        fname_match = filename_pattern.search(filename)
        run_number = fname_match.group(1)
            
        current_row = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # --- Check for New Generation ---
                    gen_match = generation_start_pattern.search(line)
                    if gen_match:
                        if current_row and 'generation' in current_row:
                            rows.append(current_row)
                        
                        current_row = {
                            'runNumber': run_number,
                            'generation': gen_match.group(1),
                            'codeSizeMean': '',
                            'codeSizeMedian': '',
                            'uniqueBehaviors': ''
                        }
                        continue
                    
                    if not current_row:
                        continue

                    # --- Check for Code Size Statistics ---
                    if code_size_line_check.search(line):
                        mean_match = mean_pattern.search(line)
                        if mean_match:
                            current_row['codeSizeMean'] = mean_match.group(1)
                        
                        median_match = median_pattern.search(line)
                        if median_match:
                            current_row['codeSizeMedian'] = median_match.group(1)

                    # --- Check for Unique Behaviors ---
                    beh_match = unique_behaviors_pattern.search(line)
                    if beh_match:
                        current_row['uniqueBehaviors'] = beh_match.group(1)

                # End of file: Append the very last generation row
                if current_row and 'generation' in current_row:
                    rows.append(current_row)

        except Exception as e:
            sys.stdout.write('\r' + ' ' * 80 + '\r') 
            print(f"Error reading file {filename}: {e}")
        
        # Update Progress Bar
        print_progress_bar(i + 1, total_files)

    print() # New line after bar finishes

    # 5. Sort and Write to CSV
    print("Sorting and saving data...")
    rows.sort(key=lambda x: (int(x['runNumber']), int(x['generation'])))

    headers = ['runNumber', 'generation', 'codeSizeMean', 'codeSizeMedian', 'uniqueBehaviors']
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Data written to: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape GP log files to CSV.")
    # nargs='?' makes the argument optional
    # default='.' means it defaults to current directory if nothing is provided
    parser.add_argument("folder", type=str, nargs='?', default='.', 
                        help="Path to the folder containing runN.txt files (defaults to current dir)")
    
    args = parser.parse_args()

    # 1. Get the Absolute Path (resolves '.' to '/home/user/my_experiment')
    abs_folder_path = os.path.abspath(args.folder)
    
    # 2. Get the base name of that absolute path (e.g. 'my_experiment')
    folder_name = os.path.basename(abs_folder_path)
    
    # 3. Construct filename
    output_name = f"{folder_name}-size-and-diversity.csv"
    
    parse_logs(args.folder, output_name)