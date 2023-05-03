import calendar
import datetime
import pandas as pd

import update
import utilities as u


def update_indeks():
    indekses = [('SP_500', '^GSPC'), ('NASDAQ', '^IXIC')]
    cursor, wsj_conn, engine = u.create_sql_connection('wsj')
    sql_table_list = u.get_all_tables(cursor)
    frequencies = ['1mo', '1d']
    for indeks_name, indeks_ticker in indekses:
        for frequency in frequencies:
            indeks_price_history = indeks_name + '_price_history_' + frequency
            price_df_url = update.download_and_prepare_price_history(indeks_ticker, frequency)

            if update.check_if_tables_exists(indeks_price_history, sql_table_list):
                sql_select_all = 'SELECT * FROM {0}'.format(indeks_price_history)
                price_df_sql = pd.read_sql(sql_select_all, wsj_conn)
                price_df_sql.sort_values('Date', ascending=False, inplace=True)
                price_df_sql.reset_index(inplace=True)
                if price_df_sql.iloc[0, 0] == price_df_url.iloc[0, 0]:
                    pass
                else:
                    df_diff = pd.concat([price_df_url, price_df_sql]).drop_duplicates(keep=False)
                    for r in df_diff.index:
                        insert_values = [indeks_price_history]
                        for c in df_diff.columns:
                            insert_values.append(df_diff[c][r])
                        sql_insert = 'INSERT INTO {0} (Date, Open, High, Low, Close, Volume, Dividends, Stock Splits)' \
                                     'VALUES ({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})'.format(*insert_values)
                        cursor.execute(sql_insert)
            else:
                price_df = update.download_and_prepare_price_history(indeks_ticker, frequency)
                price_df.to_sql(indeks_price_history, con=engine, if_exists='replace', index=False)

            print('{0} updated'.format(indeks_price_history))
    wsj_conn.close()

