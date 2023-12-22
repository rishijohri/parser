import pyparsing as pp
from .Condition import Condition

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
        # print(parse_query)
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

