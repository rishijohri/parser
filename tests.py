# Python
import pyparsing as pp

value_grammar = pp.MatchFirst([pp.Word(pp.nums[0:1] + pp.nums + "."), pp.quotedString()]) + pp.StringEnd()
# print(value_grammar.parseString("1.0"))
# print(value_grammar.parseString("column1"))
# print(value_grammar.parseString("column"))
# Test the grammar

