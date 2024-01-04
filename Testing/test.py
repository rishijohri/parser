# Python
import pyparsing as pp

nested_parentheses = pp.nestedExpr('(', ')')
result = nested_parentheses.parseString("(heelo(dhd) jjjsdjj(jj))")

print(result.asList())