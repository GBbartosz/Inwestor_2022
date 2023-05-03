import pandas as pd
import utilities as u
import time


class AnalysisDatabase:
    def __init__(self, tickers_list, indicators_dict, wsj_conn):
        for ticker in tickers_list:
            setattr(self, ticker, Ticker(ticker))
        for indicator in indicators_dict.keys():
            setattr(self, indicator, Indicator(indicator, indicators_dict, tickers_list, wsj_conn))


class Ticker:
    def __init__(self, ticker):
        setattr(self, 'tables', TickerTables(ticker))

    def get_df(self, wsj_conn):
        sql_query = 'SELECT * FROM {}'.format(self.tables.year)
        df = pd.read_sql(sql_query, wsj_conn)
        return df


class TickerTables:
    def __init__(self, ticker):
        self.year = 'analysis_{}_year'.format(ticker)
        self.quarter = 'analysis_{}_quarter'.format(ticker)
        self.glob = 'analysis_{}_global'.format(ticker)


class Indicator:
    def __init__(self, indicator, indicators_dict, tickers_list, wsj_conn):
        self.index = indicators_dict[indicator]

        df = None
        for ticker in tickers_list:
            tic = Ticker(ticker)
            #sql_query = 'SELECT * FROM wsj.dbo.{} WHERE index = {}'.format(tic.tables.year, self.index)
            sql_query = 'SELECT * FROM wsj.dbo.{} WHERE index = {}'.format(Ticker(ticker).tables.year, self.index)
            tic_df = pd.read_sql(sql_query, wsj_conn).iloc[:, 2:]
            #tic_df = tic_df.loc[:, tic_df.columns != 'Current']
            tic_df = transform_dates_to_quarters(tic_df)
            tic_df['ticker'] = [ticker]
            df = df_concat(df, tic_df)


def transform_dates_to_quarters(df):

    def get_month_year(x):
        x = x.split('-')
        month = x[1]
        year = x[2]
        return month, year

    cols = df.columns
    cols.remove('Current')
    month_name_quarter_dict = u.month_name_quarter_dict()
    new_cols = []
    for c in cols:
        m, y = get_month_year(c)
        q = month_name_quarter_dict[m]
        yq = y + '-' + q
        new_cols.append(yq)
    df.columns = new_cols + ['Current']
    return df


def df_concat(df, tic_df):
    if df is None:
        df = tic_df
    else:
        df = pd.concat([df, tic_df], axis=0, ignore_index=True)
    return df


def get_all_analysis_tables(cursor):
    sql_table_list = u.get_all_tables(cursor)
    analysis_tables = [t for t in sql_table_list if 'analysis' in t]
    print(analysis_tables)
    return sql_table_list


def convert_reports_dates_to_quarters():
    pass


def get_indicators_dict(wsj_conn):
    sql_query = 'SELECT * FROM wsj.dbo.analysis_META_YEAR'
    df = pd.read_sql(sql_query, wsj_conn)
    index_list = indicators_list = df.iloc[:, 0].values
    indicators_list = df.iloc[:, 1].values
    indicators_dict = {}
    for index, indicator in zip(index_list, indicators_list):
        indicators_dict[indicator] = index
    print(indicators_dict)
    return indicators_dict


def dashboard():
    u.pandas_df_display_options()
    tickers_list = ['GOOGL', 'META', 'NFLX']                                                   #dodac jako argument
    cursor, wsj_conn, engine = u.create_sql_connection()
    indicators_dict = get_indicators_dict(wsj_conn)
    #sql_analysis_tables = get_all_analysis_tables(cursor)
    adb = AnalysisDatabase(tickers_list, indicators_dict, wsj_conn)
    print(adb.META.tables.year)
    print(adb.META.get_df(wsj_conn))



start_time = time.time()
dashboard()
end_time = time.time()
print(end_time - start_time)
