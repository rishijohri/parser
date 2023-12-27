from functions.parse_mk3 import parse_create_query


default_test_cases = {
    "column": False,
    "case_column": False,
    "condition": True,
    "create": False,
    "join": False,
    "table": False,
    "query": False,
    "print_query": True,
    "print_result": True,
}

parse_create_query('', default_test_cases)