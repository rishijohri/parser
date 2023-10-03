import sqlglot

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


# Example usage:

query = 'CREATE TABLE new_table AS SELECT a.column1, column2 FROM sdb.source a WHERE column1 = 1 AND column2 = 2 ;'
sql_query = SQLQuery(query)
print(sql_query)