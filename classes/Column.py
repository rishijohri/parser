import pyparsing as pp
from .ConditionGroup import ConditionGroup
from .BaseColumn import BaseColumn
from .Condition import Condition
from typing import Any
from .NewCondition import NewCondition
from pprint import pprint
from types import SimpleNamespace
def namespace_to_dict(obj):
    if isinstance(obj, SimpleNamespace):
        return {k: namespace_to_dict(v) for k, v in vars(obj).items()}
    elif isinstance(obj, list):
        return [namespace_to_dict(v) for v in obj]
    else:
        return obj

class CaseResult:
    def __init__(self, parsed_dict: Any, alias_names=[], alias_list=[]):
        '''
        condition: list of NewCondition objects
        result: list of results can be either a string or a CaseResult object
        leaf_cases: a list of boolean values to indicate if the result is a string or a CaseResult object
        '''
        #notes: result can be more than 1 if there is some arithmetic operation happening in the result
        self.meta_data = parsed_dict
        self.result = []
        self.condition: list[NewCondition] = []
        self.leaf_cases = []
        self.else_result = BaseColumn(parsed_dict.else_case.definition[0]) if hasattr(parsed_dict, "else_case") else ""
        self.source_tables = []
        self.source_columns = []
        for case in parsed_dict.cases:
            self.condition.append(NewCondition(case, alias_names, alias_list))
            if hasattr(case.result[0], "cases"):
                self.leaf_cases.append(False)
                self.result.append(CaseResult(case.result[0], alias_names, alias_list))
            else:
                self.leaf_cases.append(True)
                self.result.append(BaseColumn(case.result[0], alias_names, alias_list))
        
        # post process the case statement
        for condition in self.condition:
            self.source_tables.extend(condition.source_tables)
            self.source_columns.extend(condition.source_columns)
        for result in self.result:
            if isinstance(result, BaseColumn):
                if result.real_column:
                    self.source_tables.append(result.source_table)
                    self.source_columns.append(result)
        
        if self.else_result != "":
            if isinstance(self.else_result, BaseColumn):
                if self.else_result.real_column:
                    self.source_tables.append(self.else_result.source_table)
                    self.source_columns.append(self.else_result)
        
        self.source_tables = list(set(self.source_tables))
        self.source_columns = list(set(self.source_columns))
        return
        
    
    def recreate_query(self, tabs: str=""):
        query = tabs + "CASE \n"
        for i in range(len(self.condition)):
            if self.leaf_cases[i]:
                query += tabs + "WHEN " + str(self.condition[i].recreate_query()) + " THEN " + self.result[i].recreate_query() + "\n"
            else:
                query += tabs + "WHEN " + self.condition[i].recreate_query() + " THEN \n" + self.result[i].recreate_query(tabs="\t") + "\n"
        if self.else_result != "" and isinstance(self.else_result, BaseColumn):
            query += tabs + "ELSE " + self.else_result.recreate_query() + "\n"
        query += "END"
        return query

class Column:
    def __init__(self, parsed_dict: Any, alias_names=[], alias_list=[]):
        '''
        meta_data: contains the parsed dictionary
        name: name of the column
        alias: alias of the column
        source_columns: list of BaseColumn objects
        source_aliases: list of source aliases
        source_tables: list of source tables
        definition: Complete dictionary of the column definition
        '''
        self.meta_data = parsed_dict
        self.source_columns: list[BaseColumn] = []
        self.source_aliases = []
        self.source_tables = []
        self.alias = parsed_dict.column_alias[0][1] if hasattr(parsed_dict, "column_alias") else ""
        self.definition = parsed_dict.definition if hasattr(parsed_dict, "definition") else []
        self.row_number = " ".join(parsed_dict.row_num_col.partition_by[0]) if hasattr(parsed_dict, "row_num_col") else ""
        for definition in self.definition:
            self.source_columns.append(BaseColumn(definition, alias_names, alias_list))
        if len(self.source_columns) == 1:
            self.name = self.source_columns[0].name
        
        if len(self.source_columns) == 1:
            self.name = self.source_columns[0].name
        self.name = self.alias if self.alias != "" else self.name

        # handle case statement
        self.case_type = False
        self.conditions = []
        self.results = []
        if hasattr(parsed_dict, "case_column"):
            self.case_type = True
            self.case = CaseResult(parsed_dict.case_column, alias_names, alias_list)
            self.source_columns += self.case.source_columns
            self.source_tables += self.case.source_tables

        for source_column in self.source_columns:
            if source_column.real_column:
                self.source_aliases.append(source_column.source_alias)
                self.source_tables.append(source_column.source_table)
        
        self.source_aliases = list(set(self.source_aliases))
        self.source_tables = list(set(self.source_tables))
        # pprint(namespace_to_dict(self.meta_data))
    def recreate_query(self):
        """
        Recreate the query for the column
        """
        query = ""
        if self.case_type:
            query += self.case.recreate_query()
        else:
            for source_column in self.source_columns:
                query += source_column.recreate_query()
        if self.row_number != "":
            query = "ROW_NUMBER() OVER ( " + self.row_number + " )"
        if self.alias != "":
            query += " AS " + self.alias + "\n"
        return query

    def __str__(self):
        pprint(self.meta_data)

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

