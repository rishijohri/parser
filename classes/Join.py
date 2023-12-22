import pyparsing as pp
from .ConditionGroup import ConditionGroup
from .NewCondition import NewCondition
from collections import namedtuple
from typing import Any, Union
from pprint import pprint

BaseTable = namedtuple("BaseTable", ["table_name", "database"])

class Join:
    def __init__(self, parsed_dict: Any):
        '''
        meta_data: contains the parsed dictionary
        name: name of the table
        alias: alias of the table
        database: source of the table
        join_type: type of join
        condition: join condition (NewCondition)
        '''
        self.meta_data = parsed_dict
        self.sub_query_chk = False
        if hasattr(parsed_dict, "sub_query"):
            self.sub_query_chk = True
            self.sub_query = parsed_dict.sub_query
            self.name = parsed_dict.sub_query.table_def.table_name[0]
            self.alias = parsed_dict.sub_query.table_alias[0] if hasattr(parsed_dict.sub_query, "table_alias") else parsed_dict.sub_query.table_def.table_name
            self.database = parsed_dict.sub_query.table_def.source[0] if hasattr(parsed_dict.sub_query.table_def, "source") else "Default"
            self.sub_query_condition: Union[NewCondition, None] = NewCondition(parsed_dict.sub_query.where[0]) if hasattr(parsed_dict.sub_query, "where") else None
        else:
            self.name = parsed_dict.table_def.table_name[0]
            self.alias = parsed_dict.table_def.table_alias[0] if hasattr(parsed_dict.table_def, "table_alias") else parsed_dict.table_def.table_name
            self.database = parsed_dict.table_def.source[0] if hasattr(parsed_dict.table_def, "source") else "Default"
        self.join_type = parsed_dict.join_type
        self.condition = NewCondition(parsed_dict)

    def recreate_sub_query(self):
        query = ""
        query += "( SELECT "
        for column in self.sub_query.columns:
            query += column.definition[0].name[0] + ", "
        query = query[:-2]
        query += " FROM " + self.database + "." + self.name
        if self.sub_query_condition != None:
            query += " WHERE " + self.sub_query_condition.recreate_query() + " ) "
        return query
    
    def recreate_query(self, tabs=""):
        query = self.join_type + " "
        if self.sub_query_chk:
            query +=  self.recreate_sub_query() 
        else:
            query += self.name
        
        if self.alias != "":
            query += " " + self.alias
        query += " ON " + self.condition.recreate_query()
        return query
        

    def post_process(self, alias_names, alias_list):
        """
        Post process the join to fill in the source table
        """
        self.condition.post_process(alias_names, alias_list)
        self.source_columns = self.condition.source_columns

    def __str__(self):
        pprint(self.meta_data)

