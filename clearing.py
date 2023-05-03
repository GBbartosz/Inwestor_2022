import utilities as u


def clear_incorrect_cols():
    # usuwa kolumnny powstale w wyniku bledu przy imporcie danych

    def drop_col(c):
        if c in t_cols:
            cursor.execute(drop_query.format(t, c))

    cursor, wsj_conn, engine = u.create_sql_connection('wsjj')
    sql_table_list = u.get_all_tables(cursor)

    drop_query = 'ALTER TABLE {} DROP COLUMN [{}]'

    all_cols = []
    for t in sql_table_list:
        sql_query = '''
                    SELECT NAME 
                    FROM sys.columns 
                    WHERE object_id = OBJECT_ID('dbo.{}')
                    '''.format(t)
        t_cols = cursor.execute(sql_query).fetchall()
        t_cols = [x[0] for x in t_cols]
        drop_col('1-Jan-0001')
        drop_col('Unnamed: 3')
        drop_col('Unnamed: 4')
        drop_col('Unnamed: 5')
        drop_col('5-qtr trend')
        drop_col('5-year trend')
        all_cols += t_cols
    all_cols = list(set(all_cols))
    all_cols.sort()
    print(all_cols)
