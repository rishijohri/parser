import re
import pyparsing as pp

# write parse_create_table_as_select_query function here using pyparsing


def parse_query(query):
    # define grammar
    select_stmt = pp.Keyword("SELECT") + pp.Word(pp.alphas+"_*")
    from_stmt = pp.Keyword("FROM") + pp.Word(pp.alphas+"_*")
    where_stmt = pp.Keyword("WHERE") + pp.Word(pp.alphas+"_*")
    stmt = select_stmt + from_stmt + where_stmt
    # parse
    result = stmt.parseString(query)
    # return
    return result


def parse_create_table_as_select_query(query):
    """Parses a SQL Create table as select query and stores all the columns, source table, filters, and columns used from the source table.

    Args:
      query: A SQL Create table as select query.

    Returns:
      A dictionary containing the following keys:
        columns: A list of all the columns in the new table.
        source_table: The name of the source table.
        filters: A list of all the filters in the SELECT statement.
        source_table_columns: A list of all the columns used from the source table.
    """

    # Extract the column names from the CREATE TABLE statement.
    create_statement_regex = 'CREATE\sTABLE\s(\w+)\sAS\s'
    select_statement_regex = 'SELECT\s(.*)\s'
    from_statement_regex = 'FROM\s(\w+(\.\w+)?)\s(\w+\s)?'
    where_statement_regex = 'WHERE\s(.*)'
    # join_statement_regex = '(\w+(\.\w+)?)\s(JOIN|INNER JOIN|LEFT JOIN|RIGHT JOIN|FULL OUTER JOIN)\s(\w+(\.\w+)?)\s(\w+\s)?ON\s(.*)'
    join_statement_regex = ''
    group_by_statement_regex = 'GROUP BY\s(.*)'
    order_by_statement_regex = 'ORDER BY\s(.*)'
    limit_statement_regex = 'LIMIT\s(.*)'
    # print(re.compile(join_statement_regex).match('JOIN sdb.source2 b on a.skey = b.pkey'))
    query_regex = re.compile(
        f'{create_statement_regex}{select_statement_regex}{from_statement_regex}({where_statement_regex})?({join_statement_regex})*({where_statement_regex})?({group_by_statement_regex})?({order_by_statement_regex})?({limit_statement_regex})?;')
    # query_regex = re.compile('CREATE\sTABLE\s(\w+)\sAS\sSELECT\s(.*)\s(WHERE\s(.*))?;')
    query_match = query_regex.match(query)
    if query_match is None:
        raise ValueError('Invalid SQL Create table as select query.')
    columns = [s.strip() for s in query_match.group(2).split(',')]

    # Extract Table name
    table_name = query_match.group(1).strip()

    # Extract the source table name from the SELECT statement
    source_table = query_match.group(3).strip()
    alias = query_match.group(5)
    if alias is not None:
        source_table_alias = alias.strip()


    # Extract the filters from the SELECT statement.
    filters = []
    filter_group = query_match.group(7)
    if filter_group is not None:
        filters = [f.strip() for f in filter_group.split('AND')]

    # Identify the columns used from the source table.
    source_table_columns = []
    if alias is None:  # No alias specified.
        source_table_columns = columns
    else:
        for column in columns:
            if column.startswith(source_table_alias + '.'):
                source_table_columns.append(
                    column[len(source_table_alias) + 1:])

    return {
        'columns': columns,
        'source_table': source_table,
        'filters': filters,
        'source_table_columns': source_table_columns
    }

# Example usage:


query = 'CREATE TABLE new_table AS SELECT a.column1, column2 FROM sdb.source a LEFT JOIN sdb.source2 b ON a.skey = b.pkey WHERE column1 = 1 AND column2 = 2 ;'
parsed_query = parse_create_table_as_select_query(query)

print('Columns:', parsed_query['columns'])
print('Source table:', parsed_query['source_table'])
print('Filters:', parsed_query['filters'])
print('Source table columns:', parsed_query['source_table_columns'])


# Output:

# Columns: ['column1', 'column2']
# Source table: source_table
# Filters: ['"column1" = 1', '"column2" = 2']
# Source table columns: ['column1', 'column2']
