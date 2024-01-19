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
        self.meta_data = parsed_dict
        self.false_column = False
        self.real_column = False
        if parsed_dict == []:
            self.false_column = True
            return
        self.name = parsed_dict.name[0] if hasattr(parsed_dict, "name") else ""
        self.operator = parsed_dict.operator if hasattr(parsed_dict, "operator") else ""
        self.source_alias = parsed_dict.source[0] if hasattr(parsed_dict, "source") else ""
        self.source_table = ""
        self.source_columns = []
        self.col_argument = []
        self.arguments = []
        self.base_func = parsed_dict.base_func if hasattr(parsed_dict, "base_func") else ""
        self.aggregate_func = (
            parsed_dict.aggregate_func if hasattr(parsed_dict, "aggregate_func") else ""
        )

        if self.aggregate_func != "":
            self.real_column = True
            col_argument = parsed_dict.col_argument.definition if hasattr(parsed_dict, "col_argument") else []
            arguments = parsed_dict.arguments if hasattr(parsed_dict, "arguments") else []
            for argument in col_argument:
                if type(argument) == str:
                    self.col_argument.append(argument)
                else:
                    base_column = BaseColumn(argument, alias_names, alias_list)
                    self.col_argument.append(base_column)
                    if base_column.real_column:
                        self.source_columns.append(base_column)
                        self.source_columns += base_column.source_columns
            for argument in arguments:
                if type(argument) == str:
                    self.arguments.append(argument)
                elif hasattr(argument, "definition"):
                    for definition in argument.definition:
                        base_column = BaseColumn(definition, alias_names, alias_list)
                        self.arguments.append(base_column)
                        if base_column.real_column:
                            self.source_columns.append(base_column)
                            self.source_columns += base_column.source_columns
                
        elif self.name != "":
            self.real_column = True
        if self.real_column:
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
        # print("RECREATE INITIATED \n\t", self.name, "\n\t",self.aggregate_func, "\n\t",self.meta_data)
        if self.false_column:
            # print("False Column Encounter")
            return ""
        if self.real_column==False:
            # print("Unreal Column Encounter")
            query += self.name + " "+self.operator
            return query
        if self.aggregate_func != "":
            query += self.aggregate_func + "("
            for argument in self.col_argument:
                if type(argument) == BaseColumn:
                    query += argument.recreate_query()
                else:
                    query += argument
            if self.aggregate_func.lower() == "cast":
                query += " as "
            for argument in self.arguments:
                query += ", " + argument.recreate_query()
            query += ")"
        else:
            query += self.source_table + "." if self.source_table != "" else ""
            query += self.name if self.name != "" else ""
        
        query += " " + self.operator if self.operator != "" else ""
        # print("RECREATE ENDED \n\t", self.name, "\n\t", self.aggregate_func)
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
