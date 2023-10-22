import pyparsing as pp
import os
import pprint

# Create class to store information about Column
all_tables = []
all_columns = []
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


class BaseColumn:
    def __init__(self, column_name, source_alias=""):
        self.source_table = None
        self.column = column_name
        self.source_alias = source_alias

    def __str__(self):
        return (
            f"\n\t\tSource table: {self.source_table}\n"
            + f"\t\tColumn Name: {self.column}\n"
            + f"\t\tSource alias: {self.source_alias}\n"
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, BaseColumn):
            return False
        uncheck_alias = False 
        if self.source_alias == "" or __value.source_alias == "":
            uncheck_alias = True
        
        return (
            self.column == __value.column
            and self.source_table == __value.source_table
            and (uncheck_alias or self.source_alias == __value.source_alias)
        )
    
    def __hash__(self):
        return hash((self.source_table, self.column))


class Condition:
    def __init__(self, parse_query, result='NULL', condition_type="A.equality"):
        '''
        condition_type = "Z.else" | "A.equality" | "multiple"
        '''
        self.condition_type = condition_type
        self.conditions = []
        self.results = result
        self.source_columns = []
        self.source_aliases = []
        self.meta_data = parse_query
        for condition in parse_query:
            self.conditions.append(condition)
        if len(self.conditions) > 1:
            self.condition_type = "multiple"
        self.extract_columns()

    def extract_columns(self):
        # define grammer for matching column names
        column_def = (
            ~pp.Word(pp.nums) + pp.Word(pp.alphanums + "_\"'*/-+") + special_words
        )
        for condition in self.conditions:
            # print("ECC", condition)
            for token in condition:
                if type(token) == pp.ParseResults:
                    parse_token = column_def.searchString(token.name)
                    if len(parse_token):
                        self.source_columns.append(
                            BaseColumn(
                                column_name=token.name, source_alias=token.source
                            )
                        )
                        self.source_aliases.append(token.source)
        self.source_aliases = list(set(self.source_aliases))

    def post_process(self, alias_names, alias_list):
        for source_column in self.source_columns:
            if source_column.source_alias in alias_list:
                source_column.source_table = alias_names[source_column.source_alias]
            elif source_column.source_alias == "":
                source_column.source_table = alias_names[alias_list[0]]
    
    def recreate_query(self, source_columns = [], else_case=True):
        '''
        Recreate the query for the condition
        '''
        query = ''
        if source_columns == []:
            source_columns = self.source_columns
        # print('condition ', len(self.conditions), self.condition_type)
        if len(self.source_columns)==0:
            if else_case and self.results != 'NULL':
                query += 'ELSE ' + self.results + "\n"
        else:
            for condition in self.conditions:  
                # print("LHS         ", condition, self.condition_type)
                if condition.condition_type == "Z.else":
                    query += "ELSE " +condition.results + " "
                else:      
                    LHS_name = condition.LHS[0].name
                    RHS_name = condition.RHS[0].name
                    for source_column in source_columns:
                        if source_column.column == condition.LHS[0].name and source_column.source_alias == condition.LHS[0].source:
                            LHS_name = source_column.source_table + "." + source_column.column
                        if source_column.column == condition.RHS[0].name and source_column.source_alias == condition.RHS[0].source:
                            RHS_name = source_column.source_table + "." + source_column.column
                    query += LHS_name + " " + condition[1] + " " + RHS_name + " " + condition.delimiter + " "
            if self.results != 'NULL':
                query += "THEN " + self.results + "\n "

        return query

    def __str__(self):
        condition_str = "\n"
        for cond in self.conditions:
            condition_str += "\t\t" + str(cond) + " \n"

        source_column_str = "\n"
        for i in range(len(self.source_columns)):
            source_column_str += "\t" + str(self.source_columns[i])
            source_column_str += "\n"
        return (
            f" \n\tCondition type: {self.condition_type}\n "
            + f"\tConditions: {condition_str}\n "
            + f"\tCondition Results: {self.results}\n"
            + f"\tSource columns: {source_column_str}\n"
            # + f"\tCondition Source aliases: {self.source_aliases}\n"
        )


class Column:
    def __init__(self, parse_query, alias_names=[], alias_list=[]):
        self.name = None
        self.alias = None
        self.source_tables = []
        self.source_database = None
        self.source_columns = []
        self.conditions = []
        self.results = []
        self.source_aliases = []
        self.conditions_src = []
        self.meta_data = parse_query

        # check if column has single base column
        if parse_query.base_column != "":
            self.source_aliases.append(parse_query.base_column[0].source)
            self.source_columns = [
                BaseColumn(
                    column_name=parse_query.base_column[0].name,
                    source_alias=parse_query.base_column[0].source,
                )
            ]
            self.name = parse_query.base_column[0].name
            self.alias = parse_query.base_column[0].name

        # check if column has alias
        if len(parse_query.column_alias) != 0:
            self.alias = parse_query.column_alias[1]
            self.name = parse_query.column_alias[1]

        # check if column has case statement
        if len(parse_query.case_column) != 0:
            self.case_parser(parse_query.case_column)

        # extract distinct source columns and source aliases
        for condition in self.conditions:
            for source in condition.source_columns:
                if source not in self.source_columns:
                    self.source_columns.append(source)
            for alias in condition.source_aliases:
                if alias not in self.source_aliases:
                    self.source_aliases.append(alias)

        self.post_process(alias_names, alias_list)
        return
    
    def recreate_query(self):
        '''
        Recreate the query for the column
        '''
        query = ''
        if len(self.source_columns)==1:
            query += self.source_columns[0].column + " AS " + self.alias + "\n"
        else:
            query += "CASE \n"
            # self.conditions = sorted(self.conditions, key=lambda x: (x.condition_type))
            for condition in self.conditions:
                if condition.condition_type != "Z.else":
                    query += 'WHEN '
                query += condition.recreate_query(self.source_columns)
                        
                    #     # fix LHS and RHS names
                    #     LHS_name = cond.LHS[0].name
                    #     RHS_name = cond.RHS[0].name
                    #     for source_column in self.source_columns:
                    #         if source_column.column == cond.LHS[0].name:
                    #             LHS_name = source_column.source_table + "." + source_column.column
                    #         if source_column.column == cond.RHS[0].name:
                    #             RHS_name = source_column.source_table + "." + source_column.column
                    #     query += LHS_name + " " + cond[1] + " " + RHS_name + " " + cond.delimiter + ""
                    # query += "THEN " + condition.results + "\n "

            query += "END AS " + self.alias + "\n"
        return query
    
    def case_parser(self, parse_query):
        # for each case within case statement
        for i in range(len(parse_query.cases)):
            current_condition = Condition(
                parse_query.cases[i].equality_condition,
                parse_query.cases[i].result[0].name,
            )
            self.conditions.append(current_condition)
        
        # for else case
        if parse_query.else_case != "":
            else_condition = Condition(
                [], parse_query.else_case.base_column[0].name, condition_type="Z.else"
            )
            self.conditions.append(else_condition)

    def post_process(self, alias_names, alias_list):
        for alias in self.source_aliases:
            if alias in alias_list:
                self.source_tables.append(alias_names[alias])
            elif alias == "":
                self.source_tables.append(alias_names[alias_list[0]])

        self.source_tables = list(set(self.source_tables))

        for source_column in self.source_columns:
            if source_column.source_alias in alias_list:
                source_column.source_table = alias_names[source_column.source_alias]
            elif source_column.source_alias == "":
                source_column.source_table = alias_names[alias_list[0]]


    def __str__(self):
        condition_str = " \tConditions:\n"
        for i in range(len(self.conditions)):
            condition_str += "\t" + str(self.conditions[i])
            condition_str += "\n"
        condition_str += " \tResults:\n"
        for i in range(len(self.results)):
            condition_str += "\t" + str(self.results[i])
            condition_str += "\n"

        source_column_str = "\n"
        for i in range(len(self.source_columns)):
            source_column_str += "\t" + str(self.source_columns[i])
        return (
            f" \tColumn name: {self.name}\n "
            + f"\tSource aliases: {self.source_aliases}\n"
            + f"\tSource table: {self.source_tables}\n "
            + f"\tAlias: {self.alias} \n "
            + f"\tSource columns: {source_column_str}\n"
            + condition_str
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Column):
            return False
        
        return (
            self.name == __value.name
            # and self.alias == __value.alias
            and self.source_tables == __value.source_tables
            # and self.source_columns == __value.source_columns
            # and self.conditions == __value.conditions
            # and self.results == __value.results
            # and self.source_aliases == __value.source_aliases
        )

# Create class to store information about Join
class Join:
    def __init__(self, table, join_type, condition):
        # self.join_database = 'Default'
        # source_table_raw = table[0].split(".")
        # if len(source_table_raw) == 1:
        #     self.table = source_table_raw[0]
        # else:
        #     self.table = source_table_raw[1]
        #     self.join_database = source_table_raw[0]
        self.table = table[0]
        if len(table) > 1:
            self.alias = table[1]
        else:
            self.alias = table[0]
        self.join_type = join_type
        
        self.condition = Condition(condition)
        self.source_columns = self.condition.source_columns
        self.source_aliases = self.condition.source_aliases

    def post_process(self, alias_names, alias_list):
        for source_column in self.source_columns:
            if source_column.source_alias in alias_list:
                source_column.source_table = alias_names[source_column.source_alias]
            elif source_column.source_alias == "":
                source_column.source_table = alias_names[alias_list[0]]

    def __str__(self):
        source_column_str = "\n"
        for i in range(len(self.source_columns)):
            source_column_str += "\t" + str(self.source_columns[i])
        return (
            f"Join Table: {self.table}\n"
            + f"Join Table Alias: {self.alias}\n"
            + f"Join type: {self.join_type}\n"
            + f"Join Source Columns: {source_column_str}\n"
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
        self.filters = Condition([], result=[], condition_type="None")
        self.group_by = []
        self.order_by = []
        self.limit = None
        self.meta_data = None
        self.alias_list = []
        self.alias_names = {}

    def __str__(self):
        col_str = "\t--------------------------------\n"
        for col in self.columns:
            col_str += str(col)
            col_str += "\t--------------------------------\n"
        source_information = (
            "<>" * 25
            + f" \n Table name: {self.name}\n"
            + f" Source database: {self.source_database}\n "
            + f"Source table: {self.source_table}\n "
            + f"Source alias: {self.source_alias}\n"
            + "<>" * 25
        )
        join_info = ""
        for join in self.joins:
            join_info += str(join)
            join_info += "\t--------------------------------\n"
        return (
            f"{source_information}\n "
            + f"Filters: {self.filters}\n "
            + f"Joins: \n{join_info}\n"
            + f"Group by: {self.group_by}\n"
            + f"Order by: {self.order_by}\n"
            + f"Limit: {self.limit}\n"
            + f"Columns:\n{col_str}\n"
        )

    def alias_solver(self):
        """
        Figures out the relationship between aliases and tables names
        """
        alias_names = {}
        alias_list = []
        alias_names[self.source_alias] = self.source_table
        alias_list.append(self.source_alias)
        for join in self.joins:
            alias_names[join.alias] = join.table
            alias_list.append(join.alias)
        self.alias_names = alias_names
        self.alias_list = alias_list

    def post_process_columns(self):
        """
        Post process columns to add additional source columns from joins
        (convert alias to table name)
        """
        for column in self.columns:
            column.post_process(self.alias_names, self.alias_list)
            # add additional source column in column from joins

    def new_data_entry(self, parsed_query):
        # Find Table name
        name_raw = str(parsed_query.create.table_name).split(".")
        if len(name_raw) == 1:
            self.name = name_raw[0]
        else:
            self.name = name_raw[1]
            self.database = name_raw[0]

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

        # Solve for aliases
        self.alias_solver()

        # Find Columns
        column_parse = parsed_query.columns
        for column in column_parse:
            self.columns.append(
                Column(column, alias_names=self.alias_names, alias_list=self.alias_list)
            )


        #Post porcess Joins
        for join in self.joins:
            join.post_process(self.alias_names, self.alias_list)
        # Parse Group by

        # Parse Filters
        filter_parse = []
        if parsed_query.wheres2 != "":
            filter_parse = parsed_query.wheres2
        elif parsed_query.wheres1 != "":
            filter_parse = parsed_query.wheres1
        if filter_parse != []:
            self.filters = Condition(filter_parse[1])

        # post process filters
        if isinstance(self.filters, Condition):
            self.filters.post_process(self.alias_names, self.alias_list)
        # post process columns
        self.post_process_columns()

    def recreate_query(self, columns = []):
        '''
        For the column given in the list, recreate the query for only those columns
        '''
        query = ''
        # Add create statement
        query += f"CREATE TABLE {self.database}.{self.name} AS \n"

        # Add column statement
        query += "SELECT "
        combine_source_tables = []
        for column in columns:
            for source_table in column.source_tables:
                if source_table not in combine_source_tables:
                    combine_source_tables.append(source_table)
        for i, column in enumerate(columns):
            end_char = ""
            if i != len(columns) - 1:
                end_char = ", "
            query += column.recreate_query() + end_char
        # Add from statement
        query += "FROM " + self.source_database + "." + self.source_table + "\n"
        # print("combine_source_columns", combine_source_tables)
        # Add join statement
        for join in self.joins:
            # print(join.table)
            if join.table in combine_source_tables:
                query += join.join_type + " " + join.table + " ON " + join.condition.recreate_query() + "\n"

        # Add where statement
        if isinstance(self.filters, Condition) and self.filters.conditions != []:
            query += "WHERE " + self.filters.recreate_query(else_case=False) + "\n"

        return query


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
        pp.Group(
            special_words
            + pp.Optional(
                pp.Word(pp.alphanums).setResultsName("source") + pp.Suppress(".")
            )
            + pp.Word(pp.alphanums + "_\"'*/-+").setResultsName("name")
        )
    ).setResultsName("base_column")
    delimiter = pp.MatchFirst([pp.CaselessKeyword("AND"), pp.CaselessKeyword("OR")])
    equality_comparator = pp.ZeroOrMore(
        pp.Group(
            column.setResultsName("LHS")
            + pp.Word("=<>")
            + column.setResultsName("RHS")
            + pp.Optional(delimiter).setResultsName("delimiter")
        ),
        # delim=delimiter,
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
    # print(case_column.searchString(query))
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

def get_follow_sources(table_name, column_names=[]):
    source_columns = []
    source_tables = []
    match_table = None
    match_column = []
    for table in tables:
        if table.name == table_name:
            for column in table.columns:
                if column.name in column_names:
                    match_table = table
                    match_column.append(column)
                    for source_column in column.source_columns:
                        source_columns.append(source_column)

                    # Get Filter source columns
                    for source_column in table.filters.source_columns:
                        source_columns.append(source_column)

                    # distinct tables used
                    for source_column in source_columns:
                        source_tables.append(source_column.source_table)

                    source_tables = list(set(source_tables))
                    # Get Join source columns
                    for join in table.joins:
                        if join.table in source_tables:
                            for source_column in join.source_columns:
                                source_columns.append(source_column)
                    
                    source_columns = list(set(source_columns))

    return source_columns, source_tables, match_table, match_column


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
# table_name = "new_table"
# column_name = ["col3"]
# current_column = None
# current_table = None
# for table in tables:
#     recreate_columns = []
#     if table.name == table_name:
#         for column in table.columns:
#             if column.name in column_name:
#                 # print(column)
#                 recreate_columns.append(column)
#     if recreate_columns != []:
#         table_recreate = table.recreate_query(recreate_columns)
#         print(table_recreate)





