Usage

`python3 find_bad_variables.py -d dir1 dir2 dir3 -f file1 file2`
- Will search dir1, dir2, and dir3 for for used css variables
- Will search file1 and file2 for declared css variables
- Will output unused css variables (declared in file1 and file2 but not used in dir1, dir2, and dir3)
- Will output undeclared css variables (used in dir1, dir2, and dir3 but not declared in file1 and file2)

`python3 process_sass_variables.py -f file1 file2`
 - Looks at file1 and file2 where scss and css variables are declared
 - Outputs unique css and scss variables
 - Ouputs processed css file listing unique, duplicate and conflicting css variables. Unique are only declared in one place and may cause an issue for example if there's a declaration file for angularjs and angular. Duplicate means the variables are declared in multiple declaration files which is expected. Conflict means the declarations have different values. This is filtered so root.variable is not treated the same as customer.variable and only shows true conflicts (e.g root.variable has two separate values)
 - Ouputs processed scss file listing unique, duplicate and conflicting scss variables. Unique are only declared in one place and may cause an issue for example if there's a declaration file for angularjs and angular. Duplicate means the variables are declared in multiple declaration files which is expected. Conflict means the declarations have different values like $red-color is defined one way in one file and another in another file

