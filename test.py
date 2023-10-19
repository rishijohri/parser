import pyparsing as pp

# Define grammar for matching quoted strings
quoted_string = pp.quotedString()
# Example usage
input_str = 'This is a "test" of \'quoted strings\'.'
non_quoted_string = pp.Word(pp.alphanums + "_-.")

# Example usage
input_str = 'This is a "test" of \'quoted strings\'.'
result = (quoted_string | non_quoted_string).searchString(input_str)

for match in result:
    if quoted_string.searchString(match[0]):
        print(match[0], "is in quotes")
    else:
        print(match[0], "is not in quotes")