import pyparsing as pp
from typing import Any
from pprint import pprint


class BaseColumn:
    def __init__(self, parsed_dict: Any, alias_names=[], alias_list=[]):
        '''
        meta_data: contains the parsed dictionary
        name: name of the column
        source_table: source table of the column
        source_alias: source alias of the column
        real_column: boolean to check if it is a real column or a value
        argument_func: function applied to the column
        arguments: arguments of the function
        operator: operator applied to the column at the end
        col_argument: column argument of the function (BaseColumn)
        '''
        self.real_column = True
        self.meta_data = parsed_dict
        self.argument_func = (
            parsed_dict.argument_func if hasattr(parsed_dict, "argument_func") else ""
        )
        self.arguments = (
            parsed_dict.arguments if hasattr(parsed_dict, "arguments") else ""
        )
        self.operator = parsed_dict.operator if hasattr(parsed_dict, "operator") else ""
        self.name = parsed_dict.name[0] if hasattr(parsed_dict, "name") else ""
        self.source_alias = (
            parsed_dict.source[0] if hasattr(parsed_dict, "source") else ""
        )
        self.post_process(alias_names, alias_list)

        self.col_argument = None
        if hasattr(parsed_dict, "col_argument"):
            self.col_argument = BaseColumn(parsed_dict.col_argument, alias_names, alias_list)
            self.name = self.col_argument.name

        if self.argument_func == "" and self.source_alias == "":
            # define grammar to figure out if it is a column or a value
            value_grammar = pp.MatchFirst([pp.Word(pp.nums + "."), pp.quotedString()])
            if value_grammar.searchString(self.name) != []:
                self.real_column = False
        
    

    def post_process(self, alias_names, alias_list):
        """
        Post process the column
        """
        if self.source_alias in alias_list:
            self.source_table = alias_names[self.source_alias]
        else:
            self.source_table = ""

    def __str__(self):
        pprint(self.meta_data)

    def recreate_query(self):
        """
        Recreate the query for the column
        """
        query = ""
        if self.argument_func != "":
            query += self.argument_func + "("
            if self.col_argument != None:
                query += self.col_argument.recreate_query()
            for argument in self.arguments:
                query += argument + ", "
            query += ")"
        else:
            if self.source_table != "" and self.real_column:
                query += self.source_table + "."
            elif self.source_alias != "" and self.real_column:
                query += self.source_alias + "."
            query += self.name
        query += self.operator
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
        return hash((self.source_table, self.name, self.argument_func))
