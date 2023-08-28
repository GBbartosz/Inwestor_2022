import datetime
import time
import datetime as dt
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup

import share_split as ss
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
                url_check_list = list(map(lambda u: u.format(link_insert), url_empty_check_list))
                url = url_check_list[0]
                #print(url)
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
    validation_wsj = ['All values USD', 'All values EUR', 'All values HKD', 'All values JPY']
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
            print('{0} under {1} has not valid positions'.format(ticker, url))
            return False
        else:
            return True


def update_sql_table_empty_values(df, sql_df, cursor, table_name):
    common_columns = u.common_member(df.columns, sql_df.columns)
    if common_columns:
        for col in common_columns:
            for r in sql_df.index:
                if sql_df.loc[r, col] == '-' and df.loc[r, col] != '-'\
                    or sql_df.loc[r, col] == '0.00%' and df.loc[r, col] != '0.00%'\
                        or sql_df.loc[r, col] == 'nan' and df.loc[r, col] != 'nan':
                    new_val = df.loc[r, col]
                    sql_update_statement = '''
                                    UPDATE wsj.dbo.[{}]
                                    SET [{}] = '{}'
                                    WHERE [index] = {}
                                    '''.format(table_name, col, new_val, r)
                    cursor.execute(sql_update_statement)


def squeezing(myseries):
    try:
        x = myseries.squeeze().tolist()
    except AttributeError:
        x = list(myseries.squeeze())
    return x

# fsc __repair_column_name
def repair_column_name(table_name, old_col_name, cursor):
    sql_query = '''
                ALTER TABLE [wsj].[dbo].[{}]
                DROP COLUMN [{}]
                '''.format(table_name, old_col_name)
    cursor.execute(sql_query)
    pos = table_name.find('_')
    tic = table_name[:pos]
    ticker_tables = u.create_basic_ticker_table_name(tic)
    update(tic, ticker_tables)


def yf_price_data_timeliness(df):
    yf_max_date = df['Date'].max()
    delta = datetime.date.today() - yf_max_date.to_pydatetime().date()
    diff = delta.days
    if diff < 5:
        res = True
    else:
        res = False
    return res


def convert_thousands_to_millions(df, num):

    def rename_thousands_to_millions(df, ind_col):
        newind_col = ind_col.replace('Thousands', 'MillionsTT')
        df = df.rename(columns={ind_col: newind_col})
        return df

    ind_col = df.columns[1]
    periods_cols = df.columns[2:]
    if 'Thousands' in ind_col:
        if num in [0, 1]:  #income_statement
            specwords = ['margin', 'Margin', 'growth', 'Growth', 'EPS']
            #correct_positions = [Sales Growth, COGS Growth, Gross Income Growth, Gross Profit Margin, SGA Growth, Interest Expense Growth, Pretax Income Growth, Pretax Margin, Net Income Growth, Net Margin, 'EPS (Basic)', 'EPS (Basic) Growth', 'EPS (Diluted)', 'EPS (Diluted) Growth']
        if num in [2, 3]:  #balance_assets
            specwords = ['growth', 'Growth', 'Cash & ST Investments / Total Assets', 'Accounts Receivable Turnover', 'Asset Turnover', 'Return On Average Assets']
            # Bad Debt/Doubtful Accounts -- sprawdzic
        if num in [4, 5]:  #balance_liabilities
            specwords = ['growth', 'Growth', 'Current Ratio', 'Quick Ratio', 'Cash Ratio', 'Total Liabilities / Total Assets', 'Common Equity / Total Assets', 'Total Shareholders\' Equity / Total Assets']
        if num in [6, 7]:  #cash_flow
            specwords = ['growth', 'Growth', 'Net Operating Cash Flow / Sales']
        ind_in_thousands = [x for x in df[ind_col] if all(specword not in x for specword in specwords)]
        mask = df[ind_col].isin(ind_in_thousands)  # selecting rows to be updated
        df.loc[mask, periods_cols] = df.loc[mask, periods_cols].applymap(lambda x: x / 1000)
        df = rename_thousands_to_millions(df, ind_col)
        return df


def get_financial_statement_currency(num, df, ticker):
    fs_currency = None
    main_caption = df.columns[1]
    if ' USD ' in main_caption:
        fs_currency = 'USD'
    elif ' EUR ' in main_caption:
        fs_currency = 'EUR'
    elif ' HKD ' in main_caption:
        fs_currency = 'HKD'
    elif ' JPY ' in main_caption:
        fs_currency = 'JPY'
    else:
        print(f'{ticker} has unprecedented value! (update - 377)')
    return fs_currency


def update(ticker, ticker_tables):
    global unsuccessful
    unsuccessful = None

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

    cursor, wsj_conn, engine = u.create_sql_connection('wsj')
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
                    print(f'For {ticker} {url} was not downloaded')
                    return None
            else:
                data_downloaded = True

        if num == 4 or num == 5:
            for d in df:
                if d.columns[0] in ['All values USD Thousands.', 'All values USD Millions.',
                                    'All values EUR Thousands.', 'All values EUR Millions.',
                                    'All values HKD Thousands.', 'All values HKD Millions.',
                                    'All values JPY Thousands.', 'All values JPY Millions.']:
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
        if num == 1:  # income_statement_q
            fs_currency = get_financial_statement_currency(num, df, ticker)

        # sprawdzenie zgodnosci pozycji
        if check_positions(ticker, url, positions_dic, num, df) is False:
            unsuccessful = ticker
            break

        df.iloc[:, 2:] = df.iloc[:, 2:].applymap(u.transform_val)
        if 'Thousands' in df.columns[1]:
            print('thousands convert')
            df = convert_thousands_to_millions(df, num)

        web_headers_names = list(df.columns)

        if check_if_tables_exists(ticker_tables[num], sql_table_list):
            sql_select_all = 'SELECT * FROM [{0}]'.format(ticker_tables[num])
            sql_df = pd.read_sql(sql_select_all, wsj_conn)
            sql_headers_names = list(sql_df.columns)
            lacking_column_names = []
            update_sql_table_empty_values(df, sql_df, cursor, ticker_tables[num])
            #income statement tables q, y

            # aktualziacja share split
            if ticker_tables[num] in [ticker_tables[0], ticker_tables[1]]:
                ss.handle_share_split(df, sql_df, cursor, ticker_tables[num])

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

    # price_history
    price_currency = update_price(ticker)

    # profile
    update_profile(ticker, url_check_list, fs_currency, price_currency)

    print(ticker + ' updated')


def update_profile(ticker, url_check_list, fs_currency, price_currency):
    cursor, wsj_conn, engine = u.create_sql_connection('wsj')
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

    sector = profile_data[1].text[1:-1]  # [1:-1] deletes spaces at beginning and ending
    industry = profile_data[3].text[1:-1]
    fiscal_year_ends = ' '.join(profile_data[5].text.split(' ')[1:3])  # text returns ' December 31 Download Reports '
    profile_df = pd.DataFrame([[sector, industry, fiscal_year_ends, fs_currency, price_currency]],
                              columns=['Sector', 'Industry', 'Fiscal Year Ends', 'FS_Currency', 'Price_Currency'])
    profile_df.to_sql(ticker_profile, con=engine, if_exists='replace', index=False)
    wsj_conn.close()


class UpdatePriceIndex:
    def __init__(self, price_df_sql, df_diff):
        max_index_value = int(price_df_sql.iloc[0, 0])
        max_index_after_update = int(max_index_value + len(df_diff.index))
        self.new_indexes = list(range(max_index_value, max_index_after_update))
        self.n = 0

    def get_next_prev_index(self):
        self.n -= 1
        index_value = self.new_indexes[self.n]
        return index_value


def download_and_prepare_price_history(ticker, frequency):
    global unsuccessful
    data_downloaded = False
    start_time = time.time()
    while data_downloaded is False:
        try:
            end_time = time.time()
            if end_time - start_time > 120:
                print('download_and_prepare_price_history over 120s')
            df = pd.DataFrame()
            tic = yf.Ticker(ticker)
            df = tic.history(period='max', interval=frequency)
            price_currency = tic.info['currency']

        except:
            pass
        else:
            data_downloaded = True
    if df.empty:
        unsuccessful = ticker
        print('{0} is not valid for yfinance'.format(ticker))
        return None
    if 'Date' not in df.columns:
        #df['Date'] = df.index
        df = df.reset_index()
    if yf_price_data_timeliness(df) is False:
        pass
        #download data from other source

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
    return df, price_currency


def update_price(ticker):

    cursor, wsj_conn, engine = u.create_sql_connection('wsj')

    sql_table_list = u.get_all_tables(cursor)
    # frequencies = ['1mo', '1d']  # nie wyszukuje 1mo
    frequencies = ['1d']
    for frequency in frequencies:
        ticker_price_history = ticker + '_price_history_' + frequency
        price_df_url, price_currency = download_and_prepare_price_history(ticker, frequency)
        if price_df_url is not None:
            if check_if_tables_exists(ticker_price_history, sql_table_list):
                sql_select_all = 'SELECT * FROM [{0}]'.format(ticker_price_history)
                price_df_sql = pd.read_sql(sql_select_all, wsj_conn)
                price_df_sql.sort_values('Date', ascending=False, inplace=True)
                price_df_sql.reset_index(drop=True, inplace=True)
                if price_df_sql['Date'][0] == price_df_url['Date'][0]:  # case when last date in sql is up to date
                    pass
                else:
                    df_diff = pd.concat([price_df_url, price_df_sql]).drop_duplicates(subset='Date', keep=False) # yahoo zmienia dane i w efekcie daty się duplikują, konieczny subset
                    df_diff.reset_index(drop=True, inplace=True)
                    update_price_index = UpdatePriceIndex(price_df_sql, df_diff)
                    for r in df_diff.index:
                        insert_values = [ticker_price_history]
                        index_value = update_price_index.get_next_prev_index()
                        for c in df_diff.columns:
                            insert_values.append(df_diff[c].iloc[r])
                        insert_values_without_index = [insert_values[0]] + [index_value] + insert_values[2:]
                        #for x in insert_values_without_str:
                        #    if x is not None and x is not np.nan:
                        sql_insert = 'INSERT INTO [wsj].[dbo].[{0}] ([Index], [Date], [Open], [High], [Low], [Close], [Volume], [Dividends], [Stock Splits])' \
                                     'VALUES ({1}, \'{2}\', {3}, {4}, {5}, {6}, {7}, {8}, {9})'.format(*insert_values_without_index)
                        cursor.execute(sql_insert)
                        cursor.commit()
            else:
                price_df, price_currency = download_and_prepare_price_history(ticker, frequency)
                price_df.to_sql(ticker_price_history, con=engine, if_exists='replace', index=False)
    return price_currency

    wsj_conn.close()
