import datetime
import pandas as pd
import utilities as u


def get_all_indicators(wsja2_cursor):
    sql_query = f'SELECT Indicator FROM [wsja2].[dbo].[analysis_dis_day_Close_close]'
    wsja2_cursor.execute(sql_query)
    res1 = [x[0] for x in wsja2_cursor.fetchall()]

    sql_query = f'SELECT Indicator FROM [wsja2].[dbo].[analysis_dis_no_price]'
    wsja2_cursor.execute(sql_query)
    res2 = [x[0] for x in wsja2_cursor.fetchall()]

    res = res1 + res2
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
    def __init__(self, tickers_l, indicator, industry, sector, dd_chosen_price,
                 wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine):

        self.wsj_cursor, self.wsj_conn, self.wsj_engine = wsj_cursor, wsj_conn, wsj_engine
        self.wsja2_cursor, self.wsja2_conn, self.wsja2_engine = wsja2_cursor, wsja2_conn, wsja2_engine
        self.tickers_l = tickers_l
        self.indicator = indicator
        self.sector = sector
        self.industry = industry
        self.dd_chosen_price = dd_chosen_price

        self.price_indicators, self.noprice_indicators = self.__price_or_no_price_indicator()

        self.tic_branches = TicBranches(tickers_l, self.wsj_cursor)
        self.filtered_tickers_l = []
        self.filtered_sectors = set()
        self.filtered_industries = set()
        self.__filter_tickers_by_industry_sector()

        self.dict = None
        self.__get_dictionary()

        #rows = wsja2_cursor.execute('SELECT Indicators from wsja.dbo.analysis_META_year').fetchall()
        #self.indicators_l = [r[0] for r in rows]
        self.indicators_l = get_all_indicators(self.wsja2_cursor)

    def __price_or_no_price_indicator(self):
        sql_query = f'''SELECT Indicator FROM [wsja2].[dbo].[analysis_DIS_day_close_close]'''
        self.wsja2_cursor.execute(sql_query)
        price_indicators = [x[0] for x in list(self.wsja2_cursor.fetchall())]

        sql_query = f'''SELECT Indicator FROM [wsja2].[dbo].[analysis_DIS_no_price]'''
        self.wsja2_cursor.execute(sql_query)
        noprice_indicators = [x[0] for x in list(self.wsja2_cursor.fetchall())]
        return price_indicators, noprice_indicators

    def __filter_tickers_by_industry_sector(self):
        for tic in self.tickers_l:
            tic_industry = getattr(self.tic_branches, tic).industry
            tic_sector = getattr(self.tic_branches, tic).sector
            if (len(self.industry) == 0 or tic_industry in self.industry) and (len(self.sector) == 0 or tic_sector in self.sector):
                self.filtered_tickers_l.append(tic)
                self.filtered_industries.add(tic_industry)
                self.filtered_sectors.add(tic_sector)

    def __get_dictionary(self):
        # fulfill dictionary wiht indicator values from every ticker
        # ticker: [tic1, tic2], 2022-1: [1, 3]

        self.dict = {key: [] for key in ['tickers', 'sector', 'industry', 'xs', 'ys']}
        for tic_name in self.filtered_tickers_l:
            self.dict['tickers'] = self.dict['tickers'] + [tic_name]
            self.dict['sector'] = self.dict['sector'] + [getattr(self.tic_branches, tic_name).sector]
            self.dict['industry'] = self.dict['industry'] + [getattr(self.tic_branches, tic_name).industry]

            if self.indicator in self.price_indicators:
                table_name = f'analysis_{tic_name}_{self.dd_chosen_price.period_type}_{self.dd_chosen_price.val_type}_{self.dd_chosen_price.summarization}'
            elif self.indicator in self.noprice_indicators:
                table_name = f'analysis_{tic_name}_no_price'
            else:
                print('ERROR. Ivalid name of indicator')
                print(table_name)
                print(self.price_indicators)
                print(self.noprice_indicators)
                print(self.indicator)
            sql_query = f'''SELECT * 
                            FROM [wsja2].[dbo].[{table_name}] 
                            WHERE Indicator = \'{self.indicator}\'
                            '''
            self.wsja2_cursor.execute(sql_query)

            vals = list(self.wsja2_cursor.fetchall()[0][2:])
            self.dict['ys'].append(vals)

            headers = [i[0] for i in self.wsja2_cursor.description]
            static_cols, date_cols = headers[:2], headers[2:]
            self.dict['xs'].append(date_cols)

    def get_xs(self):
        return self.dict['xs']

    def get_ys(self):
        return self.dict['ys']

    def get_sectors(self):
        return self.dict['sector']

    def get_industries(self):
        return self.dict['industry']

    def assign_colors(self, mylist):
        #colors = sns.color_palette("Paired")
        colors = u.colors()
        distinct_values = set(mylist)
        if len(colors) < len(distinct_values):
            print('ERROR! lista unikalnych wartosci jest dluzsza od listy kolorow')
        distinctval_color_dict = dict(zip(distinct_values, colors))
        res_colors = [distinctval_color_dict[x] for x in mylist]
        return res_colors


#class ChoiceForPrice:
#    def __init__(self):
#        self.period_type = 'quarter'
#        self.val_type = 'Close'
#        self.summarization = 'close'
#
#        self.table_name_type = self.__get_table_name_type()
#
#    def __get_table_name_type(self):
#        return f'{self.period_type}_{self.val_type}_{self.summarization}'
#
#    def update(self, period_type=None, val_type=None, summarization=None):
#        if period_type:
#            self.period_type = period_type
#        elif val_type:
#            self.val_type = val_type
#        elif summarization:
#            self.summarization = summarization

#u.pandas_df_display_options()
#wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
#wsja2_cursor, wsja2_conn, wsja2_engine = u.create_sql_connection('wsja2')
#tickers_list = ['DIS']
#dd_chosen_price = ChoiceForPrice()
#industry = ''
#sector = ''
#get_all_indicators(wsja2_cursor)

#sectors, industries = all_sectors_industries(tickers_list)
#
#psq = IndicatorAll(tickers_list, 'P/S', industry, sector, dd_chosen_price, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine)
#print(psq.get_xs())
#print(psq.get_ys())







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


