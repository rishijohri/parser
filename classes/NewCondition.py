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
        conditions: list of NewCondition objects
        delimiter: list of delimiters between conditions
        leaf_condition: True if the condition is a leaf condition (No child conditions attached)
        LHS: list of BaseColumn objects on the left hand side of the condition (Only for leaf conditions)
        RHS: list of BaseColumn objects on the right hand side of the condition (Only for leaf conditions)
        comparator: comparator between LHS and RHS (Only for leaf conditions)
        delimiter_leaf: delimiter for leaf conditions
        '''
        self.meta_data = parsed_dict
        self.conditions = []
        self.delimiter = []
        self.meta_data = parsed_dict
        self.leaf_conditions = True
        self.source_columns: list[BaseColumn] = []
        self.source_tables = []
        if hasattr(parsed_dict, "condition_group"):
            # non-leaf condition : Picks multiple conditions and delimiter and performs recursion
            self.leaf_condition = False
            for condition in parsed_dict.condition_group:
                self.conditions.append(NewCondition(condition, alias_names, alias_list))
                delim = condition.delimiter if hasattr(condition, "delimiter") and not hasattr(condition, "LHS") else ""
                self.delimiter.append(delim)
                self.source_columns.extend(self.conditions[-1].source_columns)
                self.source_tables.extend(self.conditions[-1].source_tables)

        if hasattr(parsed_dict, "LHS"):
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
                self.RHS = parsed_dict.RHS[0]
            elif self.comparator.lower() == "between":
                base_column__rhs1 = BaseColumn(parsed_dict.RHS1[0], alias_names, alias_list)
                base_column__rhs2 = BaseColumn(parsed_dict.RHS2[0], alias_names, alias_list)
                if base_column__rhs1.real_column:
                    self.source_columns.append(base_column__rhs1)
                if base_column__rhs2.real_column:
                    self.source_columns.append(base_column__rhs2)
                self.RHS = [base_column__rhs1, base_column__rhs2]
            else:
                self.RHS = []
                for definition in parsed_dict.RHS:
                    base_column = BaseColumn(definition, alias_names, alias_list)
                    self.RHS.append(base_column)
                    if base_column.real_column:
                        self.source_columns.append(base_column)
            self.delimiter_leaf: str = parsed_dict.delimiter if hasattr(parsed_dict, "delimiter") else ""

        for source_column in self.source_columns:
            if source_column.real_column:
                self.source_tables.append(source_column.source_table)
        
        self.source_columns = list(set(self.source_columns))
        self.source_tables = list(set(self.source_tables))

    def __str__(self):
        pprint(self.meta_data) 

    def recreate_sub_query(self, tabs=""):
        query = ""
        for word in self.RHS:
            assert(isinstance(word, str))
            query += word + " "
        return query
    def recreate_query(self, tabs=""):
        query = ""
        if self.leaf_condition:
            for i in range(len(self.LHS)):
                query += self.LHS[i].recreate_query()
            query += " "+self.comparator + " "
            if self.comparator.lower() == "in":
                assert(isinstance(self.RHS, list))
                if type(self.RHS[0])==str and self.RHS[0].lower() == "select":
                    query += "(" + self.recreate_sub_query() + ") "
                else:
                    query += "(" + ", ".join(self.RHS) + ") " # type: ignore
            elif self.comparator.lower() == "between":
                query += self.RHS[0].recreate_query() + " AND " + self.RHS[1].recreate_query()
            else:
                for i in range(len(self.RHS)):
                    query += self.RHS[i].recreate_query()
            if self.delimiter_leaf != "":
                query +=" " + self.delimiter_leaf + "  "
        else:
            for i in range(len(self.conditions)):
                if self.conditions[i].leaf_condition:
                    query += self.conditions[i].recreate_query()
                else:
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