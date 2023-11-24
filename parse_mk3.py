import pyparsing as pp
import os
import pprint
from tkinter import filedialog
from PyQt5.QtWidgets import QApplication, QFileDialog
from choice_view import choose_elements
from display_view import display_text
from typing import Tuple, List

app = QApplication([])
# Create class to store information about Column
all_tables = []
all_columns = []

special_words = pp.And(
    [
        ~pp.CaselessKeyword("RIGHT"),
        ~pp.CaselessKeyword("LEFT"),
        ~pp.CaselessKeyword("INNER"),
        ~pp.CaselessKeyword("OUTER"),
        ~pp.CaselessKeyword("JOIN"),
        ~pp.CaselessKeyword("ON"),
        ~pp.CaselessKeyword("WHEN"),
        ~pp.CaselessKeyword("THEN"),
        ~pp.CaselessKeyword("ELSE"),
        ~pp.CaselessKeyword("END"),
        ~pp.CaselessKeyword("CASE"),
        ~pp.CaselessKeyword("WHERE"),
        ~pp.CaselessKeyword("GROUP"),
        ~pp.CaselessKeyword("ORDER"),
        ~pp.CaselessKeyword("LIMIT"),
        ~pp.CaselessKeyword("FROM"),
        ~pp.CaselessKeyword("SELECT"),
        ~pp.CaselessKeyword("CREATE"),
        ~pp.CaselessKeyword("TABLE"),
        ~pp.CaselessKeyword("AS"),
        ~pp.CaselessKeyword("IN"),
        ~pp.CaselessKeyword("AND"),
        ~pp.CaselessKeyword("OR"),
    ]
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
    def __init__(self, column_name="", source_alias="", details=""):
        self.source_table: str = ""
        if details == "":
            self.column = column_name
            self.source_alias = source_alias
        else:
            # print('IN BASE COLUMN ', details)
            detail_list = details.split(".")
            if len(detail_list) == 1:
                self.column = detail_list[0]
                self.source_alias = ""
            else:
                self.column = detail_list[1]
                self.source_alias = detail_list[0]

    def __str__(self):
        return (
            f"\n\t\tSource table: {self.source_table}\n"
            + f"\t\tColumn Name: {self.column}\n"
            # + f"\t\tSource alias: {self.source_alias}\n"
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
    def __init__(self, parse_query, result="NULL", condition_type="A.equality"):
        """
        condition_type = "Z.else" | "A.equality" | "multiple"
        """
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
        """
        Extracts the source columns and source table aliases from the condition
        """
        # define grammer for matching column names
        global special_words
        special_chars = "_*/-+"
        added_def = ~pp.Word(pp.nums) + pp.Word(pp.alphanums + special_chars) or ""
        column_def = added_def + special_words
        assert type(column_def) == pp.And
        for condition in self.conditions:
            # print("ECC", condition)
            for token in condition:
                if type(token) == pp.ParseResults:
                    parse_token = column_def.searchString(token.name)
                    if len(parse_token) and parse_token[0][0] == token.name:
                        base_col = BaseColumn(
                            column_name=str(token.name), source_alias=str(token.source)
                        )
                        self.source_columns.append(base_col)
                        self.source_aliases.append(token.source)
        self.source_aliases = list(set(self.source_aliases))

    def post_process(self, alias_names, alias_list):
        for source_column in self.source_columns:
            if source_column.column.upper() == "NULL":
                source_column.source_table = "null"
                source_column.source_alias = "null"
            elif source_column.source_alias in alias_list:
                source_column.source_table = alias_names[source_column.source_alias]
            elif source_column.source_alias == "":
                source_column.source_table = alias_names[alias_list[0]]

    def recreate_column(self, parse_query, source_columns=[]):
        column_name = parse_query.name
        for source_column in source_columns:
            if (source_column.column == column_name and 
            ((parse_query.source!='' and source_column.source_alias == parse_query.source)
            or parse_query.source=='')):
                column_name = source_column.source_table + "." + source_column.column
                break;
        arguments = parse_query.arguments
        if parse_query.arguments != "":
            arguments = ', ' + ', '.join(parse_query.arguments)
        if parse_query.aggregate_func:
            return parse_query.aggregate_func + "(" +column_name + arguments + ")"
        else:
            return column_name
        
    def recreate_query(self, source_columns=[], else_case=True):
        """
        Recreate the query for the condition
        """
        query = ""
        if source_columns == []:
            source_columns = self.source_columns
        # print('condition ', len(self.conditions), self.condition_type)
        if len(self.source_columns) == 0:
            if else_case and self.results != "NULL":
                query += "ELSE " + self.results + "\n"
        else:
            for condition in self.conditions:
                # print("LHS         ", condition, self.condition_type)
                if condition.condition_type == "Z.else":
                    query += "ELSE " + condition.results + " "
                else:
                    if condition[1].upper() == "IN":
                        LHS_name = self.recreate_column(condition.LHS, source_columns)
                        # RHS[0] and RHS[2] are ( and )
                        RHS_name = ",".join(condition.RHS[1])
                        query += (
                            LHS_name
                            + " "
                            + condition[1]
                            + " ("
                            + str(RHS_name)
                            + ") "
                            + condition.delimiter
                            + " "
                        )
                    else:
                        print(condition.LHS, condition.RHS)
                        LHS_name = self.recreate_column(condition.LHS, source_columns)
                        RHS_name = self.recreate_column(condition.RHS, source_columns)
                        print(LHS_name, RHS_name)
                        query += (
                            LHS_name
                            + " "
                            + condition[1]
                            + " "
                            + RHS_name
                            + " "
                            + condition.delimiter
                            + " "
                        )
            if self.results != "NULL":
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


class ConditionGroup:
    def __init__(self, parse_query, result="NULL", condition_type="Normal"):
        """
        condition_type = "Z.else" | "A.equality" | "multiple"
        """
        self.results = result
        self.condition_type = condition_type
        self.source_columns = []
        self.source_aliases = []
        self.meta_data = parse_query
        self.delimiter: str = parse_query.delimiter or ""
        # print(self.delimiter)

        self.conditions = Condition(parse_query.condition_group)
        # print(self.conditions)

    def post_process(self, alias_names, alias_list):
        self.conditions.post_process(alias_names, alias_list)
        self.source_columns = self.conditions.source_columns
        self.source_aliases = self.conditions.source_aliases

    def extract_columns(self):
        """
        Extracts the source columns and source table aliases from the condition
        """
        # define grammer for matching column names
        self.conditions.extract_columns()
        self.source_columns = self.conditions.source_columns
        self.source_aliases = self.conditions.source_aliases

    def recreate_query(self, source_columns=[], else_case=True):
        """
        Recreate the query for the condition
        """
        query = ""
        if source_columns == []:
            source_columns = self.source_columns
        # print('condition ', len(self.conditions), self.condition_type)
        if len(self.source_columns) == 0:
            if else_case and self.results != "NULL":
                query += "ELSE " + self.results + "\n"
        else:
            query += "("
            query += self.conditions.recreate_query(source_columns, else_case)
            query += ")\n"
            query += self.delimiter + " "
            if self.results != "NULL":
                query += "THEN " + self.results + "\n "
        return query

    def __str__(self):
        condition_str = "\n"
        source_columns_str = "\n"
        for src_col in self.source_columns:
            condition_str += "\t\t" + str(src_col) + " \n"
        return (
            f" \n\tCONDITION GROUP\n "
            + f"\tConditions: {self.conditions}\n "
            + f"\tCondition Results: {self.results}\n"
            + f"\tSource columns: {source_columns_str}\n"
            # + f"\tCondition Source aliases: {self.source_aliases}\n"
        )


class Column:
    def __init__(self, parse_query, alias_names=[], alias_list=[]):
        self.name: str = ""
        self.alias: str = ""
        self.source_tables = []
        self.source_database: str = "Default"
        self.source_columns: list[BaseColumn] = []
        self.conditions = []
        self.results = []
        self.source_aliases = []
        self.conditions_src = []
        self.meta_data = parse_query
        self.aggregate_func = ""
        self.arguments = ""
        self.operation = ""
        self.case_type = False
        operand = pp.Word(pp.alphanums + "_") | pp.Word(pp.nums)
        operator = pp.oneOf("+ - * /")
        operand_expr = operand + pp.ZeroOrMore(operator + operand)
        assert type(operand_expr) == pp.And
        if parse_query.base_column != "":
            self.source_aliases.append(parse_query.base_column.source)
            # Checking if any numeric operation is done on base_column
            operand_parse = operand_expr.parseString(parse_query.base_column.name)
            if len(operand_parse) == 1:
                self.source_columns = [
                    BaseColumn(
                        column_name=parse_query.base_column.name,
                        source_alias=parse_query.base_column.source,
                    )
                ]
            else:
                self.operation = parse_query.base_column.name
                for i in range(len(operand_parse)):
                    if i % 2 == 0:

                        if len(pp.Word(pp.alphas).searchString(operand_parse[i])) > 0:
                            self.source_columns.append(
                                BaseColumn(details=operand_parse[i])
                            )
                            self.source_aliases.append(parse_query.base_column.source)
            self.name = parse_query.base_column.name
            self.alias = parse_query.base_column.name
            self.aggregate_func = parse_query.base_column.aggregate_func
            self.arguments = parse_query.base_column.arguments
        # check if column has alias
        if len(parse_query.column_alias) != 0:
            self.alias = parse_query.column_alias[1]
            self.name = parse_query.column_alias[1]

        # check if column has case statement
        if len(parse_query.case_column) != 0:
            self.case_type = True
            self.case_parser(parse_query.case_column)

        # post process conditions
        for condition in self.conditions:
            condition.post_process(alias_names, alias_list)

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
        """
        Recreate the query for the column
        """
        query = ""
        aggregate_func = ""
        aggregate_func_end = ""
        if self.aggregate_func != "":
            aggregate_func = self.aggregate_func + "("
            if self.arguments != "":
                aggregate_func_end = ", " + ", ".join(self.arguments) + ")"
            else:
                aggregate_func_end = ")"
            # aggregate_func_end = ")"
        if self.operation != "":
            # print(self.__str__())
            # print(self.operation)
            query += (
                aggregate_func
                + str(self.operation)
                + aggregate_func_end
                + " AS "
                + str(self.alias)
                + "\n"
            )
        elif len(self.source_columns) == 1 and self.case_type == False:
            query += (
                aggregate_func
                + self.source_columns[0].source_table
                + "."
                + self.source_columns[0].column
                + aggregate_func_end
                + " AS "
                + self.alias
                + "\n"
            )
        else:
            query += "CASE \n"
            # self.conditions = sorted(self.conditions, key=lambda x: (x.condition_type))
            for condition in self.conditions:
                if condition.condition_type != "Z.else":
                    query += "WHEN "
                query += condition.recreate_query(self.source_columns)

            query += "END AS " + self.alias + "\n"
        return query

    def case_parser(self, parse_query):
        # for each case within case statement
        for case in parse_query.cases:
            current_conditions = []
            for condition_grp in case.all_condition:
                current_condition = ConditionGroup(parse_query=condition_grp,)
                current_conditions.append(current_condition)
            current_conditions[-1].results = case.result.name
            self.conditions.extend(current_conditions)

        # for else case
        if parse_query.else_case != "":
            else_condition = Condition(
                [], parse_query.else_case.base_column.name, condition_type="Z.else"
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

        aggregate_func_str = ""
        if self.aggregate_func != "":
            aggregate_func_str = "Aggregate: " + self.aggregate_func + "\n"
        return (
            f" \tColumn name: {self.name}\n "
            # + f"\tSource aliases: {self.source_aliases}\n"
            + f"\tSource table: {self.source_tables}\n "
            + f"\tAlias: {self.alias} \n "
            + f"\tSource columns: {source_column_str}\n"
            + f"\t{aggregate_func_str}"
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
        self.table = table[0]
        self.condition = []
        if len(table) > 1:
            self.alias = table[1]
        else:
            self.alias = table[0]
        self.join_type = join_type
        for condition_grp in condition:
            self.condition.append(ConditionGroup(condition_grp))
        # self.condition = Condition(condition)
        self.source_columns = []
        self.source_aliases = []

    def post_process(self, alias_names, alias_list):
        for condition in self.condition:
            condition.post_process(alias_names, alias_list)

        for condition in self.condition:
            condition.post_process(alias_names, alias_list)
            self.source_columns.extend(condition.source_columns)
            self.source_aliases.extend(condition.source_aliases)

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
    def __init__(self, name: str = "Unset", alias=None):
        self.database: str = "Default"
        self.source_database: str = "Default"
        self.source_table: str = ""
        self.name = name
        self.source_alias = alias
        self.columns = []
        self.joins = []
        # self.filters = Condition([], result="NULL", condition_type="None")
        self.filters: list = []
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
                    condition=join.all_condition,
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

        # Post porcess Joins
        print(self.alias_names, self.alias_list)
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
            for condition_grp in filter_parse[0].all_condition:
                # print("condition_grp ", condition_grp)
                where_filter = ConditionGroup(condition_grp)
                self.filters.append(where_filter)
            # self.filters = Condition(filter_parse[1])

        # post process filters
        for where_filter in self.filters:
            where_filter.post_process(self.alias_names, self.alias_list)
        # post process columns
        self.post_process_columns()

    def recreate_query(self, columns=[]):
        """
        For the column given in the list, recreate the query for only those columns
        """
        query = ""
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
                query += join.join_type + " " + join.table + " ON "
                for condition in join.condition:
                    query += condition.recreate_query()
                query += "\n"

        # Add where statement
        if isinstance(self.filters, list):
            if len(self.filters) > 0:
                query += "WHERE "
            for where_filter in self.filters:
                query += where_filter.recreate_query()
            # query += "WHERE " + self.filters.recreate_query(else_case=False) + "\n"

        return query


# write function to seperate different queries from a string
def separate_queries(queries):
    return [query.strip() + " ;" for query in queries.split(";") if query.strip()]


# write parse_create_query function here using pyparsing
def parse_create_query(query):
    # define grammer
    # ALias Grammar
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
    # Aggregation func grammer
    aggregate_func = (
        pp.CaselessKeyword("SUM")
        | pp.CaselessKeyword("AVG")
        | pp.CaselessKeyword("COUNT")
        | pp.CaselessKeyword("MIN")
        | pp.CaselessKeyword("MAX")
    )
    assert isinstance(aggregate_func, pp.ParserElement)
    multi_argu_func = (
        pp.CaselessKeyword("CONCAT")
        | pp.CaselessKeyword("SUBSTR")
        | pp.CaselessKeyword("TRIM")
        | pp.CaselessKeyword("COALESCE")
        | pp.CaselessKeyword("CAST")
        | pp.CaselessKeyword("DATE_FORMAT")
        | pp.CaselessKeyword("ADD_MONTHS")
    )
    assert isinstance(multi_argu_func, pp.ParserElement)

    # Base column Grammar (Column can have aggregation function)
    column: pp.ParserElement = pp.Optional(
        pp.MatchFirst(
            [
                pp.Group(
                    special_words
                    + aggregate_func.setResultsName("aggregate_func")
                    + pp.Suppress("(")
                    + pp.Optional(
                        pp.Word(pp.alphanums).setResultsName("source")
                        + pp.Suppress(".")
                    )
                    + pp.Word(pp.alphanums + "_\"'*/-+").setResultsName("name")
                    + pp.Suppress(")")
                ),
                pp.Group(
                    special_words
                    + multi_argu_func.setResultsName("aggregate_func")
                    + pp.Suppress("(")
                    + pp.Optional(
                        pp.Word(pp.alphanums).setResultsName("source")
                        + pp.Suppress(".")
                    )
                    + pp.Word(pp.alphanums + "_\"'*/-+").setResultsName("name")
                    + pp.Optional(
                        pp.Char(",")
                        + pp.delimitedList(
                            pp.Word(pp.alphanums + "_\"'*/-+"), delim=","
                        ).setResultsName("arguments")
                    )
                    + pp.Suppress(")")
                ),
                pp.Group(
                    special_words
                    + pp.Optional(
                        pp.Word(pp.alphanums).setResultsName("source")
                        + pp.Suppress(".")
                    )
                    + pp.Word(pp.alphanums + "_\"'*/-+").setResultsName("name")
                ),
            ]
        )
    ).setResultsName("base_column")

    # Conditions grammer
    delimiter = pp.MatchFirst([pp.CaselessKeyword("AND"), pp.CaselessKeyword("OR")])
    equality_condition = pp.Group(
        pp.And(
            [
                column.setResultsName("LHS"),
                (
                    pp.Word("=<>")
                    | pp.CaselessKeyword("LIKE")
                    | pp.CaselessKeyword("IS")
                ),
                column.setResultsName("RHS"),
                pp.Optional(delimiter).setResultsName("delimiter"),
            ]
        )
    )
    value = pp.And([special_words, pp.Word(pp.alphanums + "_'-\"")])
    in_condition_clause = pp.Group(
        pp.And(
            [
                column.setResultsName("LHS"),
                pp.CaselessKeyword("IN"),
                pp.Group(
                    pp.And(
                        [
                            pp.Literal("("),
                            pp.Group(pp.delimitedList(value)),
                            pp.Literal(")"),
                        ]
                    )
                ).setResultsName("RHS"),
                pp.Optional(delimiter).setResultsName("delimiter"),
            ]
        )
    )
    condition_clause = pp.MatchFirst([equality_condition, in_condition_clause])
    condition_group = pp.Group(
        pp.And(
            [
                (
                    pp.Literal("(")
                    + pp.OneOrMore(condition_clause).setResultsName("condition_group")
                    + pp.Literal(")")
                )
                | pp.OneOrMore(condition_clause).setResultsName("condition_group"),
                pp.Optional(delimiter).setResultsName("delimiter"),
            ]
        )
    )

    all_conditions = pp.OneOrMore(condition_group).setResultsName("all_condition")

    case_column = pp.Group(
        pp.Optional(
            pp.CaselessKeyword("CASE")
            + pp.OneOrMore(
                pp.Group(
                    pp.CaselessKeyword("WHEN")
                    + all_conditions
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

    # Create Clause grammer
    create_clause = pp.Group(
        pp.And(
            [
                pp.CaselessKeyword("CREATE"),
                pp.CaselessKeyword("TABLE"),
                pp.Optional(pp.CaselessKeyword("IF NOT EXISTS")),
                pp.Word(pp.alphanums + "_.*").setResultsName("table_name"),
                pp.CaselessKeyword("AS"),
            ]
        )
    ).setResultsName("create")

    # Column Set grammar
    all_column = pp.Group(column + case_column + column_alias).setResultsName(
        "all_column"
    )

    columns = pp.delimitedList(all_column, delim=",").setResultsName("columns")

    column_clause = pp.CaselessKeyword("SELECT") + columns + pp.CaselessKeyword("FROM")

    # Table grammer
    table_grammer = pp.Group(pp.Word(pp.alphanums + "_.") + table_alias).setResultsName(
        "table_def"
    )

    # Where clause grammer
    where_clause = pp.Group(pp.CaselessKeyword("WHERE") + all_conditions)

    # Join clause grammer
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
        + all_conditions
    ).setResultsName("join")

    # Group by clause grammer
    group_clause = pp.CaselessKeyword("GROUP BY") + pp.Group(pp.delimitedList(column))

    # Order by clause grammer
    order_clause = pp.CaselessKeyword("ORDER BY") + pp.Group(pp.delimitedList(column))

    # Limit clause grammer
    limit_clause = pp.CaselessKeyword("LIMIT") + pp.Word(pp.nums)
    # print('eqsearch ', equality_condition.searchString('column1 = column2').dump())
    # print('insearch ', in_condition_clause.searchString('column1 IN (column4, \'5\', 6)').dump())
    # print(all_conditions.searchString('WHEN column1 IN (column2, column3) THEN column4'))
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
            pp.Optional(group_clause).setResultsName("groups"),
            pp.Optional(pp.Literal(";")),
            pp.Optional(order_clause).setResultsName("orders"),
            pp.Optional(pp.Literal(";")),
            pp.Optional(limit_clause),
            pp.Optional(pp.Literal(")")),
            pp.Optional(pp.Literal(";")),
        ]
    )
    # print("begin parse ", query)
    parsed_query = query_parser.parseString(query)
    # print("Result ", parsed_query.wheres1[0].all_condition)
    # Store the parsed value in Corresponding class
    table_data = Table()
    # k = 0
    # print(len(parsed_query.columns[k][1]), type(parsed_query.columns[k][1]))
    # try:
    #     print("WHERE ", parsed_query.wheres2[1])
    #     print(parsed_query.table_def)
    #     # print(parsed_query.columns[2].case_column.cases[0].all_condition[1])
    #     # print(parsed_query.columns[2].case_column.cases[1].result[0])
    # except:
    #     print("error")
    # if len(parsed_query.joins) > 0:
    #     print(parsed_query.joins[0])
    #     print(parsed_query.joins[0].all_condition[0])
    # print(parsed_query.dump())
    table_data.meta_data = parsed_query.dump()
    table_data.new_data_entry(parsed_query)

    return table_data


def get_follow_sources(
    table_name, column_names=[], tables=[]
) -> Tuple[list, list, Table, list]:
    source_columns = []
    source_tables = []
    match_table = Table()
    match_column = []
    for table in tables:
        if (
            table.name == table_name
            or (table.source_database + "." + table.name) == table_name
        ):
            for column in table.columns:
                if column.name in column_names:
                    match_table = table
                    match_column.append(column)
                    source_columns.extend(column.source_columns)

                    # Get Filter source columns
                    for where_filter in table.filters:
                        source_columns.extend(where_filter.source_columns)

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


def get_definition(table_name, column_name, tables, print_result=False):

    table_recreates = []
    source_columns = []
    source_tables = []

    source_columns, source_tables, current_table, current_columns = get_follow_sources(
        table_name, column_name, tables
    )
    assert current_table.name != "Default.Unset"

    table_recreate = current_table.recreate_query(current_columns)
    table_recreates.append(table_recreate)

    while len(source_tables) > 0:
        table_name = source_tables.pop()
        print("table_name ", table_name)
        column_names = []
        for column in source_columns:
            if column.source_table == table_name:
                column_names.append(column.column)
        # print(table_name, column_names)
        (
            source_columns_new,
            source_tables_new,
            current_table,
            current_columns,
        ) = get_follow_sources(table_name, column_names, tables)
        # print(current_table)
        if current_table != None and current_table.name != "Unset":
            print("current_table ", current_table.name)
            print('source_tables_new ', source_tables_new)
            table_recreate = current_table.recreate_query(current_columns)
            for table in source_tables_new:
                if table not in source_tables:
                    source_tables.append(table)
            for column in source_columns_new:
                if column not in source_columns:
                    source_columns.append(column)
            table_recreates.append(table_recreate)

    table_recreates.reverse()
    def_str = ""
    for table_recreate in table_recreates:
        if print_result:
            print(table_recreate)
        def_str += table_recreate + "\n"
    return table_recreates, def_str


def read_script(file_path):
    tables = []
    with open(file_path, "r") as f:
        main_query = f.read()
        queries = separate_queries(main_query)
        for query in queries:
            # print("\nQuery: \n")
            # print(query)
            # print("\nParsed Query: \n")
            table = parse_create_query(query)
            tables.append(table)
            # print(table)
            # print(table.meta_data)
    return tables


# Run if this file is run directly
if __name__ == "__main__":
    show_window = False
    if show_window:
        display_text("Welcome to the SQL Query Parser\n Choose File to Parse")
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open file", "", "All files (*.*)"
        )

        print("after file read")
        with open(file_path, "r"):
            tables = read_script(file_path)
            table_names = []
            for table in tables:
                table_names.append(table.name)
            print(table_names)
        if table_names != []:
            table_name = choose_elements(
                table_names, "Table Selection", "Select Table", allow_multiple=False
            )[0]

            column_names = []
            for table in tables:
                if table.name == table_name:
                    for column in table.columns:
                        column_names.append(column.name)
            column_names = choose_elements(
                column_names, "Column Selection", "Select Column", allow_multiple=True
            )
            print(table_name)
            print(column_names)
            definition, definition_str = get_definition(
                table_name, column_names, tables
            )
            to_print = display_text(definition_str)
            if to_print:
                # write defintion string in file
                with open("results/definition.hql", "w") as f:
                    f.write(definition_str)
    else:
        tables = []
        file_path = "queries/single_query.sql"
        with open(file_path, "r"):
            print("reading file")
            tables = read_script(file_path)
        table_name = "source2"
        column_name = ["column45"]
        definition, definition_str = get_definition(table_name, column_name, tables)
        print(definition_str)


# Example usage:
# specific_file = "complex_query.sql"
# parse_specific_file = True
# # List all files in queries directory
# if parse_specific_file:
#     tables = []
#     with open("queries/" + specific_file, "r") as f:
#         main_query = f.read()
#         queries = separate_queries(main_query)
#         for query in queries:
#             print("\nQuery: \n")
#             print(query)
#             print("\nParsed Query: \n")
#             table = parse_create_query(query)
#             tables.append(table)
#             # print(table)
#             # print(table.meta_data)
# else:
#     files = os.listdir("queries")
#     for i, sql_file in enumerate(files):
#         with open("queries/" + sql_file, "r") as f:
#             main_query = f.read()
#             queries = separate_queries(main_query)
#             for query in queries:
#                 result = parse_create_query(query)
# pprint(result)
