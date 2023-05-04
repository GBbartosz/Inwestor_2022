import utilities as u


def get_all_analysis_tables(cursor):
    sql_table_list = u.get_all_tables(cursor)
    analysis_tables = [t for t in sql_table_list if 'analysis' in t]
    return sql_table_list


class IndicatorAll:
    def __init__(self, mydate, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):
        self.df_y = None
        self.df_q = None
        self.wsj_cursor, self.wsj_conn, self.wsj_engine = wsj_cursor, wsj_conn, wsj_engine
        self.wsja_cursor, self.wsja_conn, self.wsja_engine = wsja_cursor, wsja_conn, wsja_engine






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


