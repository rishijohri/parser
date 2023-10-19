import pyparsing as pp
import os
import pprint

# Create class to store information about Column
all_tables = []
special_words = (
    ~pp.CaselessKeyword("RIGHT")
    + ~pp.CaselessKeyword("LEFT")
    + ~pp.CaselessKeyword("INNER")
    + ~pp.CaselessKeyword("OUTER")
    + ~pp.CaselessKeyword("JOIN")
    + ~pp.CaselessKeyword("ON")
    + ~pp.CaselessKeyword("WHEN")
    + ~pp.CaselessKeyword("THEN")
    + ~pp.CaselessKeyword("ELSE")
    + ~pp.CaselessKeyword("END")
    + ~pp.CaselessKeyword("CASE")
    + ~pp.CaselessKeyword("WHERE")
    + ~pp.CaselessKeyword("GROUP")
    + ~pp.CaselessKeyword("ORDER")
    + ~pp.CaselessKeyword("LIMIT")
    + ~pp.CaselessKeyword("FROM")
    + ~pp.CaselessKeyword("SELECT")
    + ~pp.CaselessKeyword("CREATE")
    + ~pp.CaselessKeyword("TABLE")
    + ~pp.CaselessKeyword("AS")
    + ~pp.CaselessKeyword("IN")
    + ~pp.CaselessKeyword("AND")
    + ~pp.CaselessKeyword("OR")
)
special_words_list = [
    "RIGHT",
    "LEFT",
    "INNER",
    "OUTER",
    "JOIN",
    "ON",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
    "CASE",
    "WHERE",
    "GROUP",
    "ORDER",
    "LIMIT",
    "FROM",
    "SELECT",
    "CREATE",
    "TABLE",
    "AS",
    "IN",
    "AND",
    "OR",
]


class Condition:
    def __init__(self, parse_query, result=[], condition_type="equality"):
        self.condition_type = condition_type
        self.conditions = []
        self.results = result
        self.source_columns = []
        self.source_aliases = []
        for condition in parse_query:
            self.conditions.append(condition)
        if len(self.conditions) > 1:
            self.condition_type = "multiple"
        self.extract_columns()

    def extract_columns(self):
        columns = []
        column_def = (
            ~pp.Word(pp.nums) + pp.Word(pp.alphanums + "_.\"'*/-+") + special_words
        )
        for condition in self.conditions:
            # print('ECC', condition)
            for token in condition:
                parse_token = column_def.searchString(token)
                if len(parse_token) > 0:
                    col_name = parse_token[0][0].split(".")
                    # print(col_name)
                    if len(col_name) > 1:
                        if col_name[1] not in self.source_columns:
                            self.source_columns.append(col_name[1])
                        if col_name[0] not in self.source_aliases:
                            self.source_aliases.append(col_name[0])
                    else:
                        if col_name[0] not in self.source_columns:
                            self.source_columns.append(col_name[0])
        # print(self.source_aliases)

    def __str__(self):
        return (
            f" \n\tCondition type: {self.condition_type}\n "
            + f"\tConditions: {self.conditions}\n "
            + f"\tResults: {self.results}\n"
            # + f"\tSource columns: {self.source_columns}\n"
            + f"\tCondition Source aliases: {self.source_aliases}\n"
        )


class Column:
    def __init__(self, parse_query):
        self.name = None
        self.alias = None
        self.source_tables = []
        self.source_database = None
        self.source_columns = []
        self.conditions = []
        self.results = []
        self.source_aliases = []
        self.conditions_src = []
        # print(parse_query, len(parse_query))
        # check if column has single base column
        if parse_query.base_column != "":
            name_raw = parse_query.base_column[0].split(".")
            if len(name_raw) == 1:
                self.name = name_raw[0]
            else:
                self.name = name_raw[1]
                self.source_aliases.append(name_raw[0])
            self.source_columns = [parse_query.base_column[0]]
        # check if column has alias
        if len(parse_query.column_alias) != 0:
            self.alias = parse_query.column_alias[1]
            self.name = parse_query.column_alias[1]
        # check if column has case statement
        if len(parse_query.case_column) != 0:
            self.case_parser(parse_query.case_column)
        else:
            self.source_columns = [self.name]

        # extract source columns and source aliases
        for condition in self.conditions:
            for source in condition.source_columns:
                if source not in self.source_columns:
                    self.source_columns.append(source)
            for alias in condition.source_aliases:
                if alias not in self.source_aliases:
                    self.source_aliases.append(alias)
        return

    def case_parser(self, parse_query):
        # print("parse_query", parse_query.cases)
        for i in range(len(parse_query.cases)):
            current_condition = Condition(
                parse_query.cases[i].equality_condition, parse_query.cases[i].result
            )
            self.conditions.append(current_condition)
            # print("Equality ",parse_query.cases[i].equality_condition)
            # print("Condition \n", current_condition)
        if parse_query.else_case != "":
            else_condition = Condition(
                [], parse_query.else_case.base_column, condition_type="else"
            )
            self.conditions.append(else_condition)
            # print(else_condition)

    def post_process(self, alias_names, alias_list):
        # print(alias_names)
        if len(self.source_aliases) == 0:
            self.source_tables = [alias_names[alias_list[0]]]
        for alias in self.source_aliases:
            if alias in alias_list:
                self.source_tables.append(alias_names[alias])

    def when_parser(self, parse_query):
        self.conditions_src.append({"query": parse_query})
        condition_mark = 0
        # print(len(parse_query), parse_query)
        for i in range(1, len(parse_query)):
            if type(parse_query[i]) == pp.ParseResults:
                specific_conditions = []
                for j in range(len(parse_query[i])):
                    # print(parse_query[i][j], condition_mark)
                    if parse_query[i][j] == "WHEN":
                        condition_mark = 1
                    elif parse_query[i][j] == "THEN":
                        condition_mark = 2
                    elif parse_query[i][j] == "ELSE":
                        condition_mark = 3
                    elif condition_mark == 1:
                        specific_conditions.append(parse_query[i][j])
                    elif condition_mark == 2:
                        self.results.append(parse_query[i][j])
                    elif condition_mark == 3:
                        self.results.append(parse_query[i][j])
                    # print(parse_query[i][j], condition_mark)
                self.conditions.append(specific_conditions)
                # self.conditions_src.append(parse_query[i])
                # self.results.append(parse_query[i])

    def __str__(self):
        condition_str = " \tConditions:\n"
        for i in range(len(self.conditions)):
            condition_str += "\t" + str(self.conditions[i])
            condition_str += "\n"
        condition_str += " \tResults:\n"
        for i in range(len(self.results)):
            condition_str += "\t" + str(self.results[i])
            condition_str += "\n"
        # condition_str += " \tSource conditions:\n"
        # for i in range(len(self.conditions_src)):
        #     condition_str += "\t" + str(self.conditions_src[i])
        #     condition_str += "\n"
        return (
            f" \tColumn name: {self.name}\n "
            + f"\tSource aliases: {self.source_aliases}\n"
            + f"\tSource table: {self.source_tables}\n "
            + f"\tAlias: {self.alias} \n "
            + f"\tSource column: {self.source_columns}\n"
            + condition_str
        )


# Create class to store information about Filter


class Filter:
    def __init__(self, variable, comparator, value):
        self.variable = variable
        self.comparator = comparator
        self.value = value


# Create class to store information about Join


class Join:
    def __init__(self, table, join_type, condition):
        self.table = table[0]
        if len(table) > 1:
            self.alias = table[1]
        else:
            self.alias = table[0]
        self.join_type = join_type
        self.condition = Condition(condition)

    def __str__(self):
        return (
            f"Join Table: {self.table}\n"
            + f"Join Alias: {self.alias}\n"
            + f"Join type: {self.join_type}\n"
            + f"Join Condition: {self.condition}\n"
        )


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
            + f" \n Table name: {self.name}\n"
            + f" Source database: {self.source_database}\n "+f"Source table: {self.source_table}\n " + f"Source alias: {self.source_alias}\n"
            + "<>" * 25
        )
        join_info = ""
        for join in self.joins:
            join_info += str(join)
            join_info += "\t--------------------------------\n"
        return (
            f"{source_information}\n "
            + f"Filters: {self.filters}\n "
            + f"Joins: {join_info}\n"
            + f"Group by: {self.group_by}\n"
            + f"Order by: {self.order_by}\n"
            + f"Limit: {self.limit}\n"
            + f"Columns:\n{col_str}\n"
        )

    def post_process(self):
        alias_names = {}
        alias_list = []
        alias_names[self.source_alias] = self.source_table
        alias_list.append(self.source_alias)
        for join in self.joins:
            alias_names[join.alias] = join.table
            alias_list.append(join.alias)

        for column in self.columns:
            column.post_process(alias_names, alias_list)

    def new_data_entry(self, parsed_query):
        # Find Table name
        name_raw = str(parsed_query.create.table_name).split(".")
        if len(name_raw) == 1:
            self.name = name_raw[0]
        else:
            self.name = name_raw[1]
            self.database = name_raw[0]

        # Find Columns
        column_parse = parsed_query.columns
        for column in column_parse:
            self.columns.append(Column(column))

        # Find Source Table
        # print(parsed_query.table_def)
        source_table_raw = parsed_query.table_def[0].split(".")
        if len(source_table_raw) == 1:
            self.source_table = source_table_raw[0]
        else:
            self.source_table = source_table_raw[1]
            self.source_database = source_table_raw[0]

        # Find Source Table Alias
        if len(parsed_query.table_def) > 1:
            self.source_alias = parsed_query.table_def[1]
        else:
            self.source_alias = self.source_table
        # Parse Joins
        join_parse = parsed_query.joins
        for join in join_parse:
            self.joins.append(
                Join(
                    table=join.table_def,
                    join_type=join[0],
                    condition=join.equality_condition,
                )
            )

        # Parse Filters
        filter_parse = []
        if parsed_query.wheres2 != "":
            filter_parse = parsed_query.wheres2
        elif parsed_query.wheres1 != "":
            filter_parse = parsed_query.wheres1
        if filter_parse != []:
            self.filters = Condition(filter_parse[1])

        # post process columns
        self.post_process()

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
    return [query.strip() + " ;" for query in queries.split(";") if query.strip()]


# write parse_create_query function here using pyparsing
def parse_create_query(query):
    # define grammer

    column_alias = pp.Group(
        pp.Optional(
            pp.CaselessKeyword("AS")
            + special_words
            + pp.Word(pp.alphas + pp.nums + "_")
        )
    ).setResultsName("column_alias")
    table_alias = pp.Optional(
        pp.Optional(pp.CaselessKeyword("AS"))
        + special_words
        + pp.Word(pp.alphanums + "_")
    )
    column = pp.Optional(
        special_words + pp.Word(pp.alphanums + "_.\"'*/-+")
    ).setResultsName("base_column")
    alias_column = pp.Group(column + column_alias)
    equality_comparator = pp.delimitedList(
        pp.Group(
            column.setResultsName("LHS") + pp.Word("=<>") + column.setResultsName("RHS")
        ),
        delim=pp.MatchFirst([pp.CaselessKeyword("AND"), pp.CaselessKeyword("OR")]),
    ).setResultsName("equality_condition")
    in_comparator = pp.Group(
        column
        + pp.CaselessKeyword("IN")
        + pp.MatchFirst(
            [
                pp.Word("(") + pp.Group(pp.delimitedList(column)) + pp.Word(")"),
                pp.Group(pp.delimitedList(column)),
            ]
        )  # + pp.Literal(')')
    )
    case_column = pp.Group(
        pp.Optional(
            pp.CaselessKeyword("CASE")
            + pp.OneOrMore(
                pp.Group(
                    pp.CaselessKeyword("WHEN")
                    + equality_comparator
                    + pp.CaselessKeyword("THEN")
                    + column.setResultsName("result")
                ).setResultsName("case")
            ).setResultsName("cases")
            + pp.Group(pp.Optional(pp.CaselessKeyword("ELSE") + column)).setResultsName(
                "else_case"
            )
            + pp.CaselessKeyword("END")
        )
    ).setResultsName("case_column")
    all_column = pp.Group(column + case_column + column_alias).setResultsName(
        "all_column"
    )
    # all_column = pp.MatchFirst([case_column, alias_column, column])
    columns = pp.delimitedList(all_column, delim=pp.Char(",")).setResultsName("columns")
    table_grammer = pp.Group(pp.Word(pp.alphanums + "_.") + table_alias).setResultsName(
        "table_def"
    )
    create_clause = pp.Group(
        pp.CaselessKeyword("CREATE")
        + pp.CaselessKeyword("TABLE")
        + pp.Word(pp.alphanums + "_*").setResultsName("table_name")
        + pp.CaselessKeyword("AS")
    ).setResultsName("create")
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

    query_parser = (
        create_clause
        + pp.Optional(pp.Literal("("))
        + column_clause
        + table_grammer
        + pp.Optional(where_clause).setResultsName("wheres1")
        + pp.Optional(pp.Literal(";"))
        + pp.Optional(pp.delimitedList(join_clause)).setResultsName("joins")
        + pp.Optional(pp.Literal(";"))
        + pp.Optional(where_clause).setResultsName("wheres2")
        + pp.Optional(pp.Literal(";"))
        + pp.Optional(group_clause).setResultsName("groups")
        + pp.Optional(pp.Literal(";"))
        + pp.Optional(order_clause).setResultsName("orders")
        + pp.Optional(pp.Literal(";"))
        + pp.Optional(limit_clause)
        + pp.Optional(pp.Literal(")"))
        + pp.Optional(pp.Literal(";"))
    )
    parsed_query = query_parser.parseString(query)
    # print(parsed_query)
    # Store the parsed value in Corresponding class
    table_data = Table()
    # k = 0
    # print(len(parsed_query.columns[k][1]), type(parsed_query.columns[k][1]))
    # try:
    #     print("WHERE ", parsed_query.wheres2[1])
    #     print(parsed_query.table_def)
    #     # print(parsed_query.columns[2].case_column.cases[0].equality_condition[1])
    #     # print(parsed_query.columns[2].case_column.cases[1].result[0])
    # except:
    #     print("error")
    # if len(parsed_query.joins) > 0:
    #     print(parsed_query.joins[0])
    #     print(parsed_query.joins[0].equality_condition[0])

    table_data.meta_data = parsed_query
    table_data.new_data_entry(parsed_query)

    return table_data


# Example usage:
specific_file = "complex_query.sql"
parse_specific_file = True
# List all files in queries directory
if parse_specific_file:
    tables = []
    with open("queries/" + specific_file, "r") as f:
        main_query = f.read()
        queries = separate_queries(main_query)
        for query in queries:
            print("\nQuery: \n")
            print(query)
            print("\nParsed Query: \n")
            table = parse_create_query(query)
            tables.append(table)
            print(table)
else:
    files = os.listdir("queries")
    for i, sql_file in enumerate(files):
        with open("queries/" + sql_file, "r") as f:
            main_query = f.read()
            queries = separate_queries(main_query)
            for query in queries:
                result = parse_create_query(query)
                # pprint(result)


# For Complex query
# IN Complex_Query.sql to search for origin of col3 in new_table
table_name = "new_table"
column_name = "col3"
current_column = None
current_table = None
# find current table
# for table in tables:
#     if table.name == table_name:
#         current_table = table
#         break
# if current_table is not None:
#     for column in current_table.columns:
#         if column.name == column_name:
#             current_column = column
#             break
#     if current_column is not None:
#         current_source_table = current_column.source_table
#         current_source_column = current_column.source_column
