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
outputFileSuffix = "_types.edn"


# Some functions
def median(lst):
    if len(lst) <= 0:
        return False
    sorts = sorted(lst)
    length = len(lst)
    if not length % 2:
        return (sorts[length // 2] + sorts[length // 2 - 1]) / 2.0
    return sorts[length // 2]

def mean(nums):
    if len(nums) <= 0:
        return False
    return sum(nums) / float(len(nums))


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

    num_types = []
    freq_10 = []
    freq_100 = []
    freq_1000 = []
    freqs = []

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

        num_lines = 0
        num_freq_gte_10 = 0
        num_freq_gte_100 = 0
        num_freq_gte_1000 = 0

        for line in open(outputDirectory + fileName):
            if line == "]":
                break

            freq = int(line.split(" ")[-1][:-2])
            freqs.append(freq)

            num_lines += 1
            
            if freq >= 10:
                num_freq_gte_10 += 1
            if freq >= 100:
                num_freq_gte_100 += 1
            if freq >= 1000:
                num_freq_gte_1000 += 1


        num_types.append(num_lines)
        freq_10.append(num_freq_gte_10)
        freq_100.append(num_freq_gte_100)
        freq_1000.append(num_freq_gte_1000)

        i += 1

    if not csv:
        print()

    


    if csv:
        print("Problem,MedianNumTypes,MeanNumTypes,MedianTypesWithFreqGTE10,MedianTypesWithFreqGTE100,MedianTypesWithFreqGTE1000,MedianFreqs")
        print("%s,%i,%d,%i,%i,%i,%i" % (outputDirectory, median(num_types), mean(num_types), median(freq_10), median(freq_100), median(freq_1000), median(freqs)))

    else:
        print("------------------------------------------------------------")

        print(f"Median number of types per run: {median(num_types)}")
        print(f"Mean number of types per run: {mean(num_types)}")

        print("------------------------------------------------------------")





def main():
    scrape_and_print(outputDirectory, verbose, csv)


if __name__ == "__main__":
    main()
