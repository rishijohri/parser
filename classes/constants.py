import pyparsing as pp

special_words: pp.ParserElement = pp.And(
    [
        ~pp.CaselessKeyword("RIGHT"),
        ~pp.CaselessKeyword("LEFT"),
        ~pp.CaselessKeyword("INNER"),
        ~pp.CaselessKeyword("OUTER"),
        ~pp.CaselessKeyword("JOIN"),
        ~pp.CaselessKeyword("ON"),
        ~pp.CaselessKeyword("WHEN"),
        ~pp.CaselessKeyword("THEN"),
        ~pp.CaselessKeyword("ELSE"),
        ~pp.CaselessKeyword("END"),
        ~pp.CaselessKeyword("CASE"),
        ~pp.CaselessKeyword("WHERE"),
        ~pp.CaselessKeyword("GROUP"),
        ~pp.CaselessKeyword("ORDER"),
        ~pp.CaselessKeyword("LIMIT"),
        ~pp.CaselessKeyword("FROM"),
        ~pp.CaselessKeyword("SELECT"),
        ~pp.CaselessKeyword("CREATE"),
        ~pp.CaselessKeyword("TABLE"),
        ~pp.CaselessKeyword("AS"),
        ~pp.CaselessKeyword("IS"),
        ~pp.CaselessKeyword("LIKE"),
        ~pp.CaselessKeyword("IN"),
        ~pp.CaselessKeyword("NOT"),
        ~pp.CaselessKeyword("AND"),
        ~pp.CaselessKeyword("OR"),
        ~pp.CaselessKeyword("BETWEEN"),
        ~pp.CaselessKeyword("INTERVAL"),
        ~pp.CaselessKeyword("EXISTS"),
        # functions
        ~pp.CaselessKeyword("SUM"),
        ~pp.CaselessKeyword("AVG"),
        ~pp.CaselessKeyword("COUNT"),
        ~pp.CaselessKeyword("MIN"),
        ~pp.CaselessKeyword("MAX"),
        ~pp.CaselessKeyword("CONCAT"),
        ~pp.CaselessKeyword("SUBSTR"),
        ~pp.CaselessKeyword("TRIM"),
        ~pp.CaselessKeyword("COALESCE"),
        ~pp.CaselessKeyword("CAST"),
        ~pp.CaselessKeyword("DATE_FORMAT"),
        ~pp.CaselessKeyword("ADD_MONTHS"),
        ~pp.CaselessKeyword("CURRENT_DATE"),
        ~pp.CaselessKeyword("CURRENT_TIMESTAMP"),
        ~pp.CaselessKeyword("UNIX_TIMESTAMP"),
        ~pp.CaselessKeyword("FROM_UNIXTIME"),
        ~pp.CaselessKeyword("TO_DATE"),
        ~pp.CaselessKeyword("ROW_NUMBER"),
        ~pp.CaselessKeyword("ROW_NUMBER()"),
        ~pp.CaselessKeyword("OVER"),
        ~pp.CaselessKeyword("PARTITION"),
        ~pp.CaselessKeyword("BY"),
        ~pp.CaselessKeyword("ORDER"),
        ~pp.CaselessKeyword("ASC"),
        ~pp.CaselessKeyword("DESC"),
        ~pp.CaselessKeyword("DISTINCT"),
        # data types
        ~pp.CaselessKeyword("INT"),
        ~pp.CaselessKeyword("FLOAT"),
        ~pp.CaselessKeyword("DOUBLE"),
        ~pp.CaselessKeyword("DATE"),
        ~pp.CaselessKeyword("TIMESTAMP"),
        ~pp.CaselessKeyword("STRING"),
        ~pp.CaselessKeyword("VARCHAR"),
        ~pp.CaselessKeyword("CHAR"),
        ~pp.CaselessKeyword("BIGINT")
        ~pp.CaselessKeyword("BOOLEAN")
        ~pp.CaselessKeyword("DECIMAL")
        ~pp.CaselessKeyword("TINYINT")
        ~pp.CaselessKeyword("SMALLINT")
        ~pp.CaselessKeyword("BINARY")
    ]
)
assert isinstance(special_words, pp.ParserElement)
special_words_list = [
    "RIGHT",
    "LEFT",
    "INNER",
    "OUTER",
    "JOIN",
    "ON",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
    "CASE",
    "WHERE",
    "GROUP",
    "ORDER",
    "LIMIT",
    "FROM",
    "SELECT",
    "CREATE",
    "TABLE",
    "AS",
    "IN",
    "AND",
    "OR",
    "=",
    " ",
    ""
]

special_char_name = "_}{$:\"\'-*"