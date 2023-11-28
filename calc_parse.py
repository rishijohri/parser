import pyparsing as pp

file_path = "projects/complex_query.dtsx"


def parse_dtsx(file_path):
    # define grammar
    create_grammar = pp.Keyword("CREATE MEMBER CURRENTCUBE.")
    calc_member = pp.Word(pp.alphanums + "_" + "[" + "]" + "/" + ".")
    grammar = (
        create_grammar + calc_member + pp.Keyword("AS") + calc_member + pp.restOfLine
    )
    main_grammar = pp.OneOrMore(grammar)

    with open(file_path, "r") as f:
        script = f.read()
        parse_grammar = grammar.parseString(script)
        print(parse_grammar)


if __name__ == "__main__":
    parse_dtsx(file_path)
