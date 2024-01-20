import pyparsing as pp
from typing import List
forbidden_words: List = ["RIGHT",
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
        "IS",
        "LIKE",
        "IN",
        "NOT",
        "AND",
        "OR",
        "BETWEEN",
        "INTERVAL",
        "EXISTS"]

function_names: List = ["SUM",
        "AVG",
        "COUNT",
        "MIN",
        "MAX",
        "CONCAT",
        "SUBSTR",
        "SUBSTRING",
        "TRIM",
        "COALESCE",
        "CAST",
        "DATE_FORMAT",
        "ADD_MONTHS",
        "CURRENT_DATE",
        "CURRENT_TIMESTAMP",
        "UNIX_TIMESTAMP",
        "FROM_UNIXTIME",
        "TO_DATE",
        "ROW_NUMBER",
        "ROW_NUMBER()",
        "RANK",
        "RANK(",
        "DENSE_RANK",
        "DENSE_RANK()",
        "DAY",
        "MONTH",
        "YEAR",
        "DATE",
        "DATE_ADD",
        "DATE_SUB",
        "DATE_DIFF",
        "DATE_TRUNC",
        "ROUND"]

expression_names: List = ["OVER",
        "PARTITION",
        "BY",
        "ORDER",
        "ASC",
        "DESC",
        "DISTINCT"]

data_types_list: List = ["INT",
        "FLOAT",
        "DOUBLE",
        "DATE",
        "TIMESTAMP",
        "STRING",
        "VARCHAR",
        "CHAR",
        "BIGINT",
        "BOOLEAN",
        "DECIMAL",
        "TINYINT",
        "SMALLINT",
        "BINARY"]

special_words: pp.ParserElement = pp.And(
    [~pp.CaselessKeyword(word) for word in forbidden_words]
    + [~pp.CaselessKeyword(word) for word in function_names]
    + [~pp.CaselessKeyword(word) for word in expression_names]
    + [~pp.CaselessKeyword(word) for word in data_types_list]
)

assert isinstance(special_words, pp.ParserElement)


special_char_name = "_}{$:\"\'-*"