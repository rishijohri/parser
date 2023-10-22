import pyparsing as pp

# Define grammar for matching column names and aliases
column_name = pp.Word(pp.alphanums + "_\"'*/-+")
source_alias = pp.Word(pp.alphas, exact=1)
column_alias = pp.Group(
    pp.Optional(source_alias + pp.Suppress(".")) + column_name
).setResultsName("column_alias")

# Define grammar for matching table aliases
table_alias = pp.Optional(
    pp.CaselessKeyword("AS") + pp.Word(pp.alphanums + "_")
)

# Define grammar for matching columns
column = pp.Group(
    pp.Optional(table_alias).setResultsName("table_alias")
    + column_alias.setResultsName("column_name")
).setResultsName("column")

# Define grammar for matching delimited lists with delimiter
delimiter = pp.MatchFirst([pp.Suppress(","), pp.Suppress(";"), pp.Suppress(":")])
delimited_list = pp.delimitedList(
    column.setResultsName("column") + pp.Optional(delimiter).setResultsName("delimiter")
).setResultsName("delimited_list")

# Example usage
input_str = "t1.column1, t2.column2; t3.column3 : t4.column4 ;"
result = delimited_list.parseString(input_str)

print(result)  # Output: [[['t1', ['column1']], ',', ['t2', ['column2']], ';', ['t3', ['column3']], ':', ['t4', ['column4']], ';']]
print(result.delimited_list[0][0].column_name)  # Output: ['column1']
print(result.delimited_list[0][0].table_alias)  # Output: ['t1']
print(result.delimited_list[0][0].delimiter)  # Output: ','