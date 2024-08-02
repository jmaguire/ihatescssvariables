import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Set
import ahocorasick

DEFAULT_EXCLUDE_DIRS = ["bourbon", "custom", "neat"]
VARIABLE_USAGE_PATTERN = r'var\((--[a-zA-Z0-9-]+)\)'
VARIABLE_DECLARATION_PATTERN = r'(--[\w-]+):'

def collect_files_in_directory(directory: str, exclude: List[str] = DEFAULT_EXCLUDE_DIRS, extension : str = "*") -> List[Path]:
    """
    Walk through the specified directory and collect paths to all .scss files that are not in
    the excluded directories.

    Parameters:
    - directory (str or Path): The directory to search within.
    - exclude (list): A list of directory names to exclude from the search.

    Returns:
    - files: A set of file paths
    """

    directory_path = Path(directory)
    files = []

    # Walk through all directories and files in the provided directory
    for path in directory_path.rglob(extension):
        if path.parent.name not in exclude:
            filename = Path(path)
            files.append(filename)
    return files

def read_files_into_memory(files : List[Path]) -> Dict[str, str]:
    """
    Walk through the specified directory and collect paths to all .scss files that are not in
    the excluded directories.

    Parameters:
    - files (List): List of file paths

    Returns:
    - file dict: A dict of file name and file content
    """

    file_dict = dict()

    # Walk through all directories and files in the provided directory
    
    for file_path in files:
        try:
            with file_path.open('r') as file:
                file_contents = file.read()
                file_dict[file_path] = file_contents 
        except IOError as e:
            print(f"Error opening or reading {file_path}: {e}")
    return file_dict


def build_automaton(images):
    A = ahocorasick.Automaton()
    for idx, image in enumerate(images):
        A.add_word(image, (idx, image))
    A.make_automaton()
    return A

def get_used_images_by_files(file_dict, images):
    automaton = build_automaton(images)
    used_images = set()

    for content in file_dict.values():
        for _, (_, image) in automaton.iter(content):
            used_images.add(image)

    return used_images

def main() -> None:
    parser = argparse.ArgumentParser(description='Process SCSS files.')
    parser.add_argument('-i', '--images', type=str, required=True, nargs='+',
                        help='The directory with scss files to be processed')
    parser.add_argument('-f', '--files', type=str, required=True, nargs='+',
                        help='File(s) where css variables are declared')
    args = parser.parse_args()

    # Get images 
    image_files = []
    for path in args.images:
        a = collect_files_in_directory(path)
        image_files.extend(collect_files_in_directory(path))
    print(f'Found {len(image_files)} images files')

    images = [image.name for image in image_files]

    with open("all_images.json", "w") as f:
        json.dump(list(images), f, indent=4)

    # Get all html, ts, js, scss, css files 
    files = []
    for path in args.files:
        files.extend(collect_files_in_directory(path, extension="*.html"))
        files.extend(collect_files_in_directory(path, extension="*.ts"))
        files.extend(collect_files_in_directory(path, extension="*.js"))
        files.extend(collect_files_in_directory(path, extension="*.scss"))
        files.extend(collect_files_in_directory(path, extension="*.css"))
    
    print(f'Found {len(files)} html , js, ts, scss, css files')

    with open("all_files.json", "w") as f:
        filenames = [file.name for file in files]
        json.dump(filenames, f, indent=4)
    
    file_dict = read_files_into_memory(files)
    print(f'Read {len(file_dict.keys())} files into memory')

    used_images = get_used_images_by_files(file_dict, images)
    unused_images = set(images) - used_images
    print(f'Found {len(used_images)} used images')
    print(f'Found {len(unused_images)} used images')
    with open("unused_images.json", "w") as f:
        json.dump(list(unused_images), f, indent=4)

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken to complete main method: {elapsed_time:.2f} seconds")
