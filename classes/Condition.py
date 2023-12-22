import pyparsing as pp
from .constants import special_char_name, special_words_list, special_words
from .BaseColumn import BaseColumn

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
            for token in condition:
                if type(token) == pp.ParseResults:
                    parse_token = column_def.searchString(token.name)
                    if len(parse_token) and parse_token[0][0] == token.name:
                        base_col = BaseColumn(
                            parse_query=token.base_column, column_name=str(token.name), source_alias=str(token.source)
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
                        LHS_name = self.recreate_column(condition.LHS, source_columns)
                        RHS_name = self.recreate_column(condition.RHS, source_columns)
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
