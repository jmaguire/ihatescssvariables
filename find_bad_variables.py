import argparse
import os
import sys
import re
import json
import time
from pathlib import Path

EXCLUDE = ["base", "bourbon", "custom", "neat"]


def collect_scss_files_in_directory(directory):
    """
    Walk through all directories and files in the provided directory,
    filtering out directories listed in EXCLUDE, and collect all .scss files.
    """
    directory_path = Path(directory)
    scss_files = []

    # Walk through all directories and files in the provided directory
    for path in directory_path.rglob('*.scss'):
        if path.parent.name not in EXCLUDE:
            scss_files.append(str(path))

    return scss_files

def extract_css_variables(filename):
    """
    Extract all CSS variable usages formatted as var(--variable-name) from a given file.
    """
    variable_pattern = r'var\((--[a-zA-Z0-9-]+)\)'
    variable_names = set()  # Use a set to avoid duplicate variable names

    with open(filename, 'r') as f:
        file_contents = f.read()

    return set(re.findall(variable_pattern, file_contents))

def extract_css_variable_declarations(filename):
    """
    Extract all CSS variable declarations formatted as --variable-name: from a given file.
    """
    variable_pattern = r'(--[\w-]+):'
    variable_names = set()  # Use a set to avoid duplicate variable names

    with open(filename, 'r') as f:
        file_contents = f.read()

    # Find all matches for the pattern
    return set(re.findall(variable_pattern, file_contents))

def get_undeclared_css_variables(file_list, declared_variables):
    """
    Create a dictionary of undeclared variables with the value cooresponding to the files
    where the variable is used.
    """
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

def get_unused_css_variables(file_list, declared_variables):
    """
    Create a list of unused variables.
    """
    # set of variables that are never used
    used_variables_combined = set()
    for filename in file_list:
        filename_only = Path(filename).name
        used_variables_combined = used_variables_combined.union(extract_css_variables(filename))
    return list(declared_variables - used_variables_combined)


def main():
    parser = argparse.ArgumentParser(description='Process SCSS files.')
    parser.add_argument('-d', '--directory', type=str, required=True, nargs='+',
                        help='The directory with scss files to be processed')
    parser.add_argument('-f', '--files', type=str, required=True, nargs='+',
                        help='File(s) where css variables are declared')
    args = parser.parse_args()

    if not args.directory or not args.files:
        parser.print_usage()
        sys.exit(1)

    # Setup css variables
    css_variables = set()
    for filename in args.files:
      with open(filename) as f:
          css_variables.update(extract_css_variable_declarations(filename))
  
    # Get scss files
    scss_files = []
    for path in args.directory:
        scss_files.extend(collect_scss_files_in_directory(path))
    print(f'Found {len(scss_files)} scss files')


    undeclared = get_undeclared_css_variables(scss_files, css_variables)
    files = {file for var, files in undeclared.items() for file in files}
    
    print(f'Found {len(undeclared)} undeclared variables')
    print(f'Found across {len(files)} files')
    
    with open("undeclared_variables.json", "w") as f:
        json.dump(undeclared, f, indent=4)
    
    unused = get_unused_css_variables(scss_files, css_variables)
    print(f'Found {len(unused)} unused variables')
    with open("unused_variables.json", "w") as f:
        json.dump(unused, f, indent=4)


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken to complete main method: {elapsed_time:.2f} seconds")
