import pyparsing as pp
from .constants import special_char_name, special_words_list, special_words
from .BaseColumn import BaseColumn
from pprint import pprint
from typing import Any

class NewCondition:
    def __init__(self, parsed_dict: Any, alias_names=[], alias_list=[]):
        '''
        meta_data: contains the parsed dictionary. 
            Expected to have "condition_group" and optionally delimiter
                or ("LHS" and "RHS" and "comparator" and optionally "delimiter")
        '''
        self.conditions = []
        self.delimiter = []
        self.meta_data = parsed_dict
        self.leaf_condition = True
        self.source_columns: list[BaseColumn] = []
        if hasattr(parsed_dict, "condition_group"):
            # non-leaf condition : Picks multiple conditions and delimiter and performs recursion
            self.leaf_condition = False
            for condition in parsed_dict.condition_group:
                self.conditions.append(NewCondition(condition, alias_names, alias_list))
                delim = condition.delimiter if hasattr(condition, "delimiter") else ""
                self.delimiter.append(delim)
        elif hasattr(parsed_dict, "LHS"):
            # leaf condition : Picks single LHS - RHS + comparator condition
            self.leaf_condition = True
            self.LHS = []
            for definition in parsed_dict.LHS:
                base_column = BaseColumn(definition, alias_names, alias_list)
                self.LHS.append(base_column)
                if base_column.real_column:
                    self.source_columns.append(base_column)
            self.comparator = parsed_dict.comparator if hasattr(parsed_dict, "comparator") else "##"
            if self.comparator.lower() == "in":
                self.RHS = parsed_dict.RHS
            else:
                self.RHS = []
                for definition in parsed_dict.RHS:
                    base_column = BaseColumn(definition, alias_names, alias_list)
                    self.RHS.append(base_column)
                    if base_column.real_column:
                        self.source_columns.append(base_column)
            self.delimiter_leaf: str = parsed_dict.delimiter if hasattr(parsed_dict, "delimiter") else ""


    def __str__(self):
        pprint(self.meta_data) 

    def recreate_query(self, tabs=""):
        query = ""
        if self.leaf_condition:
            for i in range(len(self.LHS)):
                query += self.LHS[i].recreate_query()
            query += " "+self.comparator + " "
            if self.comparator.lower() == "in":
                query += "(" + ", ".join(self.RHS) + ") "
            else:
                for i in range(len(self.RHS)):
                    query += self.RHS[i].recreate_query()
            if self.delimiter_leaf != "":
                query +=" " + self.delimiter_leaf + "  "
        else:
            for i in range(len(self.conditions)):
                query += "(" + self.conditions[i].recreate_query() + ")"
                query += " " + self.delimiter[i] + " "
        return query

    def post_process(self, alias_names, alias_list):
        """
        Post process the condition to fill in the source table
        """
        if self.leaf_condition:
            for source_column in self.source_columns:
                source_column.post_process(alias_names, alias_list)
        else:
            for condition in self.conditions:
                condition.post_process(alias_names, alias_list)
            self.source_columns = []
            for condition in self.conditions:
                self.source_columns.extend(condition.source_columns)
    def extract_columns(self):
        """
        Extracts the source columns and source table aliases from the condition
        """
        # define grammer for matching column names
        

# Python
# import pyparsing as pp

# # Define a placeholder for a case statement
# case_stmt = pp.Forward()

# # Define the grammar for a case statement
# case_stmt << ("CASE" + pp.OneOrMore(pp.Group("WHEN" + case_stmt + "THEN" + pp.Word(pp.alphas)) + pp.Optional("ELSE" + pp.Word(pp.alphas)) + "END")

# # Test the grammar
# print(case_stmt.parseString("CASE WHEN CASE WHEN CASE WHEN x THEN y ELSE z END THEN a ELSE b END THEN c END"))