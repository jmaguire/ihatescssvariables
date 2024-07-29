import argparse
import json
import re
import sys
import time
import sysconfig
from pathlib import Path
from typing import Dict, List, Set

DEFAULT_EXCLUDE_DIRS = ["bourbon", "custom", "neat"]
VARIABLE_USAGE_PATTERN = r'var\((--[a-zA-Z0-9-]+)\)'
VARIABLE_DECLARATION_PATTERN = r'(--[\w-]+):'

def collect_scss_files_in_directory(directory: str, exclude: List[str] = DEFAULT_EXCLUDE_DIRS) -> List[str]:
    """
    Walk through the specified directory and collect paths to all .scss files that are not in
    the excluded directories.

    Parameters:
    - directory (str or Path): The directory to search within.
    - exclude (list): A list of directory names to exclude from the search.

    Returns:
    - list: A list of paths to .scss files as strings.
    """

    directory_path = Path(directory)
    scss_files = []

    # Walk through all directories and files in the provided directory
    for path in directory_path.rglob('*.scss'):
        if path.parent.name not in exclude:
            scss_files.append(str(path))
    return scss_files

def extract_matches_as_set(filename: Path, pattern: re.Pattern) -> Set[str]:
    """
    Read the contents of a file and find all matches based on a regex pattern.
    
    Parameters:
    - filename (Path): Path to the file.
    - pattern (Pattern): Compiled regex pattern to match against.
    
    Returns:
    - set: A set of unique matches found in the file.
    """
    result = set()
    try:
        with filename.open('r') as file:
            file_contents = file.read()
        return set(re.findall(pattern, file_contents))

    except IOError as e:
        print(f"Error opening or reading {filename}: {e}")
    return result

def extract_css_variables(filename: Path) -> Set[str]:
    """
    Extract all CSS variable usages formatted as var(--variable-name) from a given file.
    
    Parameters:
    - filename (path): Path to the file.
    
    Returns:
    - set: A set of used CSS variable names.
    """
    return extract_matches_as_set(filename, VARIABLE_USAGE_PATTERN)

def extract_css_variable_declarations(filename: Path) -> Set[str]:
    """
    Extract all CSS variable declarations formatted as --variable-name: from a given file.
    
    Parameters:
    - filename (path): Path to the file.
    
    Returns:
    - set: A set of declared CSS variable names.
    """
    return extract_matches_as_set(filename, VARIABLE_DECLARATION_PATTERN)

def get_undeclared_css_variables(file_list: List[str], declared_variables: Set[str]) -> Dict[str, List[str]]:
    """
    Identify CSS variables that are used but not declared within the provided files.
    
    Parameters:
    - file_list (list): A list of file paths to check.
    - declared_variables (set): A set of globally declared CSS variables.
    
    Returns:
    - dict: A dictionary with undeclared variables as keys and the list of files they appear in as values.
    """
    undeclared_variables_combined = {}
    for filename in file_list:
        file_path = Path(filename)
        undeclared_variables = extract_css_variables(file_path) - declared_variables
        for variable in undeclared_variables:
            if variable not in undeclared_variables_combined:
                undeclared_variables_combined[variable] = []
            undeclared_variables_combined[variable].append(file_path.name)
    return undeclared_variables_combined

def get_unused_css_variables(file_list: List[str], declared_variables: Set[str]) -> List[str]:
    """
    Identify declared CSS variables that are not used in any of the provided files.
    
    Parameters:
    - file_list (list): A list of file paths where to search for variable usage.
    - declared_variables (set): A set of all declared CSS variables.
    
    Returns:
    - list: A list of unused variables.
    """
    # set of variables that are never used
    used_variables_combined = set()
    for filename in file_list:
        file_path = Path(filename)
        used_variables_combined.update(extract_css_variables(file_path))
    return declared_variables - used_variables_combined


def main() -> None:
    parser = argparse.ArgumentParser(description='Process SCSS files.')
    parser.add_argument('-d', '--directory', type=str, required=True, nargs='+',
                        help='The directory with scss files to be processed')
    parser.add_argument('-f', '--files', type=str, required=True, nargs='+',
                        help='File(s) where css variables are declared')
    args = parser.parse_args()

    # Get declared css varibles
    declared_variables = set()
    for filename in args.files:
      file_path = Path(filename)
      declared_variables.update(extract_css_variable_declarations(file_path))

    with open("declared_variables.json", "w") as f:
        declared_variables_list = sorted(list(declared_variables))
        json.dump(declared_variables_list, f, indent=4)
    
    # Get scss files
    scss_files = []
    for path in args.directory:
        scss_files.extend(collect_scss_files_in_directory(path))
    print(f'Found {len(scss_files)} scss files')


    undeclared = get_undeclared_css_variables(scss_files, declared_variables)
    files = {file for var, files in undeclared.items() for file in files}
    
    print(f'Found {len(undeclared)} undeclared variables')
    print(f'Found across {len(files)} files')
    
    with open("undeclared_variables.json", "w") as f:
        json.dump(undeclared, f, indent=4)
    
    unused = list(get_unused_css_variables(scss_files, declared_variables))
    print(f'Found {len(unused)} unused variables')
    with open("unused_variables.json", "w") as f:
        json.dump(unused, f, indent=4)


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken to complete main method: {elapsed_time:.2f} seconds")
