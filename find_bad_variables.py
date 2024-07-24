import argparse
import os
import sys
import re
from pathlib import Path
import json
import time

EXCLUDE = ["base", "bourbon", "custom", "neat"]


def find_scss_files(directory):
    scss_files = []
    # Walk through all directories and files in the provided directory
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        # Filter and add .scss files to the list
        for file in files:
            if file.endswith(".scss"):
                scss_files.append(os.path.join(root, file))
    return scss_files


def extract_css_variables(filename):
    variable_pattern = r'var\((--[a-zA-Z0-9-]+)\)'
    variable_names = set()  # Use a set to avoid duplicate variable names

    with open(filename, 'r') as f:
        file_contents = f.read()

    # Find all matches for the pattern
    matches = re.findall(variable_pattern, file_contents)
    for match in matches:
        variable_names.add(match)

    return variable_names


def get_undeclared_css_variables(file_list, declared_variables):
    undeclared_variables_combined = {}
    for filename in file_list:
        filename_only = Path(filename).name
        undeclared_variables = extract_css_variables(
            filename) - declared_variables
        for variable in undeclared_variables:
            if variable not in undeclared_variables_combined:
                undeclared_variables_combined[variable] = []
            undeclared_variables_combined[variable].append(filename_only)
    return undeclared_variables_combined


def main():
    parser = argparse.ArgumentParser(description='Process SCSS files.')
    parser.add_argument('-d', '--directory', type=str, required=True, nargs='+',
                        help='The directory with scss files to be processed')
    parser.add_argument('-f', '--file', type=str, required=True,
                        help='The list of unique css variables')
    args = parser.parse_args()

    if not args.directory or not args.file:
        parser.print_usage()
        sys.exit(1)

    # Setup css variables
    css_variables = set()
    with open(args.file) as f:
        for variable in f:
            css_variables.add(variable.strip())

    # Get scss files
    scss_files = []
    for path in args.directory:
        scss_files.extend(find_scss_files(path))
    print(f'Found {len(scss_files)} scss files')

    data = get_undeclared_css_variables(scss_files, css_variables)
    print(f'Found {len(data)} undeclared variables')
    
    with open("undeclared_variables.json", "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken to complete main method: {elapsed_time:.2f} seconds")
