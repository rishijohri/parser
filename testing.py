from functions.parse_mk3 import parse_create_query


default_test_cases = {
    "column": False,
    "case_column": False,
    "condition": True,
    "create": False,
    "join": False,
    "table": False,
    "query": False,
    "row_num_col": True,
}

parse_create_query('', default_test_cases)