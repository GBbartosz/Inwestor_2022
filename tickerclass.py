import pandas as pd
import utilities as u


def transform_dates_to_quarters(df):

    def get_month_year(x):
        x = x.split('-')
        month = x[1]
        year = x[2]
        return month, year

    cols = df.columns
    cols = [x for x in cols if x  not in ['Ticker', 'Indicators', 'Current']]
    month_name_quarter_dict = u.month_name_quarter_dict()
    new_cols = []
    for c in cols:
        m, y = get_month_year(c)
        q = month_name_quarter_dict[m]
        yq = y + '-' + q
        new_cols.append(yq)
    df.columns = ['Ticker', 'Indicators'] + new_cols + ['Current']
    return df


class Ticker:
    def __init__(self, ticker, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):
        self.ticker = ticker
        self.df_y = None
        self.df_q = None
        self.is_df_y = None
        self.is_df_q = None
        self.wsj_cursor, self.wsj_conn, self.wsj_engine = wsj_cursor, wsj_conn, wsj_engine
        self.wsja_cursor, self.wsja_conn, self.wsja_engine = wsja_cursor, wsja_conn, wsja_engine
        sector_industry = pd.read_sql(f'SELECT * FROM wsj.dbo.{ticker}_profile', self.wsj_conn).iloc[0, :].tolist()
        self.secotor = sector_industry[0]
        self.industry = sector_industry[1]
        setattr(self, 'tables', TickerTables(ticker))

    def create_indicators(self):

        def create_indicators2(df, time_type):
            indicators = df['Indicators'].tolist()
            for i in indicators:
                name = str(i) + time_type
                setattr(self, name, chosen_indicator(df, i))

        def chosen_indicator(df, i):
            # res = df[df['Indicators'] == i].iloc[0, 2:].tolist()
            mdict = df[df['Indicators'] == i].iloc[0:, 2:].to_dict('records')[0]
            mdict.pop('Current')
            return mdict

        if self.df_y is not None:
            create_indicators2(self.df_y, '_y')
        if self.df_q is not None:
            self.df_q = transform_dates_to_quarters(self.df_q)
            create_indicators2(self.df_q, '_q')

    def set_df_year(self):
        sql_query = f'SELECT * FROM {self.tables.year}'
        df = pd.read_sql(sql_query, self.wsja_conn)
        self.df_y = df

    # def get_df_year(self):
    #    return self.df_y

    def set_df_quarter(self):
        sql_query = f'SELECT * FROM {self.tables.quarter}'
        df = pd.read_sql(sql_query, self.wsja_conn)
        self.df_q = df

    def set_income_statment_df_year(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.ticker}_income_statement_y'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.is_df_y = df

    def set_income_statment_df_quarter(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.ticker}_income_statement_q'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.is_df_q = df

    # def get_df_quarter(self):
    #    return self.df_q


class TickerTables:
    def __init__(self, ticker):
        self.year = f'wsj.dbo.analysis_{ticker}_year'
        self.quarter = f'wsj.dbo.analysis_{ticker}_quarter'
        self.glob = f'wsj.dbo.analysis_{ticker}_global'







#wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
#wsja_cursor, wsja_conn, wsja_engine = u.create_sql_connection('wsja')
#tic = Ticker('GOOGL', wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
#tic.set_df_year()
#tic.set_df_quarter()
#tic.create_indicators()

