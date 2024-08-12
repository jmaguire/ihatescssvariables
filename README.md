# CSS Variable Management Tools

This repository provides tools to help manage and maintain CSS and SCSS variables in your codebase. Below are the instructions for using the tools included.

## Usage

### Finding Unused and Undeclared CSS Variables

```bash
python3 find_bad_variables.py -d dir1 dir2 dir3 -f file1 file2
```
- Search Directories: Searches `dir1`, `dir2`, and `dir3` for used CSS variables.
- Search Files: Searches `file1` and `file2` for declared CSS variables.
- Output Unused Variables: Lists CSS variables declared in `file1` and `file2` but not used in `dir1`, `dir2`, or `dir3`.
- Output Undeclared Variables: Lists CSS variables used in`dir1`, `dir2`, or `dir3` but not declared in `file1` or `file2`.

### Processing SCSS Variables Files
Note, in the code base this was built for we have variable declaration files for angularjs and angular.
```bash
python3 process_sass_variables.py -f file1 file2
```
- Search Files: Examines `file1` and `file2` for SCSS and CSS variable declarations.
- Output Unique Variables: Generates files `unique_css_variables.json` and `unique_sass_variables.json` listing unique variables that are only declared in one place. This can help identify potential issues, such as missing or misplaced declarations.
- Output processed scss data:  Generates file `processed_sass_variables.json` with unique, duplicate, and conflicting sass/scss variables. Unique variables can lead to issues because we often need to declare the variable for both angularjs and angular. Duplicates are expected because we often need to redeclare variables in angularjs and angular. Conflicts mean the same variable (e.g `$red-color`) is be defined differently in separate files leading to issues depending which is loaded first or issues between angularjs and angular.
- Output processed scss data:  Generates file `processed_csss_variables.json` with unique, duplicate, and conflicting sass/scss variables. Unique variables can lead to issues because we often need to declare the variable for both angularjs and angular. Duplicates are expected because we often need to redeclare variables in angularjs and angular. Conflicts take into account customer specific variables. For example, `--action-color` in `root` is seen as a different variable from `--action-color` in `#customer1`.

### Find Unused Images
```bash
python3 find_unused_images_fast.py -i assets/images images1 images2 -f files1 files2 files3
```
- Gather Image Names: Scans the directories `images1` and `images2` to gather image names.
- Scan Files for Usage: Scans the directories `files1`, `files2`, and `files3` to check which images are being used.
- Output Unused Images: Generates an unused_images.json file containing a list of unused images.

## Installation

This tool requires Python 3.x. Ensure you have it installed before proceeding.

It is recommended to use a virtual environment to manage dependencies. You can set one up and install the required dependencies with the following commands:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install ahocorasick
```
