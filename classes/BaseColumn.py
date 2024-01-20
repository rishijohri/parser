import pyparsing as pp
from typing import Any
from pprint import pprint

class BaseColumn:
    def __init__(self, parsed_dict: Any=[], alias_names=[], alias_list=[]):
        '''
        parsed_dict is the value contained within the definition attribute of the dict (Not the definition attribute itself)
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
        self.case_column = False
        if parsed_dict == []:
            self.false_column = True
            return
        self.name = parsed_dict.name[0] if hasattr(parsed_dict, "name") else ""
        self.operator = parsed_dict.operator if hasattr(parsed_dict, "operator") else ""
        self.source_alias = parsed_dict.source[0] if hasattr(parsed_dict, "source") else ""
        self.source_aliases = []
        self.source_table = ""
        self.source_tables = []
        self.source_columns = []
        self.col_argument = []
        self.arguments = []
        self.base_func = parsed_dict.base_func + " " if hasattr(parsed_dict, "base_func") else ""
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
        elif hasattr(parsed_dict, "cases"):
            self.real_column = True
            self.case_column = True
            self.cases = []
            self.cases_dict = parsed_dict.cases
            self.case_val = Cases(parsed_dict, alias_names, alias_list)
            self.source_columns.extend(self.case_val.source_columns)
            self.source_tables.extend(self.case_val.source_tables)
                
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
        query += self.base_func
        # print("RECREATE INITIATED \n\t", self.name, "\n\t",self.aggregate_func, "\n\t",self.meta_data)
        if self.false_column:
            return ""
        if self.real_column==False:
            query += self.name + " "+self.operator
            return query
        if self.case_column:
            query += self.case_val.recreate_query()
        elif self.aggregate_func != "":
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


from classes.NewCondition import NewCondition

class Cases:
    def __init__(self, parsed_dict, alias_names=[], alias_list=[]):
        '''
        Invoked when parsed dict contains the cases attribute
        '''
        if not hasattr(parsed_dict, "cases"):
            return
        self.meta_data = parsed_dict
        self.alias_names = alias_names
        self.alias_list = alias_list
        self.else_case = parsed_dict.else_case if hasattr(parsed_dict, "else_case") else []
        self.cases = []
        self.cases_dict = parsed_dict.cases
        self.source_columns = []
        self.source_tables = []
        for case in self.cases_dict:
            condition = NewCondition(case, self.alias_names, self.alias_list)
            self.source_columns.extend(condition.source_columns)
            self.source_tables.extend(condition.source_tables)
            if hasattr(case.result, 'definition'):
                result = [BaseColumn(res, self.alias_names, self.alias_list) for res in case.result.definition]
                for res in result:
                    if res.real_column:
                        self.source_columns.append(res)
                        self.source_columns.extend(res.source_columns)
                        self.source_tables.append(res.source_table)
            else:
                result = []
            self.cases.append((condition, result))
        
        
        if self.else_case != []:
            if hasattr(self.else_case, 'definition'):
                self.else_case = [BaseColumn(val, self.alias_names, self.alias_list) for val in self.else_case.definition] # type: ignore
                for val in self.else_case:
                    if val.real_column:
                        self.source_columns.append(val)
                        self.source_columns.extend(val.source_columns)
                        self.source_tables.append(val.source_table)
            else:
                self.else_case = []

        self.source_columns = list(set(self.source_columns))
        self.source_tables = list(set(self.source_tables))
        

    def recreate_query(self, tabs=""):
        query = "CASE \n"
        tabs += "\t"
        for case in self.cases:
            condition, result = case
            query += tabs + "WHEN " + condition.recreate_query() + " THEN " + " ".join([res.recreate_query() for res in result]) + "\n"
        if self.else_case != []:
            query += tabs + "ELSE " + " ".join([res.recreate_query() for res in self.else_case]) + "\n"
        query += "END "
        return query 
    
    def post_process(self):
        for case in self.cases:
            condition, result = case
            condition.post_process()
            for res in result:
                res.post_process()