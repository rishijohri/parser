from typing import List, Tuple
from classes.Table import Table

def get_table_columns(table_name, tables):
    columns = []
    for table in tables:
        if table.name == table_name:
            columns = [col.name for col in table.columns]
            break
    return columns

def get_follow_sources(
    table_name, column_names=[], tables: List[Table]=[]
) -> Tuple[list, list, Table, list]:
    source_columns = []
    source_tables = []
    match_table = Table()
    match_column = []
    # print("column_names ", column_names)
    for table in tables:
        if (
            table.name == table_name
            or (table.source_database + "." + table.name) == table_name
        ):
            # print("table found ", table.name)
            for column in table.columns:
                # print("\t column name ", column.name)
                if column.name in column_names:
                    match_table = table
                    match_column.append(column)
                    source_columns.extend(source_column for source_column in column.source_columns if source_column.real_column)
                    # Get Filter source columns
                    if table.filters != None:
                        source_columns.extend(table.filters.source_columns)

                    # distinct tables used
                    for source_column in source_columns:
                        source_tables.append(source_column.source_table)

                    source_tables = list(set(source_tables))
                    # Get Join source columns
                    for join in table.joins:
                        if join.name in source_tables:
                            for source_column in join.source_columns:
                                source_columns.append(source_column)

                    source_columns = list(set(source_columns))
    
    # print("source_columns ", source_columns)
    # print("source_tables ", source_tables)
    # print("match_table ", match_table.name)
    # print("match_column ", [match_column.name for match_column in match_column])
    return source_columns, source_tables, match_table, match_column


def get_definition(table_name, column_name, tables, print_result=False):

    table_recreates = []
    source_columns = []
    source_tables = []

    source_columns, source_tables, current_table, current_columns = get_follow_sources(
        table_name, column_name, tables
    )
    assert current_table.name != "Default.Unset"

    table_recreate = current_table.recreate_query(current_columns)
    table_recreates.append(table_recreate)

    while len(source_tables) > 0:
        table_name = source_tables.pop()
        column_names = []
        for column in source_columns:
            if column.source_table == table_name:
                column_names.append(column.name)
        # print(table_name, column_names)
        (
            source_columns_new,
            source_tables_new,
            current_table,
            current_columns,
        ) = get_follow_sources(table_name, column_names, tables)
        # print(current_table)
        if current_table != None and current_table.name != "Unset":
            # print("current_table ", current_table.name)
            # print("source_tables_new ", source_tables_new)
            table_recreate = current_table.recreate_query(current_columns)
            for table in source_tables_new:
                if table not in source_tables:
                    source_tables.append(table)
            for column in source_columns_new:
                if column not in source_columns:
                    source_columns.append(column)
            table_recreates.append(table_recreate)

    table_recreates.reverse()
    def_str = ""
    for table_recreate in table_recreates:
        if print_result:
            print(table_recreate)
        def_str += table_recreate + "\n"
    return table_recreates, def_str
