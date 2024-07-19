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
    def replacer(match):
        return f"|{match.group(1).strip()}|"
    """Removes comments, SASS variables, and extra lines from the content."""
    # Remove all comments [\s]*(\/\/)[^\n]*
    content = re.sub(r"[\s]*(\/\/)[^\n]*", '', content)
    # Remove all extra lines
    content = re.sub(r'\n+', '\n', content).strip()
    # Remove all scss variables
    content = re.sub(r"\s*\$[\w-]+:\s*[^;]+;", '', content)
    # Remove extra lines
    content = re.sub(r'\n+', '\n', content).strip()
    pattern = r'^\s*[#:](.*)\{$'
    #replace :root or #bv with ##element##
    content = re.sub(pattern, replacer, content, flags=re.MULTILINE)
    #replace terminating } with ##
    pattern = r'^\s*\}\s*$'
    content = re.sub(pattern, '|', content, flags=re.MULTILINE)
    return content

def get_css_variables_by_id(content, filename):
    """Extracts CSS variables by element ID from the content."""
    content = clean_file(content)
    pattern = re.compile(r"\|([\w-]+)\s*\|([^\|]*)\|", re.MULTILINE)
    
    # pattern = re.compile(r":(\w+)\s*\{([^\n\n]*)}", re.MULTILINE) need to fix to account for variables 
    matches = pattern.findall(content)
    results = []

    for match in matches:
        id = match[0].strip(':').strip("#").strip()
        properties = get_css_variables(match[1])
        results.append({"filename": f"{filename}", "id" : f"{id}", "data": properties})
    return results

def add_variables(variables, new_variables, filename, id="root"):
    """Adds new variables to the existing ones."""
    for variable, value in new_variables.items():
        if variable not in variables:
            variables[variable] = []
        variables[variable].append({"filename": filename, "value": value, "id":id})
    return variables

def extract_values_by_index(array, indices):
    extract = [elem for i, elem in enumerate(array) if i in indices]
    return extract

def analyze_variables_by_file(variables, outfile, is_css=False):
    """Analyzes and writes unique, duplicate, and conflicting variables to a file."""
    def get_row_to_print(variable, value):
        if(is_css):
            return f"{variable}: {value['value']}; //{value['filename']}.{value['id']}\n"
        return f"{variable}: {value['value']}; //{value['filename']}\n"
    
    def get_duplicates_by_value(values):
        value_counts = Counter([elem['value'] for elem in values])
        return {value for value, count in value_counts.items() if count > 1}
    
    def get_conflicts_by_id(values):
        id_values = {}
        conflicts = set()
        for obj in values:
            id, value = obj['id'], obj['value']
            if id in id_values and id_values[id] != value:
                conflicts.add(id)
            id_values[id] = value
        return conflicts

    with open(outfile, 'w') as f:
        if is_css:
            f.write(":cssVariables{\n")

        unique, duplicate, conflict, confused = "", "", "", ""

        for variable, values in variables.items():
            if(variable == "$green"):
                print(values)
            ## There is only one defined value
            if len(values) == 1:
                unique += get_row_to_print(variable, values[0])
            else:
                duplicate_values = get_duplicates_by_value(values)
                duplicate_indices = [i for val in duplicate_values for i, obj in enumerate(values) if obj['value'] == val]
                duplicates = extract_values_by_index(values, duplicate_indices)

                ## Get duplicate values
                if len(duplicates) >= 1:
                    duplicate += "".join(get_row_to_print(variable, val) for val in duplicates) + "\n"

                conflict_values = get_conflicts_by_id(values)
                conflict_indices = [i for val in conflict_values for i, obj in enumerate(values) if obj['id'] == val]
                conflicts = extract_values_by_index(values, conflict_indices)
                
                ## Get conflicts
                if len(conflicts) >= 1:
                    conflict += "".join(get_row_to_print(variable, val) for val in conflicts) + "\n"

                conflict_or_dupe = list(set(duplicate_indices).symmetric_difference(set(conflict_indices)))
                remainder = [elem for i, elem in enumerate(values) if i not in conflict_or_dupe]

                ## Get confused
                if len(remainder) >= 1:
                    confused += "".join(get_row_to_print(variable, val) for val in remainder) + "\n"


        f.write("// Unique Values\n")
        f.write(unique)
        f.write("\n\n// Duplicate Values\n")
        f.write(duplicate)
        f.write("\n\n// Conflicting Values\n")
        f.write(conflict)
        f.write("\n\n// Confused Values\n")
        f.write(confused)
        
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
            css_variables = add_variables(css_variables, variables["data"], variables["filename"], variables["id"])

        print(f'Processed {filename}')

    analyze_variables_by_file(sass_variables, "processed_sass_variables.scss")
    analyze_variables_by_file(css_variables, "processed_css_variables.scss", is_css=True)

if __name__ == "__main__":
    main()
