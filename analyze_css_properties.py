import argparse
import json
import re
import time
import sys
from pathlib import Path
from collections import Counter
from typing import List, Tuple

DEFAULT_EXCLUDE_DIRS = ["bourbon", "custom", "neat"]
ALL_CSS_VALUES = r'^\s*([\w-]*):\s*([^;]*)'
CSS_VALUES_BY_CLASS = r'\s*([\w-]*):\s*([^;]*)'
CLASS_OPENING = r'[^}]*\{\n'
CLASS_CLOSING = r'\s*\}'
DELIMITER = '||'

def collect_style_files_in_directory(directory: str, exclude: List[str] = DEFAULT_EXCLUDE_DIRS) -> List[str]:
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
    for path in directory_path.rglob('*.css'):
        if path.parent.name not in exclude:
            scss_files.append(str(path))
    return scss_files

def extract_css_properties_and_values_by_file(filename: Path, pattern: re.Pattern) -> List[Tuple[str, str]]:
    """
    Read the contents of a file and find all matches based on a regex pattern.
    
    Parameters:
    - filename (Path): Path to the file.
    - pattern (Pattern): Compiled regex pattern to match against.
    
    Returns:
    - result: list of (css_variable, css_value) pairs
    """
    result = []

    try:
        with filename.open('r') as file:
            file_contents = file.read()
        return re.findall(pattern, file_contents, re.MULTILINE)
    except IOError as e:
        print(f"Error opening or reading {filename}: {e}")
    return result

def process_class_properties(properties_by_class: List[str], pattern: re.Pattern = CSS_VALUES_BY_CLASS) -> List[str]:
    result = []
    for properties in properties_by_class:
        matches = re.findall(pattern, properties, re.MULTILINE)
        matches = [elem[0].strip() + ':' +elem[1].strip() for elem in matches]
        result.extend([';'.join(matches)])
    result = sorted(result)
    return result

def extract_class_properties_by_file(filename: Path) -> List[str]:
    """
    Read the contents of a file and find all matches based on a regex pattern.
    
    Parameters:
    - filename (Path): Path to the file.
    - pattern (Pattern): Compiled regex pattern to match against.
    
    Returns:
    - result: list of all css propteries separated by class
    """
    result = []
    if filename.suffix == ".css":
        return []

    try:
        with filename.open('r') as file:
            file_contents = file.read()
        result = re.sub(CLASS_OPENING, "\\n" + DELIMITER, file_contents, 0, re.MULTILINE)
        result = re.sub(CLASS_CLOSING, DELIMITER + "\\n", result, 0, re.MULTILINE)
        result = ' '.join(result.split())
        result = [elem.strip() for elem in result.split(DELIMITER) if elem.strip() != ""]
        result = process_class_properties(result)
        return result
    except IOError as e:
        print(f"Error opening or reading {filename}: {e}")
    return result

def get_all_css_properties_and_values(file_list: List[str]) -> List[Tuple[str, str]]:
    """
    Identify CSS variables that are used but not declared within the provided files.
    
    Parameters:
    - file_list (list): A list of file paths to check.
    - declared_variables (set): A set of globally declared CSS variables.
    
    Returns:
    - tuple of each property and value
    """
    css_properties = []
    for filename in file_list:
        file_path = Path(filename)
        css_properties.extend(extract_css_properties_and_values_by_file(file_path, ALL_CSS_VALUES))
    return css_properties

def get_all_class_properties(file_list: List[str]) -> List[List[str]]:
    """
    Identify CSS variables that are used but not declared within the provided files.
    
    Parameters:
    - file_list (list): A list of file paths to check.
    - declared_variables (set): A set of globally declared CSS variables.
    
    Returns:
    - esult: list of all css propteries separated by class
    """
    css_class_properties= []
    for filename in file_list:
        file_path = Path(filename)
        css_class_properties.extend(extract_class_properties_by_file(file_path))
    return css_class_properties

def main() -> None:
    parser = argparse.ArgumentParser(description='Process SCSS files.')
    parser.add_argument('-d', '--directory', type=str, required=True, nargs='+',
                        help='The directory with scss files to be processed')

    args = parser.parse_args()
    
    # Get scss and css files
    scss_files = []
    for path in args.directory:
        scss_files.extend(collect_style_files_in_directory(path))
    print(f'Found {len(scss_files)} scss files')
    
    class_properties = get_all_class_properties(scss_files)
    print(f'Found {len(class_properties)} propertes')

    updated_class_properties = [[item, count] for item, count in Counter(class_properties).items()]
    updated_class_properties = sorted(updated_class_properties, key=lambda x: x[-1], reverse=True)
    
    with open("class_properties.json", "w") as f:
        json.dump(updated_class_properties, f, indent=4)

    properties = get_all_css_properties_and_values(scss_files)
    updated_properties = [item + (count,) for item, count in Counter(properties).items()]
    updated_properties = sorted(updated_properties, key=lambda x: x[-1], reverse=True)

    print(f'Found {len(updated_properties)} propertes')
    
    with open("properties.json", "w") as f:
        json.dump(updated_properties, f, indent=4)

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken to complete main method: {elapsed_time:.2f} seconds")
