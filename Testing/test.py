# Python
import pyparsing as pp

grammar = pp.And([pp.Word(pp.alphas), pp.Word(pp.nums)])
print(grammar.parseString("abc123"))  # ['abc', '123']
print(grammar.parseString("abc 123"))  # ['abc', '123']