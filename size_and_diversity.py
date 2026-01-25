import argparse
import csv
import os
import re
import sys

def parse_logs(folder_path, output_filename="output.csv"):
    """
    Scrapes genetic programming logs for run number, generation, 
    code size stats, and unique behaviors.
    """
    
    # 1. Compile Regex Patterns for performance
    # Matches filenames like run1.txt, run100.txt
    filename_pattern = re.compile(r'run(\d+)\.txt$')
    
    # Matches "STARTING 0"
    generation_start_pattern = re.compile(r'STARTING\s+(\d+)')
    
    # Matches ":code-size" lines. 
    # We look for the map keys specific to this line.
    # regex explanation: Look for key, whitespace, capture anything that isn't a comma, closing brace, or whitespace.
    code_size_line_check = re.compile(r':code-size\s+\{')
    mean_pattern = re.compile(r':mean\s+([^,\}\s]+)')
    median_pattern = re.compile(r':50%\s+([^,\}\s]+)')
    
    # Matches ":unique-behaviors 103"
    unique_behaviors_pattern = re.compile(r':unique-behaviors\s+(\d+)')

    rows = []

    # 2. Check directory existence
    if not os.path.isdir(folder_path):
        print(f"Error: The directory '{folder_path}' does not exist.")
        sys.exit(1)

    print(f"Scanning directory: {folder_path}...")

    # 3. Iterate over files
    files_processed_count = 0
    for entry in os.scandir(folder_path):
        if not entry.is_file():
            continue

        # Check if file matches naming scheme runN.txt
        fname_match = filename_pattern.search(entry.name)
        if fname_match:
            files_processed_count += 1
            run_number = fname_match.group(1)
            file_path = entry.path
            
            # Temporary holder for the data of the generation currently being parsed
            current_row = {}

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        # --- Check for New Generation ---
                        gen_match = generation_start_pattern.search(line)
                        if gen_match:
                            # If we were already building a row, save it before starting a new one
                            if current_row and 'generation' in current_row:
                                rows.append(current_row)
                            
                            # Initialize new row for this generation
                            current_row = {
                                'runNumber': run_number,
                                'generation': gen_match.group(1),
                                'codeSizeMean': '',
                                'codeSizeMedian': '',
                                'uniqueBehaviors': ''
                            }
                            continue
                        
                        # If we haven't hit a STARTING line yet, skip data lines
                        if not current_row:
                            continue

                        # --- Check for Code Size Statistics ---
                        if code_size_line_check.search(line):
                            # Extract Mean
                            mean_match = mean_pattern.search(line)
                            if mean_match:
                                current_row['codeSizeMean'] = mean_match.group(1)
                            
                            # Extract Median (:50%)
                            median_match = median_pattern.search(line)
                            if median_match:
                                current_row['codeSizeMedian'] = median_match.group(1)

                        # --- Check for Unique Behaviors ---
                        beh_match = unique_behaviors_pattern.search(line)
                        if beh_match:
                            current_row['uniqueBehaviors'] = beh_match.group(1)

                    # End of file: Append the very last generation row if it exists
                    if current_row and 'generation' in current_row:
                        rows.append(current_row)

            except Exception as e:
                print(f"Error reading file {entry.name}: {e}")

    # 4. Sort and Write to CSV
    # Sorting by Run Number (int) then Generation (int) for cleaner output
    rows.sort(key=lambda x: (int(x['runNumber']), int(x['generation'])))

    headers = ['runNumber', 'generation', 'codeSizeMean', 'codeSizeMedian', 'uniqueBehaviors']
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Processed {files_processed_count} files.")
    print(f"Data written to: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    # Setup command line arguments
    parser = argparse.ArgumentParser(description="Scrape GP log files to CSV.")
    parser.add_argument("folder", type=str, help="Path to the folder containing runN.txt files")
    
    args = parser.parse_args()
    parse_logs(args.folder)
