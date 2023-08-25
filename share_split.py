import utilities as u


def get_name_of_column_with_indicator_names(tdf):
    column_name = tdf.columns[1]
    return column_name


def get_columns_only_in_sql(df, sql_df):
    res = []
    for sqlc in sql_df.columns:
        if sqlc not in df.columns:
            res.append(sqlc)
    res = u.get_rid_of_index_and_indicators(res)
    return res


def compare_changes(changel, share_ind, s_l, ssql_l):  # 2 ostatnie dodane tylko dla printu
    outcome = True
    c0 = changel[0]
    for c in changel:
        if c != 0 and c0 != 0:  # byl blad dzielenia przez 0 gdy danego wskaznika nie bylo na wsj w sql zapisywal sie jako 0 (RJF)
            res = c / c0
            if res < 0.9 or res > 1.1:
                print('Error stock split change for {}: {}'.format(share_ind, changel))
                outcome = False
    return outcome


def shorten_df_to_chosen_fragment(tdf, chosen_columns, column_name, share_ind):
    tdf2 = tdf.query("`{}` == '{}'".format(column_name, share_ind))
    tdf2 = tdf2[chosen_columns].values[0]
    #tdf2 = squeezing(tdf2)
    return tdf2


def avg(mylist):
    return sum(mylist) / len(mylist)


def handle_share_split(df, sql_df, cursor, table_name):
    common_columns = u.common_member(df.columns, sql_df.columns)
    only_sql_columns = get_columns_only_in_sql(df, sql_df)
    df_indicators_column_name = get_name_of_column_with_indicator_names(df)
    sql_df_indicators_column_name = get_name_of_column_with_indicator_names(sql_df)
    shares_indicators = ['Basic Shares Outstanding', 'Diluted Shares Outstanding', 'EPS (Basic)', 'EPS (Diluted)']
    # czy rownize eps diluted nie powinno byc zmieniane
    diff_dict = {}
    if common_columns:
        for share_ind in shares_indicators:  # wybrane wskazniki
            s_l = shorten_df_to_chosen_fragment(df, common_columns, df_indicators_column_name, share_ind)
            ssql_l = shorten_df_to_chosen_fragment(sql_df, common_columns, sql_df_indicators_column_name, share_ind)
            diff_l = []
            for v, sqlv, col in zip(s_l, ssql_l, common_columns):
                if v != sqlv and v != '-' and sqlv != '-':
                    v = u.transform_val(v)
                    sqlv = u.transform_val(sqlv)
                    if float(sqlv) != 0:  # wykluczneie przypadkow gdy nie ma daneog parametru na wsj w sql jest 0
                        diff_l.append(float(v) / float(sqlv))
                        sql_update_statement = f'''
                                        UPDATE wsj.dbo.[{table_name}]
                                        SET [{col}] = '{v}'
                                        WHERE [{sql_df_indicators_column_name}] = '{share_ind}'
                                        '''
                        cursor.execute(sql_update_statement)
            diff_dict[share_ind] = diff_l
    if len(only_sql_columns) > 0:
        for share_ind in shares_indicators:
            if diff_dict[share_ind]:
                if compare_changes(diff_dict[share_ind], share_ind, s_l, ssql_l) is False:
                    break
                change = avg(diff_dict[share_ind])
                ssql_l = shorten_df_to_chosen_fragment(sql_df, only_sql_columns, sql_df_indicators_column_name,
                                                       share_ind)
                for sqlv, col in zip(ssql_l, only_sql_columns):
                    sqlv = u.transform_val(sqlv)
                    new_v = sqlv * change
                    sql_update_statement = '''
                                    UPDATE wsj.dbo.[{}]
                                    SET [{}] = '{}'
                                    WHERE [{}] = '{}'
                                    '''.format(table_name, col, new_v, sql_df_indicators_column_name, share_ind)
                    cursor.execute(sql_update_statement)
