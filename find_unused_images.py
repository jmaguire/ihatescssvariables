import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Set

DEFAULT_EXCLUDE_DIRS = ["bourbon", "custom", "neat"]
VARIABLE_USAGE_PATTERN = r'var\((--[a-zA-Z0-9-]+)\)'
VARIABLE_DECLARATION_PATTERN = r'(--[\w-]+):'

def collect_files_in_directory(directory: str, exclude: List[str] = DEFAULT_EXCLUDE_DIRS, extension : str = "*") -> Set[str]:
    """
    Walk through the specified directory and collect paths to all .scss files that are not in
    the excluded directories.

    Parameters:
    - directory (str or Path): The directory to search within.
    - exclude (list): A list of directory names to exclude from the search.

    Returns:
    - files: A set of files
    """

    directory_path = Path(directory)
    files = set()

    # Walk through all directories and files in the provided directory
    for path in directory_path.rglob(extension):
        if path.parent.name not in exclude:
            filename = Path(path)
            files.add(filename)
    return files

def get_used_images_by_file(filename: Path, images : Set[str]) -> Set[str]:
    """
    Returns the number of times an image is found in a file.
    
    Parameters:
    - filename (Path): Path to the file.
    - images (Set): Set of images in assets
    
    Returns:
    - used_images: Set of images used in file
    """

    used_images_file = set()
    try:
        with filename.open('r') as file:
            file_contents = file.read()
        for image in images:
            if image in file_contents:
                used_images_file.add(image)
        return used_images_file
    except IOError as e:
        print(f"Error opening or reading {filename}: {e}")
    return used_images_file

def main() -> None:
    parser = argparse.ArgumentParser(description='Process SCSS files.')
    parser.add_argument('-i', '--images', type=str, required=True, nargs='+',
                        help='The directory with scss files to be processed')
    parser.add_argument('-f', '--files', type=str, required=True, nargs='+',
                        help='File(s) where css variables are declared')
    args = parser.parse_args()

    # Get images 
    image_files = set()
    for path in args.images:
        image_files.update(collect_files_in_directory(path))
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
    
    used_images = set()

    for file in files:
        file_path = Path(file)
        used_images.update(get_used_images_by_file(file_path, images))

    print(f'Found {len(used_images)} used images')

    # unused_images = [image for image in image_counts if image_counts[image] == 0]
    # with open("unused_images.json", "w") as f:
    #     json.dump(unused_images, f, indent=4)

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken to complete main method: {elapsed_time:.2f} seconds")
