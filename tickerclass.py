import pandas as pd
import utilities as u


def dictionary_values_to_list(mydict):
    return list(mydict.values())


def dictionary_keys_to_list(mydict):
    return list(mydict.keys())


class Ticker:
    def __init__(self, ticker, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):
        self.name = ticker
        self.df_y = None
        self.df_q = None
        self.dates_y = None
        self.dates_q = None
        self.is_df_y = None
        self.is_df_q = None
        self.ba_df_y = None
        self.ba_df_q = None
        self.bl_df_y = None
        self.bl_df_q = None
        self.cf_df_y = None
        self.cf_df_q = None
        self.indicators_names_l = None
        self.wsj_cursor, self.wsj_conn, self.wsj_engine = wsj_cursor, wsj_conn, wsj_engine
        self.wsja_cursor, self.wsja_conn, self.wsja_engine = wsja_cursor, wsja_conn, wsja_engine
        sector_industry = pd.read_sql(f'SELECT * FROM wsj.dbo.{ticker}_profile', self.wsj_conn).iloc[0, :].tolist()
        self.sector = sector_industry[0]
        self.industry = sector_industry[1]
        setattr(self, 'tables', TickerTables(ticker))

    def create_indicators(self):

        def create_indicators2(df, time_type):
            indicators = df['Indicators'].tolist()
            self.indicators_names_l = indicators
            for i in indicators:
                name = str(i) + time_type
                setattr(self, name, ChosenIndicator(df, i, name))

        class ChosenIndicator:
            def __init__(self, df, i, name):
                mdict = df[df['Indicators'] == i].iloc[0:, 2:].to_dict('records')[0]
                #mdict.pop('Current')
                self.name = name
                setattr(self, 'values', dictionary_values_to_list(mdict))
                setattr(self, 'dates', dictionary_keys_to_list(mdict))

        if self.df_y is not None:
            create_indicators2(self.df_y, '_y')
        if self.df_q is not None:
            create_indicators2(self.df_q, '_q')

    def set_df_year(self):
        sql_query = f'SELECT * FROM {self.tables.year}'
        #self.wsja_cursor.execute(sql_query)
        #columns = [col[0] for col in self.wsja_cursor.description]
        #df = pd.DataFrame.from_records(self.wsja_cursor.fetchall(), columns=columns)
        df = pd.read_sql(sql_query, self.wsja_conn)
        self.df_y = df
        self.dates_y = df.columns[2:]

    def set_df_quarter(self):
        sql_query = f'SELECT * FROM {self.tables.quarter}'
        df = pd.read_sql(sql_query, self.wsja_conn)
        static_cols, new_cols = u.get_transform_dates_to_quarters(df.columns)
        df.columns = static_cols + new_cols
        self.df_q = df
        self.dates_q = df.columns[2:]

    def set_is_df_y(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_income_statement_y'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.is_df_y = df

    def set_is_df_q(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_income_statement_q'
        df = pd.read_sql(sql_query, self.wsj_conn)
        static_cols, new_cols = u.get_transform_dates_to_quarters(df.columns)
        df.columns = static_cols + new_cols
        self.is_df_q = df

    def set_ba_df_y(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_balance_assets_y'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.ba_df_y = df

    def set_ba_df_q(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_balance_assets_q'
        df = pd.read_sql(sql_query, self.wsj_conn)
        static_cols, new_cols = u.get_transform_dates_to_quarters(df.columns)
        df.columns = static_cols + new_cols
        self.ba_df_q = df

    def set_bl_df_y(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_balance_liabilities_y'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.bl_df_y = df

    def set_bl_df_q(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_balance_liabilities_q'
        df = pd.read_sql(sql_query, self.wsj_conn)
        static_cols, new_cols = u.get_transform_dates_to_quarters(df.columns)
        df.columns = static_cols + new_cols
        self.bl_df_q = df

    def set_cf_df_y(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_cash_flow_y'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.cf_df_y = df

    def set_cf_df_q(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_cash_flow_q'
        df = pd.read_sql(sql_query, self.wsj_conn)
        static_cols, new_cols = u.get_transform_dates_to_quarters(df.columns)
        df.columns = static_cols + new_cols
        self.cf_df_q = df


class TickerTables:
    def __init__(self, ticker):
        self.year = f'wsja.dbo.analysis_{ticker}_year'
        self.quarter = f'wsja.dbo.analysis_{ticker}_quarter'
        self.glob = f'wsja.dbo.analysis_{ticker}_global'







#wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
#wsja_cursor, wsja_conn, wsja_engine = u.create_sql_connection('wsja')
#tic = Ticker('GOOGL', wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
#tic.set_df_year()
#tic.set_df_quarter()
#tic.create_indicators()

