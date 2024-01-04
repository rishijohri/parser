from pprint import pprint
from PyQt5.QtWidgets import QApplication, QFileDialog
from display_view.choice_view import choose_elements
from display_view.display_view import display_text
from functions.defnition import get_definition
from functions.parse_mk3 import read_script
app = QApplication([])


if __name__ == "__main__":

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

    display_text("Welcome to the SQL Query Parser\n Choose File to Parse")
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Open file", "", "All files (*.*)"
    )

    print("after file read")
    with open(file_path, "r"):
        tables = read_script(file_path, default_test_cases)
        table_names = []
        for table in tables:
            table_names.append(table.name)
        print(table_names)
    if table_names != []:
        table_name = choose_elements(
            table_names, "Table Selection", "Select Table", allow_multiple=False
        )[0]

        column_names = []
        for table in tables:
            if table.name == table_name:
                for column in table.columns:
                    column_names.append(column.name)
        column_names = choose_elements(
            column_names, "Column Selection", "Select Column", allow_multiple=True
        )
        print(table_name)
        print(column_names)
        definition, definition_str = get_definition(
            table_name, column_names, tables
        )
        to_print = display_text(definition_str)
        if to_print:
            # write defintion string in file
            with open("results/definition.hql", "w") as f:
                f.write(definition_str)
