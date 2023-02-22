import time

from bs4 import BeautifulSoup
import datetime as dt
import numpy as np
import pandas as pd
import requests
import yfinance as yf

import utilities as u


unsuccessful = None


def check_if_tables_exists(table, sql_table_list):
    if table in sql_table_list:
        return True
    else:
        return False


def check_if_columns_are_current(web_headers_names, sql_headers_names, lacking_column_names):
    for web_header in web_headers_names:
        if web_header not in sql_headers_names and 'All values' not in web_header:
            lacking_column_names.append(web_header)
    return lacking_column_names


def inside_apostrophe(word):
    word = '{0}{1}{0}'.format('\'', word)
    return word


def download_and_prepare_price_history(ticker, frequency):
    global unsuccessful
    data_downloaded = False
    while data_downloaded is False:
        try:
            df = pd.DataFrame()
            tic = yf.Ticker(ticker)
            df = tic.history(period='max', interval=frequency)
        except:
            pass
        else:
            data_downloaded = True
    if df.empty:
        unsuccessful = ticker
        print('{0} is not valid for yfinance'.format(ticker))
        return None
    if frequency == '1mo':
        df.sort_values('Date', ascending=False, inplace=True)
        df.drop(index=df.index[0], axis=0, inplace=True)
    df.reset_index(drop=False, inplace=True)
    df['Date'] = df['Date'].apply(lambda x: str(dt.datetime.strptime(str(x)[:-6], '%Y-%m-%d %H:%M:%S').date()))
    #df['Date'] = df['Date'].apply(lambda x: str(x)[:10])
    df.dropna(inplace=True)
    #for col in df.columns:
    #    for r in df.index:
    #        if df[col].iloc[r] == np.nan or df[col].iloc[r] == None or df[col].iloc[r] == 'NULL':
    #            df.drop(labels=r, axis=0, inplace=True)
    df.sort_values('Date', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def validate_urls(url_empty_check_list_wsj, url_empty_check_list_yahoo, ticker):
    def validate_url_list(url_empty_check_list, link_insert, link_insert_options, validation):
        def prepare_to_next_attempt(attempts, attempts_level, link_insert, link_insert_options):
            if attempts == attempts_level:
                print('over attempts level')
                link_insert_enum = int(attempts_level / 4 - 1)
                attempts_level += 4
                link_insert = link_insert_options[link_insert_enum]
            attempts += 1
            return attempts, attempts_level, link_insert


        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        url_ok = False
        attempts = 1
        attempts_level = 4
        while url_ok is False:
            try:
                #print('attempts: {0}'.format(attempts))
                #print('attempts level: {0}'.format(attempts_level))
                url_check_list = list(map(lambda u: u.format(link_insert), url_empty_check_list))
                url = url_check_list[0]
                resp = requests.get(url, headers=headers).text
                dfs = pd.read_html(resp)
                for d in dfs:
                    if any(x in d.columns[0] for x in validation):
                        url_ok = True
                        return url_check_list
                if url_ok is False:
                    # czy przekroczono liczbe prob
                    if attempts == len(link_insert_options) * 4 + 4:
                        url_check_list = []
                        print('{0} url not valid'.format(ticker))
                        return url_check_list
                    attempts, attempts_level, link_insert = prepare_to_next_attempt(attempts, attempts_level, link_insert,
                                                                    link_insert_options)
            except:
                # czy przekroczono liczbe prob
                if attempts == len(link_insert_options) * 4 + 4:
                    url_check_list = []
                    print('{0} url not valid'.format(ticker))
                    return url_check_list
                attempts, attempts_level, link_insert = prepare_to_next_attempt(attempts, attempts_level, link_insert,
                                                                link_insert_options)

    link_insert = ticker
    link_insert_options_wsj = ['XE/XETR/' + ticker, 'LU/XLUX/' + ticker]
    link_insert_options_yahoo = [ticker + '.DE']
    validation_wsj = ['All values USD', 'All values EUR']
    validation_yahoo = ['Date']

    url_check_list_wsj = validate_url_list(url_empty_check_list_wsj, link_insert, link_insert_options_wsj,
                                           validation_wsj)

    if len(url_empty_check_list_yahoo) != 0:
        url_check_list_yahoo = validate_url_list(url_empty_check_list_yahoo, link_insert, link_insert_options_yahoo,
                                                 validation_yahoo)
    else:
        url_check_list_yahoo = []

    url_check_list = url_check_list_wsj + url_check_list_yahoo
    return url_check_list


def check_positions(ticker, url, positions_dic, num, df):
    for i in df.index:
        if positions_dic[num][i] != df.iloc[i, 1]:
            print(positions_dic[num][i])
            print(df.iloc[i, 1])
            print('{0} under {1} has not valid positions'.format(ticker, url))
            return False
        else:
            return True


def get_rid_of_index_and_indicators(coll):
    if 'index' in coll:
        coll.remove('index')
    for c in coll:
        if 'Fiscal' in c:
            coll.remove(c)
    return coll


def common_member(a, b):
    common = []
    for c in a:
        if c in b:
            common.append(c)
    common = get_rid_of_index_and_indicators(common)
    return common


def get_columns_only_in_sql(df, sql_df):
    res = []
    for sqlc in sql_df.columns:
        if sqlc not in df.columns:
            res.append(sqlc)
    res = get_rid_of_index_and_indicators(res)
    return res


def update_sql_table_empty_values(df, sql_df, cursor, table_name):
    common_columns = common_member(df.columns, sql_df.columns)
    if common_columns:
        for col in common_columns:
            for r in sql_df.index:
                if sql_df.loc[r, col] == '-' and df.loc[r, col] != '-'\
                    or sql_df.loc[r, col] == '0.00%' and df.loc[r, col] != '0.00%'\
                        or sql_df.loc[r, col] == 'nan' and df.loc[r, col] != 'nan':
                    new_val = df.loc[r, col]
                    sql_update_statement = '''
                                    UPDATE wsj.dbo.{}
                                    SET [{}] = '{}'
                                    WHERE [index] = {}
                                    '''.format(table_name, col, new_val, r)
                    cursor.execute(sql_update_statement)


def avg(mylist):
    return sum(mylist) / len(mylist)


def get_name_of_column_with_indicator_names(tdf):
    column_name = tdf.columns[1]
    return column_name


def shorten_df_to_chosen_fragment(tdf, chosen_columns, column_name, share_ind):
    tdf = tdf.query("`{}` == '{}'".format(column_name, share_ind))
    tdf = tdf[chosen_columns]
    tdf = squeezing(tdf)
    return tdf


def compare_changes(changel):
    outcome = True
    c0 = changel[0]
    for c in changel:
        res = c / c0
        if res < 0.9 or res > 1.1:
            print('Error stock split change: {}'.format(changel))
            outcome = False
    return outcome


def squeezing(myseries):
    try:
        x = myseries.squeeze().tolist()
    except AttributeError:
        x = list(myseries.squeeze())
    return x


def update_sql_table_diluted_shares_outstanding(df, sql_df, cursor, table_name):
    common_columns = common_member(df.columns, sql_df.columns)
    only_sql_columns = get_columns_only_in_sql(df, sql_df)
    df_indicators_column_name = get_name_of_column_with_indicator_names(df)
    sql_df_indicators_column_name = get_name_of_column_with_indicator_names(sql_df)
    shares_indicators = ['Basic Shares Outstanding', 'Diluted Shares Outstanding', 'EPS (Basic)']
    diff_dict = {}
    if common_columns:
        for share_ind in shares_indicators:
            s_l = shorten_df_to_chosen_fragment(df, common_columns, df_indicators_column_name, share_ind)
            ssql_l = shorten_df_to_chosen_fragment(sql_df, common_columns, sql_df_indicators_column_name, share_ind)
            diff_l = []
            for v, sqlv, col in zip(s_l, ssql_l, common_columns):
                if v != sqlv:
                    if v != '-' and sqlv != '-':
                        diff_l.append(float(v) / float(sqlv))
                    sql_update_statement = '''
                                    UPDATE wsj.dbo.{}
                                    SET [{}] = '{}'
                                    WHERE [{}] = '{}'
                                    '''.format(table_name, col, v, sql_df_indicators_column_name, share_ind)
                    #cursor.execute(sql_update_statement)
            diff_dict[share_ind] = diff_l

    if len(only_sql_columns) > 0:
        for share_ind in shares_indicators:
            if diff_dict[share_ind]:
                if compare_changes(diff_dict[share_ind]) is False:
                    break
                change = avg(diff_dict[share_ind])
                ssql_l = shorten_df_to_chosen_fragment(sql_df, only_sql_columns, sql_df_indicators_column_name, share_ind)
                print('x')
                print(ssql_l)
                for sqlv, col in zip(ssql_l, only_sql_columns):
                    new_v = float(sqlv) * change
                    sql_update_statement = '''
                                    UPDATE wsj.dbo.{}
                                    SET [{}] = '{}'
                                    WHERE [{}] = '{}'
                                    '''.format(table_name, col, new_v, sql_df_indicators_column_name, share_ind)
                    print(sql_update_statement)
                    # cursor.execute(sql_update_statement)


def update(ticker, ticker_tables):
    global unsuccessful
    unsuccessful = None
    #print(ticker)

    income_statement_positions = ['Sales/Revenue', 'Sales Growth', 'Cost of Goods Sold (COGS) incl. D&A',
                                  'COGS excluding D&A', 'Depreciation & Amortization Expense', 'Depreciation',
                                  'Amortization of Intangibles', 'Amortization of Deferred Charges', 'COGS Growth',
                                  'Gross Income', 'Gross Income Growth', 'Gross Profit Margin', 'SG&A Expense',
                                  'Research & Development', 'Other SG&A', 'SGA Growth', 'Other Operating Expense',
                                  'EBIT', 'Unusual Expense', 'Non Operating Income/Expense',
                                  'Non-Operating Interest Income', 'Equity in Affiliates (Pretax)', 'Interest Expense',
                                  'Interest Expense Growth', 'Gross Interest Expense', 'Interest Capitalized',
                                  'Pretax Income', 'Pretax Income Growth', 'Pretax Margin', 'Income Tax',
                                  'Income Tax - Current Domestic', 'Income Tax - Current Foreign',
                                  'Income Tax - Deferred Domestic', 'Income Tax - Deferred Foreign',
                                  'Income Tax Credits', 'Equity in Affiliates', 'Other After Tax Income (Expense)',
                                  'Consolidated Net Income', 'Minority Interest Expense', 'Net Income',
                                  'Net Income Growth', 'Net Margin', 'Extraordinaries & Discontinued Operations',
                                  'Extra Items & Gain/Loss Sale Of Assets', 'Cumulative Effect - Accounting Chg',
                                  'Discontinued Operations', 'Net Income After Extraordinaries', 'Preferred Dividends',
                                  'Net Income Available to Common', 'EPS (Basic)', 'EPS (Basic) Growth',
                                  'Basic Shares Outstanding', 'EPS (Diluted)', 'EPS (Diluted) Growth',
                                  'Diluted Shares Outstanding', 'EBITDA', 'EBITDA Growth', 'EBITDA Margin', 'EBIT']
    balance_assets_positions = ['Net Income before Extraordinaries', 'Cash & Short Term Investments', 'Cash Only',
                                'Short-Term Investments', 'Cash & Short Term Investments Growth',
                                'Cash & ST Investments / Total Assets', 'Total Accounts Receivable',
                                'Accounts Receivables, Net', 'Accounts Receivables, Gross',
                                'Bad Debt/Doubtful Accounts', 'Other Receivables', 'Accounts Receivable Growth',
                                'Accounts Receivable Turnover', 'Inventories', 'Finished Goods', 'Work in Progress',
                                'Raw Materials', 'Progress Payments & Other', 'Other Current Assets',
                                'Prepaid Expenses', 'Miscellaneous Current Assets', 'Total Current Assets',
                                'Net Property, Plant & Equipment', 'Property, Plant & Equipment - Gross', 'Buildings',
                                'Land & Improvements', 'Machinery & Equipment', 'Construction in Progress', 'Leases',
                                'Computer Software and Equipment', 'Leased Property', 'Transportation Equipment',
                                'Other Property, Plant & Equipment', 'Accumulated Depreciation', 'Buildings',
                                'Land & Improvements', 'Machinery & Equipment', 'Construction in Progress', 'Leases',
                                'Computer Software and Equipment', 'Leased Property', 'Transportation Equipment',
                                'Other Property, Plant & Equipment', 'Total Investments and Advances',
                                'LT Investment - Affiliate Companies', 'Other Long-Term Investments',
                                'Long-Term Note Receivable', 'Intangible Assets', 'Net Goodwill',
                                'Net Other Intangibles', 'Other Assets', 'Deferred Charges', 'Tangible Other Assets',
                                'Total Assets', 'Assets - Total - Growth', 'Asset Turnover', 'Return On Average Assets']
    balance_liabilities_positions = ['ST Debt & Current Portion LT Debt', 'Short Term Debt',
                                     'Current Portion of Long Term Debt', 'Accounts Payable', 'Accounts Payable Growth',
                                     'Income Tax Payable', 'Other Current Liabilities', 'Dividends Payable',
                                     'Accrued Payroll', 'Miscellaneous Current Liabilities',
                                     'Total Current Liabilities', 'Total Current Assets FOR CALCULATION PURPOSES ONLY',
                                     'Total Assets FOR CALCULATION PURPOSES ONLY',
                                     'Inventories FOR CALCULATION PURPOSES ONLY',
                                     'Cash & Short Term Investments FOR CALCULATION PURPOSES ONLY', 'Current Ratio',
                                     'Quick Ratio', 'Cash Ratio', 'Long-Term Debt',
                                     'Long-Term Debt excl. Capitalized Leases', 'Non-Convertible Debt',
                                     'Convertible Debt', 'Capitalized Lease Obligations',
                                     'Provision for Risks & Charges', 'Deferred Taxes', 'Deferred Taxes - Credit',
                                     'Deferred Taxes - Debit', 'Other Liabilities',
                                     'Deferred Tax Liability-Untaxed Reserves',
                                     'Other Liabilities (excl. Deferred Income)', 'Deferred Income',
                                     'Total Liabilities', 'Non-Equity Reserves', 'Total Liabilities / Total Assets',
                                     'Preferred Stock (Carrying Value)', 'Redeemable Preferred Stock',
                                     'Non-Redeemable Preferred Stock', 'Preferred Stock issues for ESOP',
                                     'ESOP Guarantees - Preferred Stock', 'Common Equity (Total)',
                                     'Common Stock Par/Carry Value', 'Additional Paid-In Capital/Capital Surplus',
                                     'Retained Earnings', 'ESOP Debt Guarantee',
                                     'Cumulative Translation Adjustment/Unrealized For. Exch. Gain',
                                     'Unrealized Gain/Loss Marketable Securities', 'Revaluation Reserves',
                                     'Other Appropriated Reserves', 'Unappropriated Reserves', 'Treasury Stock',
                                     'Common Equity / Total Assets', 'Total Shareholders\' Equity',
                                     'Total Shareholders\' Equity / Total Assets', 'Accumulated Minority Interest',
                                     'Total Equity', 'Liabilities & Shareholders\' Equity']
    cash_flow_positions = ['Net Income before Extraordinaries', 'Net Income Growth',
                           'Depreciation, Depletion & Amortization', 'Depreciation and Depletion',
                           'Amortization of Intangible Assets', 'Deferred Taxes & Investment Tax Credit',
                           'Deferred Taxes', 'Investment Tax Credit', 'Other Funds', 'Funds from Operations',
                           'Extraordinaries', 'Changes in Working Capital', 'Receivables', 'Inventories',
                           'Accounts Payable', 'Income Taxes Payable', 'Other Accruals', 'Other Assets/Liabilities',
                           'Net Operating Cash Flow', 'Net Operating Cash Flow Growth',
                           'Net Operating Cash Flow / Sales']
    positions_dic = {
        **dict.fromkeys([0, 1], income_statement_positions),
        **dict.fromkeys([2, 3], balance_assets_positions),
        **dict.fromkeys([4, 5], balance_liabilities_positions),
        **dict.fromkeys([6, 7], cash_flow_positions)
    }

    cursor, wsj_conn, engine = u.create_sql_connection()
    sql_table_list = u.get_all_tables(cursor)

    WSJ_income_statement_y = 'https://www.wsj.com/market-data/quotes/{0}/financials/annual/income-statement'
    WSJ_income_statement_q = 'https://www.wsj.com/market-data/quotes/{0}/financials/quarter/income-statement'
    WSJ_balance_assets_y = 'https://www.wsj.com/market-data/quotes/{0}/financials/annual/balance-sheet'
    WSJ_balance_assets_q = 'https://www.wsj.com/market-data/quotes/{0}/financials/quarter/balance-sheet'
    WSJ_balance_liabilities_y = 'https://www.wsj.com/market-data/quotes/{0}/financials/annual/balance-sheet'
    WSJ_balance_liabilities_q = 'https://www.wsj.com/market-data/quotes/{0}/financials/quarter/balance-sheet'
    WSJ_cash_flow_y = 'https://www.wsj.com/market-data/quotes/{0}/financials/annual/cash-flow'
    WSJ_cash_flow_q = 'https://www.wsj.com/market-data/quotes/{0}/financials/quarter/cash-flow'
    profile_path = 'https://www.wsj.com/market-data/quotes/{0}/company-people'

    url_empty_check_list_yahoo = []
    url_empty_check_list_wsj = [WSJ_income_statement_y, WSJ_income_statement_q,
                                WSJ_balance_assets_y, WSJ_balance_assets_q,
                                WSJ_balance_liabilities_y, WSJ_balance_liabilities_q,
                                WSJ_cash_flow_y, WSJ_cash_flow_q, profile_path]

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    url_check_list = validate_urls(url_empty_check_list_wsj, url_empty_check_list_yahoo, ticker)
    # jesli url nie przeszedl walidacji
    if len(url_check_list) == 0:
        unsuccessful = ticker
        return None
    url_list = url_check_list[0:8]
    num = 0
    for url in url_list:
        df = pd.DataFrame()
        data_downloaded = False
        try_start_time = time.time()
        while not data_downloaded:
            try:
                resp = requests.get(url, headers=headers).text
                df = pd.read_html(resp)
            except:
                try_end_time = time.time()
                try_time = try_end_time - try_start_time
                if try_time > 60:
                    unsuccessful = ticker
                    print('For {0} {1} was not downloaded'.format(ticker, url))
                    return None
            else:
                data_downloaded = True

        if num == 4 or num == 5:
            for d in df:
                if d.columns[0] in ['All values USD Thousands.', 'All values USD Millions.',
                                    'All values EUR Thousands.', 'All values EUR Millions.']:
                    df = d
        else:
            df = df[0]
        df = df.iloc[:, :-1]
        df.dropna(how='all', inplace=True)
        df_first_column = df.iloc[:, :1]
        df_rest_reversed = df.iloc[:, :0:-1]
        df = df_first_column.join(df_rest_reversed)
        df.reset_index(drop=True, inplace=True)
        df.reset_index(inplace=True)

        # sprawdzenie zgodnosci pozycji
        if check_positions(ticker, url, positions_dic, num, df) is False:
            unsuccessful = ticker
            break

        web_headers_names = list(df.columns)

        if check_if_tables_exists(ticker_tables[num], sql_table_list):
            sql_select_all = 'SELECT * FROM [{0}]'.format(ticker_tables[num])
            sql_df = pd.read_sql(sql_select_all, wsj_conn)
            sql_headers_names = list(sql_df.columns)
            lacking_column_names = []
            update_sql_table_empty_values(df, sql_df, cursor, ticker_tables[num])
            #income statement tables q, y
            if ticker_tables[num] in [ticker_tables[0], ticker_tables[1]]:
                update_sql_table_diluted_shares_outstanding(df, sql_df, cursor, ticker_tables[num])

            if len(check_if_columns_are_current(web_headers_names, sql_headers_names, lacking_column_names)) == 0:
                pass
            else:
                new_df = df[lacking_column_names]
                col_name = '[{0}]'.format(str(sql_headers_names[0]))
                sql_select_first_column = 'SELECT {0} FROM [{1}]'.format(col_name, ticker_tables[num])
                cursor.execute(sql_select_first_column)
                sql_first_column_values = []
                for r in cursor.fetchall():
                    sql_first_column_values.append(r[0])
                for col in new_df.columns:
                    # create new column
                    col_name = '[{0}]'.format(str(col))
                    sql_create_column = "ALTER TABLE [{0}] ADD {1} VARCHAR(max);".format(ticker_tables[num], col_name)
                    cursor.execute(sql_create_column)
                    for ind in new_df.index:
                        # update
                        val = inside_apostrophe(df[col][ind])
                        sql_first_col_val = inside_apostrophe(sql_first_column_values[ind])
                        sql_update_values = 'UPDATE [{0}] SET {1}={2} WHERE [{3}]={4};'.format(ticker_tables[num],
                                                                                             col_name, val,
                                                                                             sql_headers_names[0],
                                                                                             sql_first_col_val)
                        cursor.execute(sql_update_values)
        else:
            df.to_sql(ticker_tables[num], con=engine, if_exists='replace', index=False)
        num += 1
    wsj_conn.close()

    # profile
    update_profile(ticker, url_check_list)

    # price_history
    update_price(ticker)

    print(ticker + ' updated')


def update_profile(ticker, url_check_list):
    cursor, wsj_conn, engine = u.create_sql_connection()
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    ticker_profile = ticker + '_profile'
    profile_path = url_check_list[8]
    data_downloaded = False
    while not data_downloaded:
        try:
            req = requests.get(profile_path, headers=headers)
            soup = BeautifulSoup(req.content, 'html5lib')
            profile_data = soup.find('div', attrs={'class': 'cr_overview_data cr_data'}) \
                .find_all('span', attrs={'class': 'data_data'})
        except:
            pass
        else:
            data_downloaded = True
    profile_df = pd.DataFrame([[profile_data[1].text, profile_data[3].text, profile_data[5].text[1:4]]],
                              columns=['Sector', 'Industry', 'Fiscal Year Ends'])
    profile_df.to_sql(ticker_profile, con=engine, if_exists='replace', index=False)
    wsj_conn.close()


def update_price(ticker):
    cursor, wsj_conn, engine = u.create_sql_connection()
    sql_table_list = u.get_all_tables(cursor)
    # frequencies = ['1mo', '1d']  # nie wyszukuje 1mo
    frequencies = ['1d']
    for frequency in frequencies:
        ticker_price_history = ticker + '_price_history_' + frequency

        price_df_url = download_and_prepare_price_history(ticker, frequency)
        if price_df_url is not None:
            if check_if_tables_exists(ticker_price_history, sql_table_list):
                sql_select_all = 'SELECT * FROM [{0}]'.format(ticker_price_history)
                price_df_sql = pd.read_sql(sql_select_all, wsj_conn)
                price_df_sql.sort_values('Date', ascending=False, inplace=True)
                price_df_sql.reset_index(drop=True, inplace=True)
                if price_df_sql.iloc[0, 0] == price_df_url.iloc[0, 0]:
                    pass
                else:
                    df_diff = pd.concat([price_df_url, price_df_sql]).drop_duplicates(subset='Date', keep=False) # yahoo zmienia dane i w efekcie daty się duplikują, konieczny subset
                    df_diff.reset_index(drop=True, inplace=True)
                    #print(df_diff)
                    for r in df_diff.index:
                        insert_values = [ticker_price_history]
                        for c in df_diff.columns:
                            insert_values.append(df_diff[c].iloc[r])
                        insert_values_without_str = insert_values[2:]
                        if any(np.isnan(x) for x in insert_values_without_str) is False:
                            sql_insert = 'INSERT INTO [wsj].[dbo].[{0}] ([Date], [Open], [High], [Low], [Close], [Volume], [Dividends], [Stock Splits])' \
                                         'VALUES (\'{1}\', {2}, {3}, {4}, {5}, {6}, {7}, {8})'.format(*insert_values)
                            cursor.execute(sql_insert)
                            cursor.commit()
            else:
                price_df = download_and_prepare_price_history(ticker, frequency)
                price_df.to_sql(ticker_price_history, con=engine, if_exists='replace', index=False)

        #print('{0} updated'.format(ticker_price_history))
    wsj_conn.close()
