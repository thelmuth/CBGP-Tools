#!/usr/bin/python3 

"""
Uses efficient_solution_counts.py to scrape each subdirectory of given directory.
Uses csv printing and not verbose by default
"""

import sys, os
import efficient_solution_counts, count_types

parent_dir = sys.argv[1]


problem_dirs = os.listdir(parent_dir)
problem_dirs.sort()

for prob in problem_dirs:
    full = parent_dir + prob
    efficient_solution_counts.scrape_and_print(full, False, True)

# for prob in problem_dirs:
#     full = parent_dir + prob
#     count_types.scrape_and_print(full, False, True)
