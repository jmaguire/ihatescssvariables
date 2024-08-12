Usage

python3 find_bad_variables.py -d dir1 dir2 dir3 -f file1 file2
- Will search dir1, dir2, and dir3 for for used css variables
- Will search file1 and file2 for declared css variables
- Will output unused css variables (declared in file1 and file2 but not used in dir1, dir2, and dir3)
- Will output undeclared css variables (used in dir1, dir2, and dir3 but not declared in file1 and file2)

 python3 process_sass_variables.py -f ngx_variables.scss base_variables.scss
 - takes one or more scss files
 - computes the css and scss variables
 - finds unique, duplicate, and mismatch
