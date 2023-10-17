import pyparsing as pp
import os

# Create class to store information about Column
all_tables = []


class Column:
    def __init__(self, parse_query):
        self.name = None
        self.alias = None
        self.source_table = None
        self.source_database = None
        self.source_column = None
        self.conditions = []
        self.results = []
        if len(parse_query) == 1:
            details = parse_query[0].split(".")
            if len(details) == 1:
                self.name = parse_query[0]
                self.alias = None
                self.source_column = parse_query[0]
            else:
                self.name = details[1]
                self.alias = None
                self.source_column = details[1]
                self.source_table = details[0]
        else:
            if parse_query[0] == "CASE":
                self.name = parse_query[5]
                self.alias = parse_query[5]
                self.when_parser(parse_query)
                print(parse_query[1])

    def condition_parser(self, parse_query):
        for i in range(1, len(parse_query)):
            if type(parse_query[i]) == pp.ParseResults:
                self.conditions.append(parse_query[i])

    def when_parser(self, parse_query):
        for i in range(1, len(parse_query)):
            if type(parse_query[i]) == pp.ParseResults:
                if parse_query[i][0] == "WHEN":
                    self.conditions.append(parse_query[i][1])
                self.conditions.append(parse_query[i])
                self.results.append(parse_query[i])
            elif parse_query[i] == "END":
                break
            elif parse_query[i] == "THEN":
                self.results.append(parse_query[i + 1])

    def __str__(self):
        condition_str = " \tConditions:\n"
        for condition in self.conditions:
            condition_str += "\t" + str(condition)
            condition_str += "\n"
        return (
            f" \tColumn name: {self.name}\n \tSource table: {self.source_table}\n \tAlias: {self.alias} \n \tSource column: {self.source_column}\n"
            + condition_str
        )


# Create class to store information about Filter


class Filter:
    def __init__(self, variable, comparator, value):
        self.variable = variable
        self.comparator = comparator
        self.value = value


# Create Case_Column class inheriting from Column which also includes information about the case statement


class Case_Column(Column):
    def __init__(self, parse_query):
        super().__init__(parse_query)

        self.conditions = []
        self.results = []
        self.source_tables = []
        self.source_column = []

    def __str__(self):
        return f" Column name: {self.name}\n Source table: {self.source_table}\n Alias: {self.alias} \n Source column: {self.source_column}\n"


# Create class to store information about Join


class Join:
    def __init__(self, table, join_type, condition):
        self.table = table
        self.join_type = join_type
        self.condition = condition


# Create class to store information about Table


class Table:
    def __init__(self, name="Unset", alias=None):
        self.database = "Default"
        self.source_database = None
        self.source_table = None
        self.name = name
        self.source_alias = alias
        self.columns = []
        self.joins = []
        self.filters = []
        self.group_by = []
        self.order_by = []
        self.limit = None
        self.meta_data = None

    def __str__(self):
        col_str = "\t--------------------------------\n"
        for col in self.columns:
            col_str += str(col)
            col_str += "\t--------------------------------\n"
        source_information = (
            "<>" * 25
            + f"\n Source database: {self.source_database}\n Source table: {self.source_table}\n Source alias: {self.source_alias}\n"
            + "<>" * 25
        )
        return (
            f" Table name: {self.name}\n"
            + f"{source_information}\n "
            + f"Filters: {self.filters}\n "
            + f"Joins: {self.joins}\n"
            + f"Group by: {self.group_by}\n"
            + f"Order by: {self.order_by}\n"
            + f"Limit: {self.limit}\n"
            + f"Columns:\n{col_str}\n"
        )

    def name_parser(self, parsed_query):
        name = parsed_query.split(".")
        if len(name) == 1:
            self.name = name[0]
        else:
            self.name = name[1]
            self.database = name[0]

    def source_table_parser(self, parsed_query):
        if len(parsed_query) == 1:
            self.source_table = parsed_query[0]
        else:
            self.source_table = parsed_query[0]
            self.source_alias = parsed_query[1]

    def data_entry1(self, parsed_query):
        # table name
        table_name = parsed_query["table_def"]

    def data_entry(self, parsed_query):
        for i, token in enumerate(parsed_query):
            if token == "CREATE":
                self.name_parser(parsed_query[i + 2])
            elif token == "SELECT":
                k = parsed_query.asList().index("FROM")
                for j in range(i + 1, k):
                    self.columns.append(Column(parsed_query[j]))
            elif token == "FROM":
                self.source_table_parser(parsed_query[i + 1])
            elif token == "WHERE":
                self.filters = parsed_query[i + 1]
            elif token == "JOIN":
                self.joins.append(
                    Join(parsed_query[i + 1], parsed_query[i + 2], parsed_query[i + 3])
                )
            elif token == "GROUP BY":
                self.group_by = parsed_query[i + 1]
            elif token == "ORDER BY":
                self.order_by = parsed_query[i + 1]
            elif token == "LIMIT":
                self.limit = parsed_query[i + 1]

        # Change source table of each column to source table of table
        for column in self.columns:
            if column.source_table == None:
                column.source_table = self.source_table
                column.source_database = self.source_database
            if column.source_column == None:
                column.source_column = column.name
            if column.alias == None:
                column.alias = column.name


# Create a Tree Node which will store information about tables. children will be source tables and parent will be new table.


class TreeNode:
    def __init__(self, table):
        self.table = table
        self.children = []
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self


# write function to seperate different queries from a string
def separate_queries(queries):
    return [query.strip() + ";" for query in queries.split(";") if query.strip()]


# write parse_create_query function here using pyparsing
def parse_create_query(query):
    # define grammer
    column_alias = pp.Optional(
        pp.CaselessKeyword("AS") + pp.Word(pp.alphas + pp.nums + "_")
    )
    table_alias = pp.Optional(
        pp.Optional(pp.CaselessKeyword("AS"))
        + ~pp.CaselessKeyword("RIGHT")
        + pp.Word(pp.alphanums + "_")
    )
    column = pp.Word(pp.alphanums + "_.\"'*/-+")
    alias_column = pp.Group(column + column_alias)
    equality_comparator = pp.delimitedList(
        pp.Group(column + pp.Word("=<>") + column),
        delim=pp.MatchFirst([pp.CaselessKeyword("AND"), pp.CaselessKeyword("OR")]),
    )
    in_comparator = pp.Group(
        column
        + pp.CaselessKeyword("IN")
        + pp.MatchFirst([pp.Word("(")+pp.Group(pp.delimitedList(column))+pp.Word(")"), pp.Group(pp.delimitedList(column))])   # + pp.Literal(')')
    )
    case_column = pp.Group(
        pp.CaselessKeyword("CASE")
        + pp.Group(
            pp.OneOrMore(
                pp.CaselessKeyword("WHEN")
                + equality_comparator
                + pp.CaselessKeyword("THEN")
                + column
            )
        )
        + pp.Group(pp.Optional(pp.CaselessKeyword("ELSE") + column))
        + pp.CaselessKeyword("END")
        + column_alias
    )
    all_column = pp.MatchFirst([case_column, alias_column, column])
    columns = pp.delimitedList(all_column, delim=pp.Char(",")).setResultsName("columns")
    table_grammer = pp.Group(pp.Word(pp.alphanums + "_.") + table_alias).setResultsName(
        "table_def"
    )
    create_clause = (
        pp.CaselessKeyword("CREATE")
        + pp.CaselessKeyword("TABLE")
        + pp.Word(pp.alphanums + "_*")
        + pp.CaselessKeyword("AS")
    )
    column_clause = pp.CaselessKeyword("SELECT") + columns + pp.CaselessKeyword("FROM")
    where_clause = pp.CaselessKeyword("WHERE") + pp.Group(
        pp.delimitedList(
            equality_comparator,
            delim=pp.MatchFirst([pp.CaselessKeyword("AND"), pp.CaselessKeyword("OR")]),
        )
    )
    join_clause = pp.Group(
        pp.MatchFirst(
            [
                pp.CaselessKeyword("LEFT JOIN"),
                pp.CaselessKeyword("RIGHT JOIN"),
                pp.CaselessKeyword("OUTER JOIN"),
                pp.CaselessKeyword("INNER JOIN"),
                pp.CaselessKeyword("JOIN"),
            ]
        )
        + table_grammer
        + pp.CaselessKeyword("ON")
        + equality_comparator
    ).setResultsName("join")
    group_clause = pp.CaselessKeyword("GROUP BY") + pp.Group(pp.delimitedList(column))
    order_clause = pp.CaselessKeyword("ORDER BY") + pp.Group(pp.delimitedList(column))
    limit_clause = pp.CaselessKeyword("LIMIT") + pp.Word(pp.nums)
    # print(case_column.searchString(query))
    # Checking query correctness

    query_parser = (
        create_clause
        + column_clause
        + table_grammer
        + pp.Optional(where_clause)
        + pp.ZeroOrMore(join_clause).setResultsName("joins")
        + pp.Optional(where_clause)
        + pp.Optional(group_clause)
        + pp.Optional(order_clause)
        + pp.Optional(limit_clause)
        + pp.Literal(";")
    )
    parsed_query = query_parser.parseString(query)
    print(parsed_query["table_def"], type(parsed_query["table_def"]))
    # Store the parsed value in Corresponding class
    table_data = Table()
    table_data.meta_data = parsed_query
    table_data.data_entry(parsed_query)

    return table_data


# Example usage:
specific_file = "complex_query.sql"
parse_specific_file = True
# List all files in queries directory
if parse_specific_file:
    with open("queries/" + specific_file, "r") as f:
        main_query = f.read()
        queries = separate_queries(main_query)
        for query in queries:
            result = parse_create_query(query)
            print(result)

else:
    files = os.listdir("queries")
    for i, sql_file in enumerate(files):
        with open("queries/" + sql_file, "r") as f:
            main_query = f.read()
            queries = separate_queries(main_query)
            for query in queries:
                result = parse_create_query(query)
                print(result)
