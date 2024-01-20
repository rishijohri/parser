import pyparsing as pp
from .BaseColumn import BaseColumn
from typing import Any, Union
from pprint import pprint
from types import SimpleNamespace
def namespace_to_dict(obj):
    if isinstance(obj, SimpleNamespace):
        return {k: namespace_to_dict(v) for k, v in vars(obj).items()}
    elif isinstance(obj, list):
        return [namespace_to_dict(v) for v in obj]
    else:
        return obj


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
        self.source_expression: list[Union[str, BaseColumn]] = []
        self.source_aliases = []
        self.source_tables = []
        self.name = ""
        self.alias = parsed_dict.column_alias[0][1] if hasattr(parsed_dict, "column_alias") else ""
        self.definition = parsed_dict.definition if hasattr(parsed_dict, "definition") else []
        self.definition_group = parsed_dict.definition_group if hasattr(parsed_dict, "definition_group") else []
        self.row_number = " ".join(parsed_dict.row_num_col.partition_by[0]) if hasattr(parsed_dict, "row_num_col") else ""
        for definition in self.definition:
            if type(definition) == str:
                self.source_expression.append(definition)
            else:
                base_column = BaseColumn(definition, alias_names, alias_list)
                self.source_expression.append(base_column)
                if base_column.real_column:
                    self.source_columns.append(base_column)
                    self.source_columns += base_column.source_columns
        for source_column in self.source_columns:
            if source_column.real_column and source_column.name != "":
                self.name = source_column.name
                break
        self.name = self.alias if self.alias != "" else self.name
        

        for source_column in self.source_columns:
            if type(source_column) == BaseColumn and source_column.real_column:
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
        if self.row_number != "":
            query = "ROW_NUMBER() OVER ( " + self.row_number + " )"
            if self.alias != "":
                query += " AS " + self.alias + "\n"
            return query
        
        for source_column in self.source_expression:
            if type(source_column) == str:
                query += source_column + " "
            elif type(source_column) == BaseColumn:
                query += source_column.recreate_query() 
        
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

