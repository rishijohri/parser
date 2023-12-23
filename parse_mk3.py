import pyparsing as pp
import os
from types import SimpleNamespace
from pprint import pprint
from PyQt5.QtWidgets import QApplication, QFileDialog
from display_view.choice_view import choose_elements
from display_view.display_view import display_text
from typing import Tuple, List
from classes.constants import special_words, special_words_list, special_char_name
from classes.BaseColumn import BaseColumn
from classes.Condition import Condition
from classes.ConditionGroup import ConditionGroup
from classes.Column import Column
from classes.Join import Join
from classes.Table import Table
import test_cases


def dict_to_obj(d):
    if isinstance(d, list):
        return [dict_to_obj(v) for v in d]
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                d[k] = dict_to_obj(v)
        return SimpleNamespace(**d)
    return d

app = QApplication([])
# Create class to store information about Column
all_tables = []
all_columns = []


def query_type_check(queries):
    """
    Gets an list of queries and returns a list of query which are create table queries
    """
    create_queries = []
    for query in queries:
        if query[:6].upper() == "CREATE":
            create_queries.append(query)
    return create_queries


# write function to seperate different queries from a string
def separate_queries(queries):
    return [query.strip() + " ;" for query in queries.split(";") if query.strip()]


# write parse_create_query function here using pyparsing
def parse_create_query(query):
    # define grammer
    # ALias Grammar
    allowed_name: pp.ParserElement = pp.And(
        [special_words, pp.Word(pp.alphanums + special_char_name)]
    )
    assert isinstance(allowed_name, pp.ParserElement)

    column_alias = pp.Optional(
        pp.Group(pp.CaselessKeyword("AS") + allowed_name)
    ).setResultsName("column_alias")

    table_alias = pp.Optional(
        pp.Optional(pp.CaselessKeyword("AS")) + allowed_name
    ).setResultsName("table_alias")

    multi_argu_func = (
        pp.CaselessKeyword("SUM")
        | pp.CaselessKeyword("AVG")
        | pp.CaselessKeyword("COUNT")
        | pp.CaselessKeyword("MIN")
        | pp.CaselessKeyword("MAX")
        | pp.CaselessKeyword("CONCAT")
        | pp.CaselessKeyword("SUBSTR")
        | pp.CaselessKeyword("TRIM")
        | pp.CaselessKeyword("COALESCE")
        | pp.CaselessKeyword("CAST")
        | pp.CaselessKeyword("DATE_FORMAT")
        | pp.CaselessKeyword("ADD_MONTHS")
    )
    assert isinstance(multi_argu_func, pp.ParserElement)

    data_types = (
        pp.CaselessKeyword("INT")
        | pp.CaselessKeyword("FLOAT")
        | pp.CaselessKeyword("DOUBLE")
        | pp.CaselessKeyword("DATE")
        | pp.CaselessKeyword("TIMESTAMP")
        | pp.CaselessKeyword("STRING")
        | pp.CaselessKeyword("VARCHAR")
        | pp.CaselessKeyword("CHAR")
    )
    assert isinstance(data_types, pp.ParserElement)
    # Base column Grammar (Column can have aggregation function)
    column = pp.Forward()
    base_column = pp.Group(
        pp.Optional(allowed_name.setResultsName("source") + pp.Suppress("."))
        + allowed_name.setResultsName("name")
        + pp.Optional(pp.Word("+-*/").setResultsName("operator"))
    )

    multi_argu_column: pp.ParserElement = pp.Group(
        multi_argu_func.setResultsName("aggregate_func")
        + pp.Suppress("(")
        + column.setResultsName("col_argument")
        + pp.Optional(
            pp.Char(",")
            + pp.delimitedList(allowed_name, delim=",").setResultsName("arguments")
        )
        + pp.Suppress(")")
        + pp.Optional(pp.Word("+-*/").setResultsName("operator"))
    )

    column << pp.MatchFirst(  # type: ignore
        [base_column, multi_argu_column]
    )
    column = pp.OneOrMore(column).setResultsName("definition")

    # print("Column Test")
    # for test in test_cases.column_tests:
    #     print(test)
    #     print(column.parseString(test))

    # Conditions grammer
    delimiter = pp.MatchFirst([pp.CaselessKeyword("AND"), pp.CaselessKeyword("OR")])
    comparator = pp.Word("=<>") | pp.CaselessKeyword("LIKE") | pp.CaselessKeyword("IS") | pp.CaselessKeyword("NOT LIKE")
    assert isinstance(comparator, pp.ParserElement)
    equality_condition = pp.Group(
        pp.And(
            [
                column.setResultsName("LHS"),
                comparator.setResultsName("comparator"),
                column.setResultsName("RHS"),
                pp.Optional(delimiter).setResultsName("delimiter"),
            ]
        )
    )
    in_comparator = pp.CaselessKeyword("IN") | pp.CaselessKeyword("NOT IN")
    assert isinstance(in_comparator, pp.ParserElement)
    
    in_condition_clause = pp.Group(
        pp.And(
            [
                column.setResultsName("LHS"),
                in_comparator.setResultsName("comparator"),
                pp.Group(
                    pp.And(
                        [
                            pp.Suppress("("),
                            pp.delimitedList(allowed_name),
                            pp.Suppress(")"),
                        ]
                    )
                ).setResultsName("RHS"),
                pp.Optional(delimiter).setResultsName("delimiter"),
            ]
        )
    )
    condition_clause = pp.MatchFirst([equality_condition, in_condition_clause])

    condition_group = pp.Forward()
    condition_group << pp.OneOrMore(  # type: ignore
        pp.MatchFirst(
            [
                condition_clause,
                pp.Group(pp.Literal("(")
                + condition_group
                + pp.Literal(")")
                + pp.Optional(delimiter).setResultsName("delimiter")),
            ]
        )
    ).setResultsName("condition_group")

    # print("Condition Test")
    # for test in test_cases.all_condition_tests:
    #     print(test)
    #     print(condition_group.parseString(test))

    case_column = pp.Forward()
    # Case statement grammer
    case_column << pp.Group(  # type: ignore
        pp.Optional(pp.Keyword("("))
        + pp.CaselessKeyword("CASE")
        + pp.OneOrMore(
            pp.Group(
                pp.CaselessKeyword("WHEN")
                + condition_group
                + pp.CaselessKeyword("THEN")
                + pp.MatchFirst([column, case_column]).setResultsName("result")
            ).setResultsName("case")
        ).setResultsName("cases")
        + pp.Optional(
            pp.Group(
                pp.CaselessKeyword("ELSE") + pp.MatchFirst([column, case_column])
            ).setResultsName("else_case")
        )
        + pp.CaselessKeyword("END")
        + pp.Optional(pp.Keyword(")"))
    ).setResultsName("case_column")

    # print("Case Column Test")
    # for test in test_cases.case_column_tests:
    #     print(test)
    #     pprint(case_column.parseString(test).asDict())
    #     print(case_column.parseString(test).case_column.case.result)

    # Create Clause grammer
    create_clause = pp.Group(
        pp.And(
            [
                pp.CaselessKeyword("CREATE"),
                pp.CaselessKeyword("TABLE"),
                pp.Optional(pp.CaselessKeyword("IF NOT EXISTS")),
                pp.Optional(allowed_name.setResultsName("source") + pp.Suppress(".")),
                allowed_name.setResultsName("table_name"),
                pp.Optional(
                    pp.MatchFirst(
                        [
                            pp.CaselessKeyword(
                                'STORED AS ORC TBLPROPERTIES ("orc.compress"="SNAPPY")'
                            ),
                            pp.CaselessKeyword(
                                'STORED AS ORC TBLPROPERTIES ("orc.compress"="ZLIB")'
                            ),
                            pp.CaselessKeyword(
                                'STORED AS ORC TBLPROPERTIES ("orc.compress"="LZO")'
                            ),
                            pp.CaselessKeyword(
                                'STORED AS ORC TBLPROPERTIES ("orc.compress"="NONE")'
                            ),
                            pp.CaselessKeyword(
                                'STORED AS ORC TBLPROPERTIES ("orc.compress"="ZSTD")'
                            ),
                        ]
                    )
                ),
                pp.Optional(pp.CaselessKeyword("AS")),
            ]
        )
    ).setResultsName("create")

    # Column Set grammar
    column_definition = pp.Group(
        pp.MatchFirst([column, case_column]) + column_alias
    ).setResultsName("column_def")

    columns = pp.delimitedList(column_definition, delim=",").setResultsName("columns")

    column_clause = pp.CaselessKeyword("SELECT") + columns + pp.CaselessKeyword("FROM")

    # Table grammer
    table_grammer = pp.Group(
        pp.Optional(allowed_name.setResultsName("source") + pp.Suppress("."))
        + allowed_name.setResultsName("table_name")
        + table_alias
    ).setResultsName("table_def")

    # Where clause grammer
    where_clause = pp.Group(pp.CaselessKeyword("WHERE") + condition_group)

    query_grammar = column_clause + table_grammer + pp.Optional(where_clause).setResultsName("where")
    assert isinstance(query_grammar, pp.ParserElement)

    # print("Basic Table Test")
    # for test in test_cases.basic_table_tests:
    #     print(test)
    #     pprint(query_grammar.parseString(test).asDict())

    # Join clause grammer
    sub_query = pp.Group(pp.Literal("(") + query_grammar + pp.Literal(")") + table_alias).setResultsName("sub_query")
    join_clause = pp.Group(
        pp.MatchFirst(
            [
                pp.CaselessKeyword("LEFT JOIN"),
                pp.CaselessKeyword("RIGHT JOIN"),
                pp.CaselessKeyword("OUTER JOIN"),
                pp.CaselessKeyword("INNER JOIN"),
                pp.CaselessKeyword("JOIN"),
            ]
        ).setResultsName("join_type")
        + pp.MatchFirst([sub_query, table_grammer])
        + pp.CaselessKeyword("ON")
        + condition_group
    )

    # print("Join Test")
    # for test in test_cases.join_tests:
    #     print(test)
    #     pprint(join_clause.parseString(test).asDict())


    # Group by clause grammer
    group_clause = pp.Group(pp.Suppress(pp.CaselessKeyword("GROUP BY")) + columns)

    # Order by clause grammer
    order_clause = pp.Group(pp.Suppress(pp.CaselessKeyword("ORDER BY")) + columns)

    # Limit clause grammer
    limit_clause = pp.Group(pp.Suppress(pp.CaselessKeyword("LIMIT")) + pp.Word(pp.nums))

    # Final Query grammer
    assert type(create_clause) == pp.Group and create_clause is not None

    query_parser = pp.And(
        [
            create_clause,
            pp.Optional(pp.Literal("(")),
            column_clause,
            table_grammer,
            pp.Optional(where_clause).setResultsName("wheres1"),
            pp.Optional(pp.Literal(";")),
            pp.Optional(pp.OneOrMore(join_clause)).setResultsName("joins"),
            pp.Optional(pp.Literal(";")),
            pp.Optional(where_clause).setResultsName("wheres2"),
            pp.Optional(pp.Literal(";")),
            pp.Optional(group_clause).setResultsName("group_by"),
            pp.Optional(pp.Literal(";")),
            pp.Optional(order_clause).setResultsName("order_by"),
            pp.Optional(pp.Literal(";")),
            pp.Optional(limit_clause).setResultsName("limit"),
            pp.Optional(pp.Literal(")")),
            pp.Optional(pp.Literal(";")),
        ]
    )

    parsed_query = query_parser.parseString(query)
    parsed_dict = parsed_query.asDict()
    # pprint(parsed_dict)
    parsed_dict = dict_to_obj(parsed_dict)
    table_data = Table()
    table_data.data_entry(parsed_dict)

    return table_data


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
        print("table_name ", table_name)
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
            print("current_table ", current_table.name)
            print("source_tables_new ", source_tables_new)
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


def read_script(file_path):
    tables = []
    with open(file_path, "r") as f:
        main_query = f.read()
        queries = separate_queries(main_query)
        for query in queries:
            # print("\nQuery: \n")
            # print(query)
            # print("\nParsed Query: \n")
            table = parse_create_query(query)
            tables.append(table)
            # print(table)
            # print(table.meta_data)
    return tables


# Run if this file is run directly
if __name__ == "__main__":
    show_window = False
    if show_window:
        display_text("Welcome to the SQL Query Parser\n Choose File to Parse")
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open file", "", "All files (*.*)"
        )

        print("after file read")
        with open(file_path, "r"):
            tables = read_script(file_path)
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
    else:
        tables = []
        file_path = "code/complex_query.sql"
        with open(file_path, "r"):
            print("reading file")
            tables = read_script(file_path)
        table_name = "new_table"
        column_name = ["col3"]
        definition, definition_str = get_definition(table_name, column_name, tables)
        print(definition_str)



