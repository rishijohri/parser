import sqlglot
from sqlglot.executor import execute 
import os
# Class for storing Table name, column names and source tables and filters for a SQL query.

class SQLQuery:
    def __init__(self, query):
        self.query = query
        self.table_name = ''
        self.columns = []
        self.source_table = ''
        self.filters = []
        self.source_table_columns = []
        self.parse_query()

    def parse_query(self):
        # Parse the query using sqlglot.
        parsed_query = sqlglot.parse(self.query)
        print(parsed_query)
        # Extract the table name.
        self.table_name = parsed_query[0]
        print(self.table_name)
        # # Extract the column names.
        # self.columns = parsed_query['create'].select.columns
        # # Extract the source table name.
        # self.source_table = parsed_query['create'].select
        # # Extract the filters.
        # self.filters = parsed_query['create'].select.where
        # # Extract the source table columns.
        # self.source_table_columns = parsed_query['create']

    def __str__(self):
        return f'Table name: {self.table_name}\nColumns: {self.columns}\nSource table: {self.source_table}\nFilters: {self.filters}\nSource table columns: {self.source_table_columns}\n'


specific_file = 'many_query.sql'
parse_specific_file = True

if parse_specific_file:
    with open("queries/" + specific_file, "r") as f:
        main_query = f.read()
        result = execute(main_query)
        print(result)

else:
    files = os.listdir("queries")
    for i, sql_file in enumerate(files):
        with open("queries/" + sql_file, "r") as f:
            main_query = f.read()
            result = execute(main_query)
            print("Query: " + sql_file)
            print("Result: ")
            print(type(result[0]))
