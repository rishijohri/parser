import pyparsing as pp
import re
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
import functions.test_cases as test_cases


def dict_to_obj(d):
    if isinstance(d, list):
        return [dict_to_obj(v) for v in d]
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                d[k] = dict_to_obj(v)
        return SimpleNamespace(**d)
    return d


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

def comment_remover(query):
    '''
    remove comments from hive and sql scripts
    comments start with -- and end with \n
    '''
    query_without_comments = re.sub(r'--.*?$|/\*.*?\*/', '', query, flags=re.MULTILINE|re.DOTALL)
    return query_without_comments

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
    comparator = pp.Word("=<>") | pp.CaselessKeyword("LIKE") | pp.CaselessKeyword("IS") | pp.CaselessKeyword("NOT LIKE") | pp.CaselessKeyword("IS NOT") | pp.CaselessKeyword("NOT")
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

def read_script(file_path):
    tables = []
    with open(file_path, "r") as f:
        main_query = f.read()
        queries = separate_queries(main_query)
        queries = query_type_check(queries)
        for query in queries:
            query = comment_remover(query)
            table = parse_create_query(query)
            tables.append(table)

    return tables


# Run if this file is run directly



