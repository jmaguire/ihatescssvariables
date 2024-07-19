import argparse
import re
import sys
from collections import Counter

def get_file_content(filename):
    """Reads the content of a file."""
    try:
        with open(filename, 'r') as file:
            content = file.read()
        return content
    except IOError as e:
        print(f"Error reading file {filename}: {e}")
        sys.exit(1)

def get_sass_variables(content):
    """Extracts SASS variables from the content."""
    pattern = re.compile(r"(\$[\w-]+):\s+([^;]+);", re.MULTILINE)
    matches = pattern.findall(content)
    return {match[0].strip(): match[1].strip() for match in matches}

def get_css_variables(content):
    """Extracts CSS variables from the content."""
    pattern = re.compile(r"(\--[\w-]+):\s+([^;]+);", re.MULTILINE)
    matches = pattern.findall(content)
    return {match[0].strip(): match[1].strip() for match in matches}

def clean_file(content):
    """Removes comments, SASS variables, and extra lines from the content."""
    content = re.sub(r"[\s]*(\/\/)[^\n]*", '', content)
    
    content = re.sub(r"\$[\w-]+[^\n]+", '', content)
    content = re.sub(r'\n+', '\n', content).strip()
    return content

def get_css_variables_by_id(content, filename):
    """Extracts CSS variables by element ID from the content."""
    content = clean_file(content)
    pattern = re.compile(r'([:#.]?[\w-]+)\s*\{([^}]*)\}', re.MULTILINE)
    matches = pattern.findall(content)
    results = []

    for match in matches:
        id = match[0].strip(':').strip("#").strip()
        properties = get_css_variables(match[1])
        results.append({"filename": f"{filename}.{id}", "data": properties})

    return results

def add_variables(variables, new_variables, filename):
    """Adds new variables to the existing ones."""
    for variable, value in new_variables.items():
        if variable not in variables:
            variables[variable] = []
        variables[variable].append({"filename": filename, "value": value})
    return variables

def analyze_variables_by_file(variables, outfile, is_css=False):
    """Analyzes and writes unique, duplicate, and conflicting variables to a file."""
    def get_row_to_print(variable, value):
        return f"{variable}: {value['value']}; //{value['filename']}\n"
    
    def values_match(values):
        unique_values = set(value["value"] for value in values)
        return len(unique_values) == 1

    with open(outfile, 'w') as f:
        if is_css:
            f.write(":cssVariables{\n")

        unique, duplicate, conflict = "", "", ""

        for variable, values in variables.items():
            if len(values) == 1:
                unique += get_row_to_print(variable, values[0])
            elif values_match(values):
                duplicate += "".join(get_row_to_print(variable, val) for val in values) + "\n"
            else:
                conflict += "".join(get_row_to_print(variable, val) for val in values) + "\n"

        f.write("// Unique Values\n")
        f.write(unique)
        f.write("\n\n// Duplicate Values\n")
        f.write(duplicate)
        f.write("\n\n// Conflicting Values\n")
        f.write(conflict)
        
        if is_css:
            f.write("}\n")

def main():
    parser = argparse.ArgumentParser(description='Process SCSS files.')
    parser.add_argument('-f', '--file', type=str, required=True, nargs='+',
                        help='The file(s) to be processed')
    args = parser.parse_args()

    if not args.file:
        parser.print_usage()
        sys.exit(1)

    sass_variables, css_variables = {}, {}

    for filename in args.file:
        content = get_file_content(filename)
        sass_variables = add_variables(sass_variables, get_sass_variables(content), filename)
        css_variables_by_id = get_css_variables_by_id(content, filename)
        
        for variables in css_variables_by_id:
            css_variables = add_variables(css_variables, variables["data"], variables["filename"])

        print(f'Processed {filename}')

    analyze_variables_by_file(sass_variables, "sass_variables.scss")
    analyze_variables_by_file(css_variables, "css_variables.scss", is_css=True)

if __name__ == "__main__":
    main()
