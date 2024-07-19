import argparse
import re
import sys
from collections import Counter


def get_file_content(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content

# Gets scss content
# Returns dict of sass variables with key,value = (variable, value)
def get_SASS_variables(content):
    pattern = re.compile(r"(\$[\w-]+):\s+([^;]+);", re.MULTILINE)

    # Get each sass variable
    matches = pattern.findall(content)
    result = {}
    for match in matches:
        variable = match[0].strip()
        value = match[1].strip()
        result[variable] = value
    return result

# Gets css content
# Returns dict of css variables with key,value = (variable, value)
def get_CSS_variables_helper(content):
    pattern = re.compile(r"(\--[\w-]+):\s+([^;]+);", re.MULTILINE)
    # Get each sass variable
    matches = pattern.findall(content)
    result = {}
    for match in matches:
        variable = match[0].strip()
        value = match[1].strip()
        result[variable] = value
    return result

# Gets scss content
# Returns list of css variables by id
def get_CSS_variables_by_id(content, filename):

    def clean_file(content):
        # Remove all comments [\s]*(\/\/)[^\n]*
        content = re.sub(r"[\s]*(\/\/)[^\n]*", '', content)

        # Remove all scss variables
        content = re.sub(r"\$[\w-]+[^\n]+", '', content)

        # Remove extra lines
        content = re.sub(r'\n+', '\n', content).strip()

        return content

    content = clean_file(content)
    pattern = re.compile(r'([:#.]?[\w-]+)\s*\{([^}]*)\}', re.MULTILINE)
    # Find all matches
    matches = pattern.findall(content)

    # Dictionary to store the results
    results = []

    for match in matches:
        id  = match[0].strip(':').strip("#").strip()
        properties = get_CSS_variables_helper(match[1])
        results.append({
            "filename" : filename + "." + id,
            "data" : properties
        })

    return results


def add_css_variables(css_variables, variables_to_add, filename):
    for variable, value in variables_to_add.items():
        if variable not in css_variables:
            css_variables[variable] = []
        css_variables[variable].append({
            "filename": filename,
            "value": value
        })
    return css_variables


def analyze_variables_by_file(sass_variables, outfile, isCSS=False):
    def getRowToPrint(variable, value):
        return f"{variable}: {value["value"]}; //{value["filename"]}\n"
    
    def valuesMatch(values):
        unique_values = set([elem["value"] for elem in values])
        return len(unique_values) == 1

    with open(outfile, 'w') as f:
        unique = ""
        duplicate = ""
        conflict = ""
        if(isCSS): 
            f.write(":cssVariables{\n")
        for variable, values in sass_variables.items():
            uniqueString, duplicateString, conflictString = "","",""
            if len(values) == 1:
                uniqueString = getRowToPrint(variable, values[0])
            elif(valuesMatch(values)):
                for val in values:
                    duplicateString += getRowToPrint(variable, val)
                duplicateString += f"\n"
            else:
                for val in values:
                    conflictString += getRowToPrint(variable, val)
                conflictString += f"\n"
            unique += uniqueString
            duplicate += duplicateString
            conflict += conflictString
        f.write("//Unique Values\n")
        f.write(unique)
        f.write("\n\n//Duplicate Values\n")
        f.write(duplicate)
        f.write("\n\n//Conflicting Values\n")
        f.write(conflict)
        if(isCSS): 
            f.write("}")
 
def add_sass_variables(sass_variables, variables_to_add, filename):
    for variable, value in variables_to_add.items():
        if variable not in sass_variables:
            sass_variables[variable] = []
        sass_variables[variable].append({
            "filename": filename,
            "value": value
        })
    return sass_variables

def main():
    parser = argparse.ArgumentParser(description='Process a file.')
    parser.add_argument('-f', '--file', type=str, required=True,
                        help='The file to be processed',  nargs='+')
    args = parser.parse_args()

    if args.file:
        files = args.file
    else:
        parser.print_usage()
        return sys.exit(1)

    sass_variables = {}
    css_variables = {}

    for filename in files:
        content = get_file_content(filename)
        sass_variables = add_sass_variables(sass_variables, get_SASS_variables(content), filename)
        css_variables_by_id = get_CSS_variables_by_id(content, filename)
        for variables in css_variables_by_id:
            css_variables = add_css_variables(css_variables, variables["data"], variables["filename"])

        outfile = filename + '.processed'
        with open(outfile, 'w') as f:
            f.write(content)

        print(f'Processed content written to {outfile}')
    
    analyze_variables_by_file(sass_variables, "sass_variables.scss")
    analyze_variables_by_file(css_variables, "css_variables.scss", True)


if __name__ == "__main__":
    main()
