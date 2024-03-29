import datetime as dt
import matplotlib.colors as mcolors
import pandas as pd
import pyodbc
import random
import sqlalchemy

import update


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

# utilities transform_val2 - syzbsza, czy nie bedzie wywalala na innych notatnikach poza financialstatementsclass
def transform_val(val):
    if val == '-':
        val = 0
    elif val is None:
        val = 0
    elif val != 0 and isinstance(val, str):
        if ',' in val:
            val = val.replace(',', '')
        if '(' in val:
            val = val.replace('(', '-')
            val = val.replace(')', '')
        #if '.' in val and val.count('.') > 1:
        #    val = val.replace('.', '')
        if '%' in val:
            val = val.replace('%', '')
            val = float(val) / 100
        val = float(val)
    return val


def get_rid_of_special_characters(word):
    if isinstance(word, str):
        special_characters = ['&', '/', '(', ')', ' ', '-', '.', ',', '\'']
        for char in special_characters:
            if char in word:
                word = word.replace(char, '_')
        special_characters2 = ['_____', '____', '___', '__']
        for char in special_characters2:
            if char in word:
                word = word.replace(char, '_')
        if word[-1] == '_':
            word = word[:-1]
        if word[0] == '_':
            word = word[1:]
    return word

#priceclass
def current_price_download(ticker):
    MW_overview = 'https://www.marketwatch.com/investing/stock/{0}'.format(ticker)
    try:
        price = pd.read_html(MW_overview)[1].loc[0, 'Close'][1:]
    except:
        price = pd.read_html(MW_overview)[1].loc[0, 'Previous Close'][1:]
    price = float(get_rid_of_special_characters(price)) / 100
    return price


class IncomeStatement(object):
    def __init__(self, ind_name_list, ind_enumerate_list, years_list, df):
        self.Sales_Revenue = None
        self.Sales_Growth = None
        self.Cost_of_Goods_Sold_COGS_incl_D_A = None
        self.COGS_excluding_D_A = None
        self.Depreciation_Amortization_Expense = None
        self.Depreciation = None
        self.Amortization_of_Intangibles = None
        self.Amortization_of_Deferred_Charges = None
        self.COGS_Growth = None
        self.Gross_Income = None
        self.Gross_Income_Growth = None
        self.Gross_Profit_Margin = None
        self.SG_A_Expense = None
        self.Research_Development = None
        self.Other_SG_A = None
        self.SGA_Growth = None
        self.Other_Operating_Expense = None
        self.EBIT = None
        self.Unusual_Expense = None
        self.Non_Operating_Income_Expense = None
        self.Non_Operating_Interest_Income = None
        self.Equity_in_Affiliates_Preta = None
        self.Interest_Expense = None
        self.Interest_Expense_Growth = None
        self.Gross_Interest_Expense = None
        self.Interest_Capitalized = None
        self.Pretax_Income = None
        self.Pretax_Income_Growth = None
        self.Pretax_Margin = None
        self.Income_Tax = None
        self.Income_Tax_Current_Domestic = None
        self.Income_Tax_Current_Foreign = None
        self.Income_Tax_Deferred_Domestic = None
        self.Income_Tax_Deferred_Foreign = None
        self.Income_Tax_Credits = None
        self.Equity_in_Affiliates = None
        self.Other_After_Tax_Income_Expens = None
        self.Consolidated_Net_Income = None
        self.Minority_Interest_Expense = None
        self.Net_Income = None
        self.Net_Income_Growth = None
        self.Net_Margin = None
        self.Extraordinaries_Discontinued_Operations = None
        self.Extra_Items_Gain_Loss_Sale_Of_Assets = None
        self.Cumulative_Effect_Accounting_Chg = None
        self.Discontinued_Operations = None
        self.Net_Income_After_Extraordinaries = None
        self.Preferred_Dividends = None
        self.Net_Income_Available_to_Common = None
        self.EPS_Basic = None
        self.EPS_Basic_Growth = None
        self.Basic_Shares_Outstanding = None
        self.EPS_Diluted = None
        self.EPS_Diluted_Growth = None
        self.Diluted_Shares_Outstanding = None
        self.EBITDA = None
        self.EBITDA_Growth = None
        self.EBITDA_Margin = None
        self.EBIT = None
        for ind_name, i in zip(ind_name_list, ind_enumerate_list):
            ind_name = get_rid_of_special_characters(ind_name)
            setattr(self, str(ind_name), Indicator(i, years_list, df))


class BalanceAssets(object):
    def __init__(self, ind_name_list, ind_enumerate_list, years_list, df):
        self.Net_Income_before_Extraordinaries = None
        self.Cash_Short_Term_Investments = None
        self.Cash_Only = None
        self.Short_Term_Investments = None
        self.Cash_Short_Term_Investments_Growth = None
        self.Cash_ST_Investments_Total_Assets = None
        self.Total_Accounts_Receivable = None
        self.Accounts_Receivables_Net = None
        self.Accounts_Receivables_Gross = None
        self.Bad_Debt_Doubtful_Accounts = None
        self.Other_Receivables = None
        self.Accounts_Receivable_Growth = None
        self.Accounts_Receivable_Turnover = None
        self.Inventories = None
        self.Finished_Goods = None
        self.Work_in_Progress = None
        self.Raw_Materials = None
        self.Progress_Payments_Other = None
        self.Other_Current_Assets = None
        self.Prepaid_Expenses = None
        self.Miscellaneous_Current_Assets = None
        self.Total_Current_Assets = None
        self.Net_Property_Plant_Equipment = None
        self.Property_Plant_Equipment_Gross = None
        self.Buildings = None
        self.Land_Improvements = None
        self.Machinery_Equipment = None
        self.Construction_in_Progress = None
        self.Leases = None
        self.Computer_Software_and_Equipment = None
        self.Leased_Property = None
        self.Transportation_Equipment = None
        self.Other_Property_Plant_Equipment = None
        self.Accumulated_Depreciation = None
        self.Buildings = None
        self.Land_Improvements = None
        self.Machinery_Equipment = None
        self.Construction_in_Progress = None
        self.Leases = None
        self.Computer_Software_and_Equipment = None
        self.Leased_Property = None
        self.Transportation_Equipment = None
        self.Other_Property_Plant_Equipment = None
        self.Total_Investments_and_Advances = None
        self.LT_Investment_Affiliate_Companies = None
        self.Other_Long_Term_Investments = None
        self.Long_Term_Note_Receivable = None
        self.Intangible_Assets = None
        self.Net_Goodwill = None
        self.Net_Other_Intangibles = None
        self.Other_Assets = None
        self.Deferred_Charges = None
        self.Tangible_Other_Assets = None
        self.Total_Assets = None
        self.Assets_Total_Growth = None
        self.Asset_Turnover = None
        self.Return_On_Average_Assets = None
        for ind_name, i in zip(ind_name_list, ind_enumerate_list):
            ind_name = get_rid_of_special_characters(ind_name)
            setattr(self, str(ind_name), Indicator(i, years_list, df))


class BalanceLiabilities(object):
    def __init__(self, ind_name_list, ind_enumerate_list, years_list, df):
        self.ST_Debt_Current_Portion_LT_Debt = None
        self.Short_Term_Debt = None
        self.Current_Portion_of_Long_Term_Debt = None
        self.Accounts_Payable = None
        self.Accounts_Payable_Growth = None
        self.Income_Tax_Payable = None
        self.Other_Current_Liabilities = None
        self.Dividends_Payable = None
        self.Accrued_Payroll = None
        self.Miscellaneous_Current_Liabilities = None
        self.Total_Current_Liabilities = None
        self.Total_Current_Assets_FOR_CALCULATION_PURPOSES_ONLY = None
        self.Total_Assets_FOR_CALCULATION_PURPOSES_ONLY = None
        self.Inventories_FOR_CALCULATION_PURPOSES_ONLY = None
        self.Cash_Short_Term_Investments_FOR_CALCULATION_PURPOSES_ONLY = None
        self.Current_Ratio = None
        self.Quick_Ratio = None
        self.Cash_Ratio = None
        self.Long_Term_Debt = None
        self.Long_Term_Debt_excl_Capitalized_Leases = None
        self.Non_Convertible_Debt = None
        self.Convertible_Debt = None
        self.Capitalized_Lease_Obligations = None
        self.Provision_for_Risks_Charges = None
        self.Deferred_Taxes = None
        self.Deferred_Taxes_Credit = None
        self.Deferred_Taxes_Debit = None
        self.Other_Liabilities = None
        self.Deferred_Tax_Liability_Untaxed_Reserves = None
        self.Other_Liabilities_excl_Deferred_Incom = None
        self.Deferred_Income = None
        self.Total_Liabilities = None
        self.Non_Equity_Reserves = None
        self.Total_Liabilities_Total_Assets = None
        self.Preferred_Stock_Carrying_Valu = None
        self.Redeemable_Preferred_Stock = None
        self.Non_Redeemable_Preferred_Stock = None
        self.Preferred_Stock_issues_for_ESOP = None
        self.ESOP_Guarantees_Preferred_Stock = None
        self.Common_Equity_Tota = None
        self.Common_Stock_Par_Carry_Value = None
        self.Additional_Paid_In_Capital_Capital_Surplus = None
        self.Retained_Earnings = None
        self.ESOP_Debt_Guarantee = None
        self.Cumulative_Translation_Adjustment_Unrealized_For_Exch_Gain = None
        self.Unrealized_Gain_Loss_Marketable_Securities = None
        self.Revaluation_Reserves = None
        self.Other_Appropriated_Reserves = None
        self.Unappropriated_Reserves = None
        self.Treasury_Stock = None
        self.Common_Equity_Total_Assets = None
        self.Total_Shareholders_Equity = None
        self.Total_Shareholders_Equity_Total_Assets = None
        self.Accumulated_Minority_Interest = None
        self.Total_Equity = None
        self.Liabilities_Shareholders_Equity = None
        for ind_name, i in zip(ind_name_list, ind_enumerate_list):
            ind_name = get_rid_of_special_characters(ind_name)
            setattr(self, str(ind_name), Indicator(i, years_list, df))


class CashFlow(object):
    def __init__(self, ind_name_list, ind_enumerate_list, years_list, df):
        self.Net_Income_before_Extraordinaries = None
        self.Net_Income_Growth = None
        self.Depreciation_Depletion_Amortization = None
        self.Depreciation_and_Depletion = None
        self.Amortization_of_Intangible_Assets = None
        self.Deferred_Taxes_Investment_Tax_Credit = None
        self.Deferred_Taxes = None
        self.Investment_Tax_Credit = None
        self.Other_Funds = None
        self.Funds_from_Operations = None
        self.Extraordinaries = None
        self.Changes_in_Working_Capital = None
        self.Receivables = None
        self.Inventories = None
        self.Accounts_Payable = None
        self.Income_Taxes_Payable = None
        self.Other_Accruals = None
        self.Other_Assets_Liabilities = None
        self.Net_Operating_Cash_Flow = None
        self.Net_Operating_Cash_Flow_Growth = None
        self.Net_Operating_Cash_Flow_Sales = None
        for ind_name, i in zip(ind_name_list, ind_enumerate_list):
            ind_name = get_rid_of_special_characters(ind_name)
            setattr(self, str(ind_name), Indicator(i, years_list, df))


class Indicator(object):
    def __init__(self, i, years_list, df):
        for y in years_list:
            #_y = '_' + y
            val = df[y][i]
            val = transform_val(val)
            setattr(self, y, val)

    def __float__(self, year):
        return getattr(self, year)

    def val(self, year):
        return getattr(self, year)

#priceclass
class Price():
    # def __init__(self, tic, years_list, fiscal_year_end, price_df_m, price_df_d):
    def __init__(self, tic, periods_list, fiscal_year_end, price_df, frequency):
        self.max = None
        self.min = None
        self.open = None
        self.close = None
        self.current = None
        prop = ['max', 'min', 'open', 'close', 'current']
        for p in prop:
            if p == 'current':
                val = current_price_download(tic)
                self.current = float(val)
            else:
                setattr(self, p, Price_year_quarter(p, periods_list, price_df, fiscal_year_end, frequency))

    def __float__(self, val):
        return self.current


def month_name_num_dict():
    month_dict = {'Jan': '01',
                  'Feb': '02',
                  'Mar': '03',
                  'Apr': '04',
                  'May': '05',
                  'Jun': '06',
                  'Jul': '07',
                  'Aug': '08',
                  'Sep': '09',
                  'Oct': '10',
                  'Nov': '11',
                  'Dec': '12'
                  }
    return month_dict


def get_month_name_quarter_dict():
    month_dict = {'Jan': '1',
                  'Feb': '1',
                  'Mar': '1',
                  'Apr': '2',
                  'May': '2',
                  'Jun': '2',
                  'Jul': '3',
                  'Aug': '3',
                  'Sep': '3',
                  'Oct': '4',
                  'Nov': '4',
                  'Dec': '4'
                  }
    return month_dict

#priceclass
class Price_year_quarter():
    #sciagnely sie zbyt krotkie tabele - powod bledu
    # trzeba usunac wiersze z NaN - nie przeszkadzaja ale nie potrzebne w miesiacach
    def __init__(self, p, periods_list, price_df, fiscal_year_end, frequency):
        if frequency == 'q':
            month_dict = month_name_num_dict()
            for quarter in periods_list:
                #quarter_end = transform_quarter(quarter, 'end')
                #quarter_start = transform_quarter(quarter, 'start')
                year = get_year(quarter)
                month_name = get_month_name(quarter)
                month_num = month_dict[month_name]
                day = get_day(quarter)
                quarter_end = '{0}-{1}-{2}'.format(year, month_num, day)
                quarter_end = dt.datetime.strptime(quarter_end, '%Y-%m-%d')

                quarter_start = quarter_end + pd.DateOffset(months=-2)
                quarter_start = str(quarter_start)[:8] + '01'
                quarter_start = dt.datetime.strptime(quarter_start, '%Y-%m-%d')

                quarter_end_ind = find_index_of_date(quarter_start, price_df)
                quarter_start_ind = find_index_of_date(quarter_end, price_df)

                df = price_df.iloc[quarter_start_ind:quarter_end_ind, :]

                if p == 'max':
                    val = df['High'].max()
                elif p == 'min':
                    val = df['Low'].min()
                elif p == 'open':
                    val = df.loc[:, 'Open'].iloc[-1]
                elif p == 'close':
                    val = df.loc[:, 'Close'].iloc[0]
                val = float(val)
                setattr(self, str(quarter), val)

        if frequency == 'y':
            for year in periods_list:
                initial_date = '{0}-{1}-{2}'.format(year, fiscal_year_end, '01')
                # if frequency == 'm':
                #     fiscal_y_start = dt.datetime.strptime(initial_date, '%Y-%m-%d') + pd.DateOffset(years=-1, months=1)
                #     fiscal_y_end = dt.datetime.strptime(initial_date, '%Y-%m-%d')

                fiscal_y_start = dt.datetime.strptime(initial_date, '%Y-%m-%d') + pd.DateOffset(years=-1, months=1)
                fiscal_y_end = dt.datetime.strptime(initial_date, '%Y-%m-%d') + pd.DateOffset(months=1, days=-1)
                start_fiscal_year_ind = find_index_of_date(fiscal_y_start, price_df)
                end_fiscal_year_ind = find_index_of_date(fiscal_y_end, price_df)
                df = price_df.iloc[end_fiscal_year_ind:start_fiscal_year_ind, :]
                if p == 'max':
                    val = df['High'].max()
                elif p == 'min':
                    val = df['Low'].min()
                elif p == 'open':
                    val = df.loc[:, 'Open'].iloc[-1]
                elif p == 'close':
                    val = df.loc[:, 'Close'].iloc[0]
                val = float(val)
                setattr(self, str(year), val)

    def val(self, period):
        return getattr(self, period)

# fsc __detect_errors
def detect_errors(table, columns):
    global cursor

    error_detected = False
    if 'cursor' not in globals():
        cursor, wsj_conn, engine = create_sql_connection('wsj')

    for col in columns:
        if '0001' in col:
            error_detected = True
            update.repair_column_name(table, col, cursor)

    return error_detected


def create_sql_connection(database):
    server = 'KOMPUTER\SQLEXPRESS'
    driver = 'SQL Server'
    wsj_conn = pyodbc.connect(f'Driver={{SQL Server}}; Server=KOMPUTER\SQLEXPRESS; Database={database}; Trusted_Connection=yes')
    wsj_conn.autocommit = True
    database_con = f'mssql://@{server}/{database}?driver={driver}'
    engine = sqlalchemy.create_engine(database_con)
    cursor = wsj_conn.cursor()
    return cursor, wsj_conn, engine


def create_basic_ticker_table_name(ticker):
    ticker_income_statement_y = ticker + '_income_statement_y'
    ticker_income_statement_q = ticker + '_income_statement_q'
    ticker_balance_assets_y = ticker + '_balance_assets_y'
    ticker_balance_assets_q = ticker + '_balance_assets_q'
    ticker_balance_liabilities_y = ticker + '_balance_liabilities_y'
    ticker_balance_liabilities_q = ticker + '_balance_liabilities_q'
    ticker_cash_flow_y = ticker + '_cash_flow_y'
    ticker_cash_flow_q = ticker + '_cash_flow_q'
    ticker_basic_tables = [ticker_income_statement_y, ticker_income_statement_q,
                     ticker_balance_assets_y, ticker_balance_assets_q,
                     ticker_balance_liabilities_y, ticker_balance_liabilities_q,
                     ticker_cash_flow_y, ticker_cash_flow_q]
    return ticker_basic_tables


def create_advanced_ticker_table_name(ticker):
    ticker_profile = ticker + '_profile'
    ticker_price_history_1d = ticker + '_price_history_1d'
    # ticker_price_history_1mo = ticker + '_price_history_1mo'
    # ticker_advanced_tables = [ticker_profile, ticker_price_history_1d, ticker_price_history_1mo]
    ticker_advanced_tables = [ticker_profile, ticker_price_history_1d]
    return ticker_advanced_tables


def all_tables_available(ticker):
    necessary_tables = create_basic_ticker_table_name(ticker) + create_advanced_ticker_table_name(ticker)
    cursor, wsj_conn, engine = create_sql_connection('wsj')
    sql_table_list = get_all_tables(cursor)
    wsj_conn.close()
    if all(t in sql_table_list for t in necessary_tables):
        return True
    else:
        return False


# fsc pod nazwa __select_all_to_df
def get_this_table_df(tabl, conn):
    sql_select_all = 'SELECT * FROM {}'.format(tabl)
    df = pd.read_sql(sql_select_all, con=conn)
    return df


def classes_from_sql(ticker):
    # import danych z sql i tworzenie klas
    wsj_conn = pyodbc.connect('Driver={SQL Server}; Server=KOMPUTER\SQLEXPRESS; Database=wsj; Trusted_Connection=yes')
    wsj_conn.autocommit = True
    ticker_tables = create_basic_ticker_table_name(ticker)
    num = 0
    for tic_tabl in ticker_tables:
        df = get_this_table_df(tic_tabl, wsj_conn)
        # tworzenie listy kolumn, lat i wskaznikow
        columns_list = list(df.columns)

        # wykrycie błędów i powtórzenie importu df
        detected_error = detect_errors(tic_tabl, columns_list)
        if detected_error is True:
            df = get_this_table_df(tic_tabl, wsj_conn)
            columns_list = list(df.columns)

        years_list = columns_list[2:]
        ind_name_list = []
        ind_enumerate_list = []
        for ind in df.index:
            ind_enumerate_list.append(ind)
            ind_name_list.append(df[columns_list[1]][ind])
        if num == 0:
            all_years_statements = years_list
            isy = IncomeStatement(ind_name_list, ind_enumerate_list, years_list, df)
        elif num == 1:
            all_quarters = years_list
            isq = IncomeStatement(ind_name_list, ind_enumerate_list, years_list, df)
        elif num == 2:
            bay = BalanceAssets(ind_name_list, ind_enumerate_list, years_list, df)
        elif num == 3:
            baq = BalanceAssets(ind_name_list, ind_enumerate_list, years_list, df)
        elif num == 4:
            bly = BalanceLiabilities(ind_name_list, ind_enumerate_list, years_list, df)
        elif num == 5:
            blq = BalanceLiabilities(ind_name_list, ind_enumerate_list, years_list, df)
        elif num == 6:
            cfy = CashFlow(ind_name_list, ind_enumerate_list, years_list, df)
        elif num == 7:
            cfq = CashFlow(ind_name_list, ind_enumerate_list, years_list, df)
        num += 1

    # ticker_price_history = ticker + '_price_history_1mo'
    # sql_select_all = 'SELECT * FROM {}'.format(ticker_price_history)
    # price_df = pd.read_sql(sql_select_all, wsj_conn)

    ticker_profile = ticker + '_profile'
    sql_select_all = 'SELECT * FROM {}'.format(ticker_profile)
    df = pd.read_sql(sql_select_all, con=wsj_conn)
    month_num = {'Jan': [1, 31], 'Feb': [2, 28], 'Mar': [3, 31], 'Apr': [4, 30], 'May': [5, 31], 'Jun': [6, 30],
                 'Jul': [7, 31], 'Aug': [8, 31], 'Sep': [9, 30], 'Oct': [10, 31], 'Nov': [11, 30], 'Dec': [12, 31]}
    fiscal_year_end = df.loc[0, 'Fiscal Year Ends'][0:3]
    fiscal_year_end = month_num[fiscal_year_end][0]
    # price_df_m, price_df_d, all_years = create_price_dfs(ticker, all_years_statements, fiscal_year_end)
    price_df_d, all_years = create_price_dfs(ticker, all_years_statements, fiscal_year_end)
    # price = Price(ticker, all_years, fiscal_year_end, price_df_m, price_df_d)
    price_y = Price(ticker, all_years, fiscal_year_end, price_df_d, 'y')
    price_q = Price(ticker, all_quarters, fiscal_year_end, price_df_d, 'q')

    wsj_conn.close()
    return isy, isq, bay, baq, bly, blq, cfy, cfq, price_y, price_q, all_years, all_quarters


def get_all_tables(cursor):
    #wsj_select_table = "SELECT DISTINCT TABLE_NAME FROM information_schema.TABLES"
    wsj_select_table = "SELECT [name] AS TableName FROM sys.tables"
    cursor.execute(wsj_select_table)
    sql_table_list = []
    res = cursor.fetchall()
    for tabl in res:
        sql_table_list.append(tabl[0])
    return sql_table_list


def price_history_5y(df):
    df = df.drop(df[df['Date'].map(len) != 10].index)
    df.reset_index(drop=True, inplace=True)
    df.sort_values('Date', ascending=False, inplace=True)
    df = df.head(1826)
    df.reset_index(drop=True, inplace=True)
    return df

#priceclass
def find_index_of_date(mydate, df):
    mydate = str(mydate.date())
    while mydate not in df['Date'].values:
        mydate = dt.datetime.strptime(mydate, '%Y-%m-%d')
        mydate = mydate + pd.DateOffset(days=1)
        mydate = str(mydate.date())
    mydate = df.index[(df['Date'] == mydate)][0]
    return mydate


def create_price_dfs(ticker, all_years_statements, fiscal_year_end):

    cursor, wsj_conn, engine = create_sql_connection('wsj')

    # ticker_price_history_m = ticker + '_price_history_1mo'
    # sql_select_all_m = 'SELECT * FROM {0}'.format(ticker_price_history_m)
    # price_df_m = pd.read_sql(sql_select_all_m, wsj_conn)

    ticker_price_history_d = ticker + '_price_history_1d'
    sql_select_all_d = 'SELECT * FROM {0} order by date desc'.format(ticker_price_history_d)
    price_df_d = pd.read_sql(sql_select_all_d, wsj_conn)

    wsj_conn.close()
    st = dt.datetime.now()
    all_years = []
    months = list(range(13))[1:]
    months = months[fiscal_year_end:] + months[:fiscal_year_end]
    for y in all_years_statements:
        one_year_months = []
        for m in months:
            # one_year_months.append(str(dt.date(int(y), m, 1)))
            one_year_months.append(str(dt.date(int(y), m, 1))[:7])
        # if all(x in price_df_m['Date'].values for x in one_year_months) is True:
        #    all_years.append(y)
        price_date_l = price_df_d['Date'].values.tolist()
        price_date_l = [x[:7] for x in price_date_l]
        if all(x in price_date_l for x in one_year_months) is True:
            all_years.append(y)
    # return price_df_m, price_df_d, all_years
    return price_df_d, all_years


def pandas_df_display_options():
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 20)
    pd.set_option('display.width', 400)


def get_total_number_and_range_of_all_tickers(tickers_list):
    total_number = len(tickers_list)
    total_number_range = range(len(tickers_list) + 1)[1:]
    print(total_number)
    return total_number, total_number_range


def transform_dataframe_columns_with_month_names_to_numbers(dfcolumns):
    df_non_date_cols = [col for col in dfcolumns if '20' not in col]
    df_date_cols = [col for col in dfcolumns if '20' in col]
    df_date_cols = transform_dates_list_with_month_names_to_numbers(df_date_cols)
    dfcolumns = df_non_date_cols[:2] + df_date_cols #+ [df_non_date_cols[-1]] last column was current
    return dfcolumns


def transform_dates_list_with_month_names_to_numbers(mylist):
    updated_list = [transform_date_with_month_names_to_numbers(i) for i in mylist]
    return updated_list


def transform_date_with_month_names_to_numbers(mydate):
    year = get_year(mydate)
    month_name = get_month_name(mydate)
    day = get_day(mydate)
    monthnamenumdict = month_name_num_dict()
    month_num = monthnamenumdict[month_name]
    updated_date = year + '-' + month_num + '-' + day
    return updated_date


def get_year(ystr):
    pos = ystr.find('-') + 1
    ystr = ystr[pos:]
    pos = ystr.find('-') + 1
    ynum = ystr[pos:]
    return ynum


def get_month_name(mstr):
    pos = mstr.find('-')
    mstart = pos + 1
    mend = pos + 4
    mname = mstr[mstart:mend]
    return mname


def get_day(dstr):
    pos = dstr.find('-')
    dnum = dstr[:pos]
    return dnum


def get_transform_dates_to_quarters(headers):

    def get_month_year(x):
        x = x.split('-')
        month = x[1]
        year = x[2]
        return month, year

    static_cols = [x for x in headers if '-20' not in x]
    date_cols = [x for x in headers if '-20' in x]
    month_name_quarter_dict = get_month_name_quarter_dict()
    new_dates_cols = []
    for c in date_cols:
        m, y = get_month_year(c)
        q = month_name_quarter_dict[m]
        yq = y + '-' + q
        new_dates_cols.append(yq)
    if 'Current' in static_cols:
        static_cols.remove('Current')
        new_dates_cols = new_dates_cols + ['Current']
    new_cols = static_cols + new_dates_cols
    return new_cols


def convert_date_with_month_name_to_number(mydate):
    month_dict = month_name_num_dict()
    year = get_year(mydate)
    month_num = month_dict[get_month_name(mydate)]
    day = get_day(mydate)
    mydate = f'{year}-{month_num}-{day}'
    return mydate


def get_stock_currency(ticker_name, cursor):
    sql_query = f'''
                SELECT name AS COLUMN_NAME
                FROM sys.columns
                WHERE object_id = OBJECT_ID(\'[wsj].[dbo].[{ticker_name}_income_statement_y]\')'''
    cursor.execute(sql_query)
    res = cursor.fetchall()[1][0]
    currency = None
    if 'Fiscal year' in res:  # na wypadek innej nazwy kolumny
        if 'USD' in res:
            currency = 'USD'
        elif 'EUR' in res:
            currency = 'EUR'
        elif 'HKD' in res:
            currency = 'HKD'
    else:
        print('ERROR! Nie znaleziono kolumny do pozyskania wartosci currency!')
    return currency


def fixed_tickers_colors():
    mydict = {'AMD': '#000000',
              'AMZN': '#ff9900',
              'AVGO': '#CC092F',
              'GOOGL': '#34A853',
              'INTC': '#0068B5',
              'MCD': '#FFC72C',
              'META': '#0080FB',
              'MSFT': '#FFB900',
              'NFLX': '#D81F26',
              'NVDA': '#76B900',
              'QCOM': '#3253DC'
    }
    return mydict


def colors():

    def get_random_colors(num_colors):
        random_colors = []
        for _ in range(num_colors):
            # Generate random RGB values
            r, g, b = random.random(), random.random(), random.random()
            # Convert RGB to hexadecimal color code
            color = mcolors.to_hex((r, g, b))
            random_colors.append(color)
        return random_colors

    colors = get_random_colors(500)

    return colors


def quarters_generator():
    # 2021-1 data poczatkowa
    y = 2021
    q = 1
    q_dates_l = []
    while y <= dt.datetime.today().year:
        q_date = str(y) + '-' + str(q)
        q_dates_l.append(q_date)
        q += 1
        if q == 5:
            y += 1
            q = 1
    return q_dates_l


def years_generator():
    y = 2017
    years_l = []
    current_year = dt.datetime.today().year
    while y <= current_year:
        years_l.append(str(y))
        y += 1
    return years_l
