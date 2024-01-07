import pyparsing as pp
from typing import Any
from pprint import pprint

class BasicColumn:
    def __init__(self, name, source_table, source_alias, real_column=True):
        self.name = name
        self.source_table = source_table
        self.source_alias = source_alias
        self.real_column = real_column
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, BasicColumn):
            return False
        skip_alias = False
        if self.source_alias == "" or __value.source_alias == "":
            skip_alias = True

        return (
            self.name == __value.name
            and self.source_table == __value.source_table
            and (skip_alias or self.source_alias == __value.source_alias)
        )

    def __hash__(self):
        return hash((self.source_table, self.name))
    
    def recreate_query(self):
        query = ""
        if self.source_table != "" and self.real_column:
            query += self.source_table + "."
        elif self.source_alias != "" and self.real_column:
            query += self.source_alias + "."
        query += self.name
        return query

class BaseColumn:
    def __init__(self, parsed_dict: Any=[], alias_names=[], alias_list=[]):
        '''
        meta_data: contains the parsed dictionary
        name: name of the column
        source_table: source table of the column
        source_alias: source alias of the column
        real_column: boolean to check if it is a real column or a value
        aggregate_func: function applied to the column
        arguments: arguments of the function
        operator: operator applied to the column at the end
        col_argument: column argument of the function (BaseColumn)
        '''
        self.false_column = False
        self.name = ""
        self.operator = ""
        self.source_table = ""
        self.source_alias = ""
        self.leaf_column = False
        if parsed_dict == []:
            self.false_column = True
        self.real_column = True
        self.meta_data = parsed_dict
        self.source_columns = []
        self.source_arguments = []
        self.col_argument = []
        self.base_func = parsed_dict.base_func if hasattr(parsed_dict, "base_func") else ""
        self.aggregate_func = (
            parsed_dict.aggregate_func if hasattr(parsed_dict, "aggregate_func") else ""
        )
        self.arguments = (
            parsed_dict.arguments if hasattr(parsed_dict, "arguments") else []
        )
        for argument in self.arguments:
            base_column = BaseColumn(argument, alias_names, alias_list)
            self.source_arguments.append(base_column)
            # self.source_arguments += base_column.source_columns
            if base_column.real_column:
                self.source_columns.append(base_column)
                self.source_columns += base_column.source_columns
        if hasattr(parsed_dict, "definition"):
            for definition in parsed_dict.definition:
                base_column = BaseColumn(definition, alias_names, alias_list)
                self.col_argument.append(base_column)
                # self.col_argument += base_column.source_columns
                if base_column.real_column:
                    self.source_columns.append(base_column)
                    self.source_columns += base_column.source_columns
        
        self.operator = parsed_dict.operator if hasattr(parsed_dict, "operator") else ""
        self.name = parsed_dict.name[0] if hasattr(parsed_dict, "name") else ""
        self.source_alias = (
            parsed_dict.source[0] if hasattr(parsed_dict, "source") else ""
        )


        if self.name == "" and self.source_columns == []:
            self.real_column = False
        if self.real_column and self.aggregate_func == "" and self.source_alias == "":
            # define grammar to figure out if it is a column or a value
            value_grammar = pp.MatchFirst([pp.Word(pp.nums[0:1] + pp.nums + "."), pp.quotedString()])
            value_result = []
            try:
                value_result = value_grammar.parseString(self.name) # any value means it is not a column
            except:
                pass
            if value_result != [] or self.name.lower() in ["true", "false", "null"] :
                self.real_column = False
        
        if self.real_column:
            self.post_process(alias_names, alias_list)
        else:
            self.source_table = ""
        if self.source_table != "":
            self.real_column = True
        # print(self.meta_data)
    

    def post_process(self, alias_names, alias_list):
        """
        Post process the column
        """
        if self.source_alias in alias_list:
            self.source_table = alias_names[self.source_alias]
        else:
            self.source_table = ""
        
        if self.source_alias == "" and alias_list != []:
            self.source_alias = alias_names[alias_list[0]]
            self.source_table = alias_names[alias_list[0]]
        
    def __str__(self):
        pprint(self.meta_data)

    def recreate_query(self):
        """
        Recreate the query for the column
        """
        query = ""
        query += self.base_func + " " if self.base_func != "" else ""
        # print("RECREATE INITIATED ", self.name, self.aggregate_func)
        if self.false_column:
            return ""
        if self.real_column==False:
            query += self.name
            return query
        query += self.aggregate_func + "(" if self.aggregate_func != "" else ""

        if len(self.col_argument)==0:
            query += self.source_table + "." if self.source_table != "" else ""
            query += self.name if self.name != "" else ""
        else:
            for argument in self.col_argument:
                # print(argument.meta_data)
                query += argument.recreate_query() 

        for argument in self.source_arguments:
            query += ", " + argument.recreate_query()
        query += " as " + self.arguments[0] if self.aggregate_func.lower() == "cast" else ""
        query += ")" if self.aggregate_func != "" else ""
        query += " " + self.operator if self.operator != "" else ""
        # print("RECREATE ENDED ", self.name, self.aggregate_func)
        return query

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, BaseColumn):
            return False
        skip_alias = False
        if self.source_alias == "" or __value.source_alias == "":
            skip_alias = True

        return (
            self.name == __value.name
            and self.source_table == __value.source_table
            and (skip_alias or self.source_alias == __value.source_alias)
        )

    def __hash__(self):
        return hash((self.source_table, self.name, self.aggregate_func))
