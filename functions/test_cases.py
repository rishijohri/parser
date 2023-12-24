case_column_tests = [
    """CASE 
        WHEN x = 1 THEN y33
        when y=2 then z2
        ELSE z END""",
    """CASE WHEN x=tyy THEN y 
            WHEN a<>"${hiveconf:start_dt} THEN 
                CASE WHEN b=1 THEN c 
                ELSE d END 
            ELSE e END""",
            '''
case
        when column4 = 5 AND column45 = 25 then 1
        when c.column4 is 6 then 2
        else 0
    end
'''
]

column_tests = [
    '''"x"''',
    '''source.column3''',
    '''MIN(source.column3)''',
    '''MAX(source.column2) - MAX(source.column4) + source1''',
    '''CAST(NULL as INT)''',
    '''CAST(source.column2 AS INT)''',
]

all_condition_tests = [
    '''(x = "${hiveconf:start_dt}" and y = "${hiveconf:end_dt}")''',
    '''(
        x = "${hiveconf:start_date}" and y = "${hiveconf:end_date}"
        ) or 
        (
            x = "${hiveconf:start_dt}" and 
            ( 
                y = "${hiveconf:end_dt} and z = "${hiveconf:z}"
            ) 
        )''',
]

join_tests = [
    '''
    left join source1.table1 t2 on t1.id = t2.id
    ''',
    '''
    JOIN ( select id, name from source1.table1 ) 
    t2 on t1.id = t2.id
    '''
]

basic_table_tests = [
    '''
    SELECT a1 - a2 as aajj, a2, a3 from source1.table1 t3
    ''',
    '''
    select MAX(a1) as a11, COALESCE(a2, 99) as a22, a3 from source1.table1 t3 where a3 = 1
    ''',
    '''
    select
            column1,
            column2,
            column3
        from
            sourc4.table1
            where column4 = "NANAMI"
    '''
]