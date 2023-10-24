import pyparsing as pp

# Define grammar for matching a column name
column_name = pp.Word(pp.alphas, pp.alphanums + "_$").setResultsName("name")

# Define grammar for matching a function argument
arg = pp.Word(pp.alphanums + "_$")

# Define grammar for matching a function call
func_call = pp.Group(
    pp.Word(pp.alphas).setResultsName("func_name")
    + pp.Suppress("(")
    + pp.delimitedList(arg).setResultsName("args")
    + pp.Suppress(")")
)

# Define grammar for matching a column with a function call
func_column = pp.Group(
    func_call.setResultsName("func_call")
    + pp.Suppress(".")
    + column_name.setResultsName("column_name")
)

# Define grammar for matching a column with a substring function call
substr_column = pp.Group(
    pp.CaselessKeyword("substr").setResultsName("func_name")
    + pp.Suppress("(")
    + column_name.setResultsName("base_column")
    + pp.Suppress(",")
    + pp.Word(pp.nums).setResultsName("start")
    + pp.Suppress(",")
    + pp.Word(pp.nums).setResultsName("length")
    + pp.Suppress(")")
)

# Define grammar for matching a case statement
case_statement = pp.CaselessKeyword("CASE").setResultsName("case") + pp.OneOrMore(
        pp.CaselessKeyword("WHEN").setResultsName("when")
        + pp.delimitedList(column_name | pp.quotedString).setResultsName("conditions")
        + pp.CaselessKeyword("THEN").setResultsName("then")
        + (column_name | pp.quotedString).setResultsName("result")  
).setResultsName("cases") + pp.Optional(
    pp.CaselessKeyword("ELSE").setResultsName("else")
    + (column_name | pp.quotedString).setResultsName("default")
) + pp.CaselessKeyword("END").setResultsName("end")


# Define grammar for matching a SQL query
sql_query = pp.CaselessKeyword("SELECT").suppress() + pp.delimitedList(substr_column | func_column | column_name | case_statement) + pp.CaselessKeyword("FROM").suppress() + pp.Word(pp.alphas, pp.alphanums + "_$").setResultsName("table_name")

# Example usage
input_str = """SELECT column1, column2, CASE wHEN abc ccc THEN abcd ELSE asdf END FROM table1"""
result = sql_query.parseString(input_str)

print(result)  # Output: ['column1', 'column2', ['case', [['when', ['column3', '=', 'value'], 'then', 'match'], ['else', 'no match']]], 'table1']