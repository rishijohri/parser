from functions.parse_mk3 import read_script
from functions.defnition import get_definition, get_table_columns
from pprint import pprint
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
to_print = True
run_default = True
tables = []
file_path = "code/single_query.sql"
table_name = "source2"
column_name = ["colmax"]
with open(file_path, "r"):
    print("reading file")
    tables = read_script(file_path, default_test_cases)
if run_default:
    definition, definition_str = get_definition(table_name, column_name, tables)
    print(definition_str)
    if to_print:
        file_name = "def_"
        file_name += "_".join(column_name)
        file_name += ".hql"
        # write defintion string in file
        with open(f"results/{file_name}", "w") as f:
            f.write(definition_str)
else:
    definition_str = "No Definition to Show (use run command to get definition)"
while True:
    command = input("Enter command: \n").strip()
    if command =='exit':
        break
    elif command == 'config':
        print("default_test_cases:")
        pprint(default_test_cases)
        print(f"table name: {table_name}")
        print(f"column name: {column_name}")
    elif command == "show tables":
        table_names = [table.name for table in tables]
        print(table_names)
    elif command == 'change table':
        table_name = input("Enter table name: \n").strip()
    elif command == 'show columns':
        available_columns = get_table_columns(table_name, tables)
        print(available_columns)
    elif command == 'change column':
        column_name = input("Enter column name: \n").strip().split(',')
        column_name = [column.strip() for column in column_name]
    elif command =="run":
        try:
            definition, definition_str = get_definition(table_name, column_name, tables)
            if to_print:
                file_name = "def_"
                file_name += "_".join(column_name)
                file_name += ".hql"
                # write defintion string in file
                with open(f"results/{file_name}", "w") as f:
                    f.write(definition_str)
        except Exception as e:
            print(e)
            print("Error in getting definition")
    elif command == "print":
        print(definition_str)
    else:
        print("Invalid command")
    
