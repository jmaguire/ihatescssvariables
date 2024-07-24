Usage

python3 find_bad_variables.py -d path_to_scss_files path_to_scss_files -f path_to_css_variable_declaration
- Note you can configure EXCLUDE
- d takes one or more directories
- f takes one or more declaration files

 python3 process_sass_variables.py -f ngx_variables.scss base_variables.scss
 - takes one or more scss files
 - computes the css and scss variables
 - finds unique, duplicate, and mismatch
