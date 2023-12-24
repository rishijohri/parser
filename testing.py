from functions.parse_mk3 import parse_create_query


default_test_cases = {
    "column": True,
    "case_column": False,
    "condition": False,
    "condition_group": False,
    "create": False,
    "join": False,
    "table": False,
    "query": False,
}

parse_create_query('', default_test_cases)