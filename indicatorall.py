import datetime
import pandas as pd
import utilities as u



def get_all_indicators(wsja_cursor):
    sql_query = f'SELECT Indicators FROM [wsja].[dbo].[analysis_META_year]'
    wsja_cursor.execute(sql_query)
    res = [x[0] for x in wsja_cursor.fetchall()]
    return res


def get_all_analysis_tables(cursor):
    sql_table_list = u.get_all_tables(cursor)
    analysis_tables = [t for t in sql_table_list if 'analysis' in t]
    return analysis_tables


def all_sectors_industries(tickers_list, wsj_cursor):
    sectors = []
    industries = []
    for tic in tickers_list:
        sql_query = f'SELECT * FROM [wsj].[dbo].[{tic}_profile]'
        wsj_cursor.execute(sql_query)
        profile_vals = wsj_cursor.fetchall()
        sector = profile_vals[0][0]
        sectors.append(sector)
        industry = profile_vals[0][1]
        industries.append(industry)
    sectors = set(sectors)
    industries = set(industries)
    return sectors, industries


class TicBranches:
    def __init__(self, tickers_l, wsj_cursor):
        for tic in tickers_l:
            setattr(self, tic, TicBranch(tic, wsj_cursor))


class TicBranch:
    def __init__(self, tic_name, wsj_cursor):
        def get_sector_industry():
            sql_query = f'SELECT * FROM [wsj].[dbo].[{self.tic_name}_profile]'
            wsj_cursor.execute(sql_query)
            profile_vals = wsj_cursor.fetchall()
            sector = profile_vals[0][0]
            industry = profile_vals[0][1]
            setattr(self, 'sector', sector)
            setattr(self, 'industry', industry)
        self.tic_name = tic_name
        self.sector = None
        self.industry = None
        get_sector_industry()


class IndicatorAll:
    def __init__(self, tickers_l, indicator, industry, sector, period,
                 wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):

        self.wsj_cursor, self.wsj_conn, self.wsj_engine = wsj_cursor, wsj_conn, wsj_engine
        self.wsja_cursor, self.wsja_conn, self.wsja_engine = wsja_cursor, wsja_conn, wsja_engine
        self.indicator = indicator
        self.sector = sector
        self.industry = industry

        self.tic_branches = TicBranches(tickers_l, self.wsj_cursor)
        self.filtered_tickers_l = []
        self.filtered_sectors = set()
        self.filtered_industries = set()
        for tic in tickers_l:
            tic_industry = getattr(self.tic_branches, tic).industry
            tic_sector = getattr(self.tic_branches, tic).sector
            if (len(self.industry) == 0 or tic_industry in self.industry) and (len(self.sector) == 0 or tic_sector in self.sector):
                self.filtered_tickers_l.append(tic)
                self.filtered_industries.add(tic_industry)
                self.filtered_sectors.add(tic_sector)
        self.period = period
        if self.period == 'year':
            self.dates = u.years_generator()
        else:
            self.dates = u.quarters_generator()

        self.dict = None
        self.get_dictionary()
        self.df = pd.DataFrame(self.dict)

        rows = wsja_cursor.execute('SELECT Indicators from wsja.dbo.analysis_META_year').fetchall()
        self.indicators_l = [r[0] for r in rows]

    def get_dictionary(self):
        # fulfill dictionary wiht indicator values from every ticker
        # ticker: [tic1, tic2], 2022-1: [1, 3]

        self.dict = dict.fromkeys(['tickers', 'sector', 'industry'] + self.dates + ['Current'], [])
        for tic_name in self.filtered_tickers_l:
            sql_query = f'SELECT * FROM [wsja].[dbo].[analysis_{tic_name}_{self.period}] where indicators = \'{self.indicator}\''
            self.wsja_cursor.execute(sql_query)

            vals = list(self.wsja_cursor.fetchall()[0][2:])

            if self.period == 'quarter':
                headers = [i[0] for i in self.wsja_cursor.description]
                static_cols, date_cols = u.get_transform_dates_to_quarters(headers)  # transformacja dat kwartalnych
            else:
                headers = [i[0] for i in self.wsja_cursor.description]
                static_cols = [x for x in headers if '20' not in x and x != 'Current']
                date_cols = [x for x in headers if '20' in x or x == 'Current']
            self.dict['tickers'] = self.dict['tickers'] + [tic_name]
            self.dict['sector'] = self.dict['sector'] + [getattr(self.tic_branches, tic_name).sector]
            self.dict['industry'] = self.dict['industry'] + [getattr(self.tic_branches, tic_name).industry]

            tmp_dict = {}
            for col, val in zip(date_cols, vals):
                tmp_dict[col] = val
            for k in self.dict.keys():
                if k not in ['tickers', 'sector', 'industry']:
                    if k in date_cols:
                        self.dict[k] = self.dict[k] + [tmp_dict[k]]
                    else:
                        self.dict[k] = self.dict[k] + [None]

    def get_x(self):
        return list(self.df.columns)[3:]

    def get_y(self):
        return [x[3:] for x in self.df.values]

    def get_sectors(self):
        return self.df['sector'].tolist()

    def get_industries(self):
        return self.df['industry'].tolist()

    def assign_colors(self, mylist):
        #colors = sns.color_palette("Paired")
        colors = u.colors()
        dictinct_values = set(mylist)
        if len(colors) < len(dictinct_values):
            print('ERROR! lista unikalnych wartosci jest dluzsza od listy kolorow')
        distinctval_color_dict = dict(zip(dictinct_values, colors))
        res_colors = [distinctval_color_dict[x] for x in mylist]
        return res_colors


    #def set_data(self):
    #    if self.statement == 'analysis' and self.period == 'year':
    #        self.tic.set_df_year()
    #    elif self.statement == 'analysis' and self.period == 'quarter':
    #        self.tic.set_df_quarter()
    #    elif self.statement == 'is' and self.period == 'year':
    #        self.tic.set_is_df_y()
    #    elif self.statement == 'is' and self.period == 'quarter':
    #        self.tic.set_is_df_q()
    #    elif self.statement == 'ba' and self.period == 'year':
    #        self.tic.set_ba_df_y()
    #    elif self.statement == 'ba' and self.period == 'quarter':
    #        self.tic.set_ba_df_q()
    #    elif self.statement == 'bl' and self.period == 'year':
    #        self.tic.set_bl_df_y()
    #    elif self.statement == 'bl' and self.period == 'quarter':
    #        self.tic.set_bl_df_q()
    #    elif self.statement == 'cf' and self.period == 'year':
    #        self.tic.set_cf_df_y()
    #    elif self.statement == 'cf' and self.period == 'quarter':
    #        self.tic.set_cf_df_q()
    #
    #def update(self, statement, period):
    #    self.statement = statement
    #    self.period = period
    #
    #def get_data(self):
    #    for tic_name in tickers_l:
    #        self.tic = Ticker(tic_name, self.wsj_cursor, self.wsj_conn, self.wsj_engine, self.wsja_cursor, self.wsja_conn,
    #                     self.wsja_engine)
            
        
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

#u.pandas_df_display_options()
#wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
#wsja_cursor, wsja_conn, wsja_engine = u.create_sql_connection('wsja')
#tickers_list = ['GOOGL', 'META', 'NFLX']
#

#get_all_indicators(wsja_cursor)

#sectors, industries = all_sectors_industries(tickers_list)
#
#psq = IndicatorAll(tickers_list, 'P/S', 'year', wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
#
#print(psq.df)







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


