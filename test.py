import pyparsing as pp
special_words = (
    ~pp.CaselessKeyword("RIGHT")
    + ~pp.CaselessKeyword("LEFT")
    + ~pp.CaselessKeyword("INNER")
    + ~pp.CaselessKeyword("OUTER")
    + ~pp.CaselessKeyword("JOIN")
    + ~pp.CaselessKeyword("ON")
    + ~pp.CaselessKeyword("WHEN")
    + ~pp.CaselessKeyword("THEN")
    + ~pp.CaselessKeyword("ELSE")
    + ~pp.CaselessKeyword("END")
    + ~pp.CaselessKeyword("CASE")
    + ~pp.CaselessKeyword("WHERE")
    + ~pp.CaselessKeyword("GROUP")
    + ~pp.CaselessKeyword("ORDER")
    + ~pp.CaselessKeyword("LIMIT")
    + ~pp.CaselessKeyword("FROM")
    + ~pp.CaselessKeyword("SELECT")
    + ~pp.CaselessKeyword("CREATE")
    + ~pp.CaselessKeyword("TABLE")
    + ~pp.CaselessKeyword("AS")
    + ~pp.CaselessKeyword("IN")
    + ~pp.CaselessKeyword("AND")
    + ~pp.CaselessKeyword("OR")
)
# Define grammar for matching a column name
column_name = pp.Word(pp.alphanums + "_")
aggregate_func = (
        pp.CaselessKeyword("SUM")
        | pp.CaselessKeyword("AVG")
        | pp.CaselessKeyword("COUNT")
    )
    # Base column Grammar (Column can have aggregation function)
column_name = pp.Optional(
    pp.Group(
        special_words+
         pp.Optional(
            aggregate_func.setResultsName("aggregate_func") + pp.Suppress("(")
        )
        + pp.Optional(
            pp.Word(pp.alphanums).setResultsName("source") + pp.Suppress(".")
        )
        + pp.Word(pp.alphanums + "_\"'*/-+").setResultsName("name")
        + pp.Optional(pp.Suppress(")"))
    )
).setResultsName("base_column")
# Define grammar for matching a value
value = pp.Word(pp.alphanums + "_'\"")

# Define grammar for matching a list of values
value_list = pp.Group(pp.Word("(") + pp.delimitedList(value) + pp.Word(")"))

# Define grammar for matching an IN condition
in_condition = pp.Group(
    column_name
    + pp.CaselessKeyword("IN")
    + value_list
)

# Example usage
input_str = "column1 IN (4, '5', 6)"
result = in_condition.parseString(input_str)

print(result)  # Output: [['column1', 'IN', ['4', "'5'", '6']]]