#!/usr/bin/python3

## Can take 0, 1, or 2 command line arguments.
## If 0 arguments, uses variable set to outputDirectory as the location of the output files.
## First argument is the location of the output files, and overrides a variable defined below.
## Second argument can be "brief" in order to not output individual run success/fail, and only output aggregate statistics
## Second argument can alternatively be "csv" in order to print one line per problem, ready to paste into a spreadsheet

import os, sys

verbose = True
if (len(sys.argv) >= 2 and sys.argv[1] == "brief") or \
        (len(sys.argv) >= 3 and sys.argv[2] == "brief"):
    verbose = False

csv = False
if (len(sys.argv) >= 2 and sys.argv[1] == "csv") or \
        (len(sys.argv) >= 3 and sys.argv[2] == "csv"):
    csv = True
    verbose = False


# Set these before running:

#outputDirectory = "Results/wc-new-experiments/UMAD/wc"



# This allows this script to take a command line argument for outputDirectory
if len(sys.argv) > 1 and sys.argv[1] != "brief" and sys.argv[1] != "csv":
    outputDirectory = sys.argv[1]

outputFilePrefix = "run"
outputFileSuffix = ".txt"


# Some functions
def median(lst):
    if len(lst) <= 0:
        return False
    sorts = sorted(lst)
    length = len(lst)
    if not length % 2:
        return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
    return sorts[length / 2]

def mean(nums):
    if len(nums) <= 0:
        return False
    return sum(nums) / float(len(nums))

def reverse_readline(filename):
    with open(filename, 'r') as fheader:  
        for line in reversed(fheader.readlines()):  
            yield line


def scrape_and_print(outputDirectory, verbose, csv):
    """Scrapes and prints from outputDirectory"""

    i = 0

    if outputDirectory[-1] != '/':
        outputDirectory += '/'
    dirList = os.listdir(outputDirectory)

    if not csv:
        print()
        print("           Directory of results:")
        print(outputDirectory)

    finished_runs = []
    failed_runs = []
    solution_runs = []
    generalized_runs = []

    # Main loop over files
    while (outputFilePrefix + str(i) + outputFileSuffix) in dirList:
        if not csv:
            sys.stdout.write("%4i" % i)
            sys.stdout.flush()
            if i % 25 == 24:
                print()

        runs = i + 1 # After this loop ends, runs should be correct
        fileName = (outputFilePrefix + str(i) + outputFileSuffix)

        if os.path.getsize(outputDirectory + fileName) == 0:
            i += 1
            continue

        for line in reverse_readline(outputDirectory + fileName):

            if "SOLUTION GENERALIZED" in line:
                finished_runs.append(i)
                solution_runs.append(i)
                generalized_runs.append(i)
                break

            if "SOLUTION FOUND" in line:
                finished_runs.append(i)
                solution_runs.append(i)
                break

            if "SOLUTION NOT FOUND" in line:
                finished_runs.append(i)
                failed_runs.append(i)
                break

        i += 1

    if not csv:
        print()


    not_done = []
    for j in range(i):
        if j not in finished_runs:
            not_done.append(j)

    if csv:
        print("%s,%i,%i,%i" % (outputDirectory,
                                  len(finished_runs), 
                                  len(solution_runs),
                                  len(generalized_runs)))

    else:
        print("------------------------------------------------------------")

        print("Number of finished runs:            %4i" % len(finished_runs))
        print("Solutions found:                    %4i" % len(solution_runs))
        print("Zero error on test set:             %4i" % len(generalized_runs))

        print("------------------------------------------------------------")

        print("Not done yet: ", end="")
        for run_i in not_done:
            print("%i," % run_i, end="")
        print()

        print("------------------------------------------------------------")




def main():
    scrape_and_print(outputDirectory, verbose, csv)


if __name__ == "__main__":
    main()
