from functions.parse_mk3 import read_script
from functions.defnition import get_definition

default_test_cases = {
    "column": False,
    "case_column": False,
    "condition": False,
    "create": False,
    "join": False,
    "table": False,
    "query": False,
    "print_query": False,
    "print_result": False,
}

tables = []
file_path = "code/single_query.sql"
to_print = True
table_name = "source2"
column_name = ["column4"]
with open(file_path, "r"):
    print("reading file")
    tables = read_script(file_path, default_test_cases)
definition, definition_str = get_definition(table_name, column_name, tables)
print(definition_str)
if to_print:
    file_name = "def_"
    file_name += "_".join(column_name)
    file_name += ".hql"
    # write defintion string in file
    with open(f"results/{file_name}", "w") as f:
        f.write(definition_str)