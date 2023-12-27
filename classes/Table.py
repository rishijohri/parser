import pyparsing as pp
from .ConditionGroup import ConditionGroup
from .Column import Column
from .Join import Join
from .NewCondition import NewCondition
from typing import Any, List, Union
class Table:
    def __init__(self, name: str = "Unset"):
        self.database: str = "Default"
        self.source_database: str = "Default"
        self.source_table: str = ""
        self.name : str = name
        self.source_alias: str = ""
        self.columns : List[Column] = []
        self.joins: List[Join] = []
        self.sub_query_chk: bool = False
        # self.filters = Condition([], result="NULL", condition_type="None")
        self.filters = None
        self.group_by = []
        self.order_by = []
        self.limit = None
        self.meta_data = None
        self.alias_list = []
        self.alias_names = {}

    def __str__(self):
        col_str = "\t--------------------------------\n"
        for col in self.columns:
            col_str += str(col)
            col_str += "\t--------------------------------\n"
        source_information = (
            "<>" * 25
            + f" \n Table name: {self.name}\n"
            + f" Source database: {self.source_database}\n "
            + f"Source table: {self.source_table}\n "
            + f"Source alias: {self.source_alias}\n"
            + "<>" * 25
        )
        join_info = ""
        for join in self.joins:
            join_info += str(join)
            join_info += "\t--------------------------------\n"
        return (
            f"{source_information}\n "
            + f"Filters: {self.filters}\n "
            + f"Joins: \n{join_info}\n"
            + f"Group by: {self.group_by}\n"
            + f"Order by: {self.order_by}\n"
            + f"Limit: {self.limit}\n"
            + f"Columns:\n{col_str}\n"
        )

    def alias_solver(self):
        """
        Figures out the relationship between aliases and tables names
        """
        alias_names = {}
        alias_list = []
        alias_names[self.source_alias] = self.source_table
        alias_list.append(self.source_alias)
        for join in self.joins:
            alias_names[join.alias] = join.name
            alias_list.append(join.alias)
        self.alias_names = alias_names
        self.alias_list = alias_list

    
    def data_entry(self, parsed_dict):
        '''
        Data entry via parsed dictionary
        '''
        self.meta_data = parsed_dict
        self.name =   parsed_dict.create.table_name[0] if hasattr(parsed_dict.create, "table_name") else "Unset"
        self.database =   parsed_dict.create.source[0] if hasattr(parsed_dict.create, "source") else "Default"

        # Source table information
        if hasattr(parsed_dict, "table_def"):
            self.source_table = parsed_dict.table_def.table_name[0]
            self.source_database = parsed_dict.table_def.source[0] if hasattr(parsed_dict.table_def, "source") else "Default"
            self.source_alias =  parsed_dict.table_def.table_alias[0] if hasattr(parsed_dict.table_def, "table_alias") else ""
        elif hasattr(parsed_dict, "sub_query"):
            self.sub_query_chk = True
            self.sub_query = parsed_dict.sub_query
            self.sub_query_condition: Union[NewCondition, None] = NewCondition(parsed_dict.sub_query.where[0]) if hasattr(parsed_dict.sub_query, "where") else None
            self.source_table = parsed_dict.sub_query.table_def.table_name[0]
            self.source_database = parsed_dict.sub_query.table_def.source[0] if hasattr(parsed_dict.sub_query.table_def, "source") else "Default"
            self.source_alias =  parsed_dict.sub_query.table_def.table_alias[0] if hasattr(parsed_dict.sub_query.table_def, "table_alias") else ""
        #Joins information
        if hasattr(parsed_dict, "joins"):
            for join in parsed_dict.joins:
                self.joins.append(
                    Join(
                        parsed_dict=join
                    )
                )
        # get alias names
        self.alias_solver()

        # parse where filters
        if hasattr(parsed_dict, "wheres2"):
            self.filters = NewCondition(parsed_dict=parsed_dict.wheres2[0], alias_names=self.alias_names, alias_list=self.alias_list)
        elif hasattr(parsed_dict, "wheres1"):
            self.filters = NewCondition(parsed_dict=parsed_dict.wheres1[0], alias_names=self.alias_names, alias_list=self.alias_list)

        # parse columns
        for column in parsed_dict.columns:
            self.columns.append(
                Column(
                    parsed_dict=column,
                    alias_names=self.alias_names,
                    alias_list=self.alias_list
                )
            )
        
        # parse group by
        if hasattr(parsed_dict, "group_by"):
            for column in parsed_dict.group_by[0].columns:
                self.group_by.append(Column(column, self.alias_names, self.alias_list))
        
        # parse order by
        if hasattr(parsed_dict, "order_by"):
            for column in parsed_dict.order_by[0].columns:
                self.order_by.append(Column(column, self.alias_names, self.alias_list))
        
        # post process joins
        for join in self.joins:
            join.post_process(self.alias_names, self.alias_list)
        
    def recreate_sub_query(self):
        query = ""
        query += "( SELECT "
        for column in self.sub_query.columns:
            if hasattr(column, "definition"):
                query += column.definition[0].name[0] + ", "
            elif hasattr(column, "column_alias"):
                query += column.column_alias[0][1] + ", "
        query = query[:-2]
        query += " FROM " + self.database + "." + self.name
        if self.sub_query_condition != None:
            query += " WHERE " + self.sub_query_condition.recreate_query()
        query += " ) "
        return query

    def recreate_query(self, columns=[]):
        """
        For the column given in the list, recreate the query for only those columns
        """
        query = ""
        # Add create statement
        query += f"CREATE TABLE {self.database}.{self.name} AS \n"
        # Add column statement
        query += "SELECT "
        combine_source_tables = []
        for column in columns:
            for source_table in column.source_tables:
                if source_table not in combine_source_tables:
                    combine_source_tables.append(source_table)
        for i, column in enumerate(columns):
            query += column.recreate_query() 
            query += ", \n" if i < len(columns) - 1 else "\n"
        # Add from statement
        query += "FROM "
        if self.sub_query_chk:
            query += self.recreate_sub_query()
        else:
            query += self.source_database + "." + self.source_table
        query += "\n"
        # print("combine_source_columns", combine_source_tables)
        # Add join statement
        for join in self.joins:
            # print(join.table)
            query += join.recreate_query()
            query += "\n"

        # Add where statement
        if self.filters != None:
            query += "WHERE " + self.filters.recreate_query() + "\n"

        # Add group by statement
        if self.group_by != []:
            query += "GROUP BY "
            for i, column in enumerate(self.group_by):
                query += column.recreate_query()
                query += ", " if i < len(self.group_by) - 1 else "\n"
        
        # Add order by statement
        if self.order_by != []:
            query += "ORDER BY "
            for i, column in enumerate(self.order_by):
                query += column.recreate_query()
                query += ", " if i < len(self.order_by) - 1 else "\n"
        query += ";"
        return query
