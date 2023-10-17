import pyparsing as pp

# Define grammar for matching words between parentheses
paren_expr = pp.nestedExpr('(', ')')

# Example usage
input_str = 'This is (a test) of the (paren_expr) grammar.'
result = paren_expr.searchString(input_str)

# Print matched words
for match in result:
    print(match[0])