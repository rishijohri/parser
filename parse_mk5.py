import sqlparse
import os
from sqlparse import parse
from sqlparse import extract_tables

# Testing on queries
specific_file = 'complex_query.sql'
parse_specific_file = True

if parse_specific_file:
    with open("queries/" + specific_file, "r") as f:
        main_query = f.read()
        result = parse(main_query)
        print("Query: " + specific_file)
        print("Result: ")
        print(type(result[0]))
        print(result[0].get_type())
        print(extract_tables(result[0]))
else:
    files = os.listdir("queries")
    for i, sql_file in enumerate(files):
        with open("queries/" + sql_file, "r") as f:
            main_query = f.read()
            result = parse(main_query)
            print("Query: " + sql_file)
            print("Result: ")
            print(type(result[0]))
