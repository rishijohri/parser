# Python
import pyparsing as pp

# Define a placeholder for a case statement
case_stmt = pp.Forward()

# Define the grammar for a case statement
word = ~pp.CaselessKeyword("END") + ~pp.CaselessKeyword("WHEN") + ~pp.CaselessKeyword("CASE") + ~pp.CaselessKeyword("THEN") + pp.Word(pp.alphas)
case_stmt << pp.Group(
    "CASE"
    + pp.OneOrMore(
        pp.Group(
            "WHEN"
            + word
            + "THEN"
            + pp.MatchFirst([word, case_stmt])
        )
    )
    + pp.Optional("ELSE" + word)
    + "END"
)

# Test the grammar
print(case_stmt.parseString("CASE WHEN x THEN CASE WHEN y THEN z END END"))
