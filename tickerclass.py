import pandas as pd
import utilities as u


def dictionary_values_to_list(mydict):
    return list(mydict.values())


def dictionary_keys_to_list(mydict):
    return list(mydict.keys())


class Ticker:
    def __init__(self, ticker, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine, dd_chosen_price):
        self.name = ticker
        self.price_df = None
        self.price_dates = None
        self.price_indicators_names_l = []
        self.noprice_df = None
        self.noprice_dates = None
        self.noprice_indicators_names_l = []
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
        self.wsja2_cursor, self.wsja2_conn, self.wsja2_engine = wsja2_cursor, wsja2_conn, wsja2_engine
        profile_df = pd.read_sql(f'SELECT * FROM wsj.dbo.{ticker}_profile', self.wsj_conn)
        self.fs_currency = profile_df['FS_Currency'][0]
        self.p_currency = profile_df['Price_Currency'][0]
        sector_industry = profile_df.iloc[0, :].tolist()
        self.sector = sector_industry[0]
        self.industry = sector_industry[1]
        self.analysis_price_table_name = f'[wsja2].[dbo].[analysis_{self.name}_{dd_chosen_price.period_type}_{dd_chosen_price.val_type}_{dd_chosen_price.summarization}]'
        self.analysis_noprice_table_name = f'[wsja2].[dbo].[analysis_{self.name}_no_price]'

    def create_indicators(self):

        def create_indicators2(df):
            indicators = df['Indicator'].tolist()
            self.indicators_names_l = self.price_indicators_names_l + self.noprice_indicators_names_l
            for i in indicators:
                setattr(self, i, ChosenIndicator(df, i))

        class ChosenIndicator:
            def __init__(self, df, i):
                mdict = df[df['Indicator'] == i].iloc[0:, 2:].to_dict('records')[0]
                self.name = i
                setattr(self, 'values', dictionary_values_to_list(mdict))
                setattr(self, 'dates', dictionary_keys_to_list(mdict))

        self.price_indicators_names_l = self.price_df['Indicator'].tolist()
        create_indicators2(self.price_df)
        self.noprice_indicators_names_l = self.noprice_df['Indicator'].tolist()
        create_indicators2(self.noprice_df)

    def set_analysis_df(self):
        sql_query = f'SELECT * FROM {self.analysis_price_table_name}'
        df = pd.read_sql(sql_query, self.wsja2_conn)
        #df.columns = u.get_transform_dates_to_quarters(df.columns)
        #df.columns = u.transform_dataframe_columns_with_month_names_to_numbers(df.columns)
        self.price_df = df
        self.price_dates = df.columns[2:]

        sql_query = f'SELECT * FROM {self.analysis_noprice_table_name}'
        df = pd.read_sql(sql_query, self.wsja2_conn)
        #df.columns = u.get_transform_dates_to_quarters(df.columns)
        #df.columns = u.transform_dataframe_columns_with_month_names_to_numbers(df.columns)
        self.noprice_df = df
        self.noprice_dates = df.columns[2:]

    def set_is_df_y(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_income_statement_y'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.is_df_y = df

    def set_is_df_q(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_income_statement_q'
        df = pd.read_sql(sql_query, self.wsj_conn)
        #df.columns = u.get_transform_dates_to_quarters(df.columns)
        df.columns = u.transform_dataframe_columns_with_month_names_to_numbers(df.columns)
        self.is_df_q = df

    def set_ba_df_y(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_balance_assets_y'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.ba_df_y = df

    def set_ba_df_q(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_balance_assets_q'
        df = pd.read_sql(sql_query, self.wsj_conn)
        #df.columns = u.get_transform_dates_to_quarters(df.columns)
        df.columns = u.transform_dataframe_columns_with_month_names_to_numbers(df.columns)
        self.ba_df_q = df

    def set_bl_df_y(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_balance_liabilities_y'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.bl_df_y = df

    def set_bl_df_q(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_balance_liabilities_q'
        df = pd.read_sql(sql_query, self.wsj_conn)
        #df.columns = u.get_transform_dates_to_quarters(df.columns)
        df.columns = u.transform_dataframe_columns_with_month_names_to_numbers(df.columns)
        self.bl_df_q = df

    def set_cf_df_y(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_cash_flow_y'
        df = pd.read_sql(sql_query, self.wsj_conn)
        self.cf_df_y = df

    def set_cf_df_q(self):
        sql_query = f'SELECT * FROM wsj.dbo.{self.name}_cash_flow_q'
        df = pd.read_sql(sql_query, self.wsj_conn)
        #df.columns = u.get_transform_dates_to_quarters(df.columns)
        df.columns = u.transform_dataframe_columns_with_month_names_to_numbers(df.columns)
        self.cf_df_q = df




# funkcja techniczna do usuniecia
#class ChoiceForPrice:
#    def __init__(self):
#        self.period_type = 'day'
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
#
#
#wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
#wsja2_cursor, wsja2_conn, wsja2_engine = u.create_sql_connection('wsja2')
#dd_chosen_price = ChoiceForPrice()
#tic = Ticker('DIS', wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine, dd_chosen_price)
#tic.set_analysis_df()
#tic.create_indicators()
#
#print(tic.indicators_names_l)
#print(tic.Revenue.values)
#print(tic.Revenue.dates)
#print(getattr(tic, 'P/S').values)
#print(getattr(tic, 'P/S').dates)




