import pandas as pd

import utilities as u


def chosen_indicator(df, i):
    res = df[df['Indicators'] == i].iloc[0, 2:].tolist()
    return res


class Ticker:
    def __init__(self, ticker, cursor, wsj_conn, engine):
        self.df_y = None
        self.df_q = None
        self.cursor, self.wsj_conn, self.engine = cursor, wsj_conn, engine
        setattr(self, 'tables', TickerTables(ticker))

    def create_indicators(self):
        indicators = self.df_y['Indicators'].tolist()
        for i in indicators:
            setattr(self, str(i), chosen_indicator(self.df_y, i))

    def set_df_year(self):
        sql_query = 'SELECT * FROM {}'.format(self.tables.year)
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.df_y = df

    # def get_df_year(self):
    #    return self.df_y

    def set_df_quarter(self):
        sql_query = 'SELECT * FROM {}'.format(self.tables.quarter)
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.df_q = df

    # def get_df_quarter(self):
    #    return self.df_q


class TickerTables:
    def __init__(self, ticker):
        self.year = 'wsj.dbo.analysis_{}_year'.format(ticker)
        self.quarter = 'wsj.dbo.analysis_{}_quarter'.format(ticker)
        self.glob = 'wsj.dbo.analysis_{}_global'.format(ticker)


cursor, wsj_conn, engine = u.create_sql_connection('wsja')
tic = Ticker('GOOGL', cursor, wsj_conn, engine)
tic.set_df_year()
print(tic.df_y)
tic.create_indicators()
print(tic.Price)

