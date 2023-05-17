import utilities as u
from tickerclass import Ticker

def get_all_analysis_tables(cursor):
    sql_table_list = u.get_all_tables(cursor)
    analysis_tables = [t for t in sql_table_list if 'analysis' in t]
    return sql_table_list


class IndicatorAll:
    def __init__(self, tickers_l, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):
        self.tickers_l = tickers_l
        self.df_y = None
        self.df_q = None
        self.wsj_cursor, self.wsj_conn, self.wsj_engine = wsj_cursor, wsj_conn, wsj_engine
        self.wsja_cursor, self.wsja_conn, self.wsja_engine = wsja_cursor, wsja_conn, wsja_engine
        self.tic = None
        self.statement = None
        self.period = None


    def set_data(self):
        if self.statement == 'analysis' and self.period == 'year':
            self.tic.set_df_year()
        elif self.statement == 'analysis' and self.period == 'quarter':
            self.tic.set_df_quarter()
        elif self.statement == 'is' and self.period == 'year':
            self.tic.set_is_df_y()
        elif self.statement == 'is' and self.period == 'quarter':
            self.tic.set_is_df_q()
        elif self.statement == 'ba' and self.period == 'year':
            self.tic.set_ba_df_y()
        elif self.statement == 'ba' and self.period == 'quarter':
            self.tic.set_ba_df_q()
        elif self.statement == 'bl' and self.period == 'year':
            self.tic.set_bl_df_y()
        elif self.statement == 'bl' and self.period == 'quarter':
            self.tic.set_bl_df_q()
        elif self.statement == 'cf' and self.period == 'year':
            self.tic.set_cf_df_y()
        elif self.statement == 'cf' and self.period == 'quarter':
            self.tic.set_cf_df_q()
        
    def update(self, statement, period):
        self.statement = statement
        self.period = period
        
    def get_data(self):
        for tic_name in tickers_l:
            self.tic = Ticker(tic_name, self.wsj_cursor, self.wsj_conn, self.wsj_engine, self.wsja_cursor, self.wsja_conn, 
                         self.wsja_engine)
            
        
    #def indicator(self):
    #    class Indicator:
    #        def __init__(self, indicator, indicators_dict, tickers_list, wsj_conn):
    #            self.index = indicators_dict[indicator]
#
    #            df = None
    #            for ticker in tickers_list:
    #                tic = Ticker(ticker)
    #                # sql_query = 'SELECT * FROM wsj.dbo.{} WHERE index = {}'.format(tic.tables.year, self.index)
    #                sql_query = 'SELECT * FROM wsj.dbo.{} WHERE index = {}'.format(Ticker(ticker).tables.year,
    #                                                                               self.index)
    #                tic_df = pd.read_sql(sql_query, wsj_conn).iloc[:, 2:]
    #                # tic_df = tic_df.loc[:, tic_df.columns != 'Current']
    #                tic_df = transform_dates_to_quarters(tic_df)
    #                tic_df['ticker'] = [ticker]
    #                df = df_concat(df, tic_df)

    #def df_concat(df, tic_df):
    #    if df is None:
    #        df = tic_df
    #    else:
    #        df = pd.concat([df, tic_df], axis=0, ignore_index=True)
    #    return df
    ##
#
    #def convert_reports_dates_to_quarters():
    #    pass
#
    #def get_indicators_dict(wsj_conn):
    #    sql_query = 'SELECT * FROM wsj.dbo.analysis_META_YEAR'
    #    df = pd.read_sql(sql_query, wsj_conn)
    #    index_list = indicators_list = df.iloc[:, 0].values
    #    indicators_list = df.iloc[:, 1].values
    #    indicators_dict = {}
    #    for index, indicator in zip(index_list, indicators_list):
    #        indicators_dict[indicator] = index
    #    print(indicators_dict)
    #    return indicators_dict


