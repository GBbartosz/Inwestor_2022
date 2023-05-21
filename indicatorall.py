import datetime

import pandas as pd

import utilities as u
from tickerclass import Ticker
import plotly.graph_objs as go


def quarters_generator():
    y = 2021
    q = 1
    q_dates_l = []
    while y <= datetime.datetime.today().year:
        q_date = str(y) + '-' + str(q)
        q_dates_l.append(q_date)
        q += 1
        if q == 5:
            y += 1
            q = 1
    return q_dates_l


def years_generator():
    y = 2017
    years_l =[]
    while y <= datetime.datetime.today().year:
        years_l.append()
        y += 1
    return years_l

def get_all_analysis_tables(cursor):
    sql_table_list = u.get_all_tables(cursor)
    analysis_tables = [t for t in sql_table_list if 'analysis' in t]
    return sql_table_list


class IndicatorAll:
    def __init__(self, tickers_l, indicator, period, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):
        self.indicator = indicator
        self.tickers_l = tickers_l
        self.period = period
        self.wsj_cursor, self.wsj_conn, self.wsj_engine = wsj_cursor, wsj_conn, wsj_engine
        self.wsja_cursor, self.wsja_conn, self.wsja_engine = wsja_cursor, wsja_conn, wsja_engine

        if self.period == 'year':
            self.dates = years_generator()
        else:
            self.dates = quarters_generator()

        self.dict = None
        self.get_dictionary()

    def get_dictionary(self):
        # fulfill dictionary wiht indicator values from every ticker
        # ticker: [tic1, tic2], 2022-1: [1, 3]
        self.dict = dict.fromkeys(['tickers'] + self.dates + ['Current'], [])
        for tic_name in self.tickers_l:
            sql_query = f'SELECT * FROM wsj.dbo.analysis_{tic_name}_{self.period} where indicators = \'{self.indicator}\''
            self.wsja_cursor.execute(sql_query)
            vals = list(self.wsja_cursor.fetchall()[0][2:])
            headers = [i[0] for i in wsja_cursor.description]
            static_cols, date_cols = u.get_transform_dates_to_quarters(headers)
            date_cols = date_cols + [static_cols[-1]]

            self.dict['tickers'] = self.dict['tickers'] + [tic_name]
            tmp_dict = {}
            for col, val in zip(date_cols, vals):
                tmp_dict[col] = val
            for k in self.dict.keys():
                if k != 'tickers':
                    if k not in date_cols and k:
                        self.dict[k] = self.dict[k] + [None]
                    else:
                        self.dict[k] = self.dict[k] + [tmp_dict[k]]



        self.df_y = None
        self.df_q = None

        self.tic = None
        self.statement = None
        self.period = None

        #rows = wsja_cursor.execute('SELECT Indicators from wsja.dbo.analysis_META_year').fetchall()
        #self.indicators_l = [r[0] for r in rows]



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

wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
wsja_cursor, wsja_conn, wsja_engine = u.create_sql_connection('wsja')
tickers_list = ['GOOGL', 'META', 'NFLX']

ind = IndicatorAll(tickers_list, 'P/S', 'quarter', wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
print(ind.dict)







#data=pd.DataFrame({'dates': ['2022', '2023', '2022', '2023', '2022', '2023'],
#                   'vals': [1, 1.2, 1.7, 1.8, 3, 2.8],
#                   'ticker': ['META', 'META', 'GOOGL', 'GOOGL', 'NETFLIX', 'NETFLIX']})
#
#data = data.pivot(index='ticker', columns='dates')['vals'].fillna(0)
#print(data)

#fig = go.Figure()
#for tic in data.index:
#    print(data[data.index == tic].iloc[0, :].tolist())
#    fig.add_trace(go.Scatter(x=data.columns,
#                             y=data[data.index == tic].iloc[0, :].tolist(),
#                             text=tic,
#                             mode='lines+markers',
#                             line = dict(shape = 'linear', color = 'rgb(205, 12, 24)', width= 0.3, dash = 'dash')))
#fig.show()


