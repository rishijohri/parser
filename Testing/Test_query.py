# Python
import pyparsing as pp

quoted_string = pp.QuotedString('"')
word = pp.Word(pp.alphas)
word_not_in_quotes = pp.And([pp.NotAny(quoted_string), word])

print(word_not_in_quotes.parseString('hello'))  # ['hello']
print(word_not_in_quotes.parseString('"hello"'))  # ParseException: Found unwanted token, "'hello'"