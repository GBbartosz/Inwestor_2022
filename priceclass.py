import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import utilities as u


class Price:
    def __init__(self, ticker_name, period_dates_l, period_quarters_l):

        def get_end_date(period_dates_l, loop_n, last_loop):
            if last_loop:
                end_date = self.max_date
            else:
                end_date = period_dates_l[loop_n + 1]
            return end_date

        self.subperiods = ['day', 'week', 'month', 'quarter']
        self.val_types = ['High', 'Low', 'Open', 'Close']
        self.summarizations = ['max', 'min', 'open', 'close']
        self.ticker_name = ticker_name
        self.wsj_cursor, self.wsj_conn, self.wsj_engine = u.create_sql_connection('wsj')
        self.table_name = self.ticker_name + '_price_history_1d'
        self.price_df = self.__select_all_to_df()
        self.max_date = self.price_df['Date'].max()

        last_loop = False
        period_df_dict = {}
        loop_n = 0
        while loop_n < len(period_dates_l):
            period_date = period_dates_l[loop_n]
            start_date = period_date
            if len(period_quarters_l) - loop_n == 1:
                last_loop = True
            end_date = get_end_date(period_dates_l, loop_n, last_loop)
            price_period_df = self.price_df[(self.price_df['Date'] > start_date) & (self.price_df['Date'] <= end_date)]
            period_df_dict[period_date] = price_period_df
            loop_n += 1
        self.period_df_dict = period_df_dict

    def __select_all_to_df(self):
        sql_select_all = 'SELECT * FROM [wsj].[dbo].[{}]'.format(self.table_name)
        df = pd.read_sql(sql_select_all, con=self.wsj_conn)
        return df

    def val(self, period_date, subperiod, val_type, summarization):
        # period_type: day, week, month, quarter
        # val_type: High, Low, Open, Close - columns
        # summarization: max, min, open, close

        def get_val_type(df, summarization):
            vals = df.iloc[:, 1].tolist()
            if summarization == 'open':
                val = vals[-1]
            elif summarization == 'close':
                val = vals[0]
            elif summarization == 'max':
                val = max(vals)
            elif summarization == 'min':
                val = min(vals)
            return val

        def get_week(date_str):
            week = dt.datetime.strptime(date_str, '%Y-%m-%d').isocalendar().week
            if week < 10:
                week = '0' + str(week)
            else:
                week = str(week)
            return week

        df = self.period_df_dict[period_date][['Date', val_type]]

        if subperiod == 'quarter':
            res = {period_date: get_val_type(df, summarization)}
        elif subperiod == 'month':
            unique_year_months = list(set([x[:7] for x in df['Date'].tolist()]))
            res = {}
            for year_month in unique_year_months:
                month_df = df[df['Date'].apply(lambda x: x[:7]) == year_month]
                res[year_month] = get_val_type(month_df, summarization)
        elif subperiod == 'week':
            df['Date'] = df['Date'].apply(lambda x: x[:4] + '-' + get_week(x))
            unique_year_weeks = list(set(df['Date'].tolist()))
            res = {}
            for year_week in unique_year_weeks:
                week_df = df[df['Date'] == year_week]
                res[year_week] = get_val_type(week_df, summarization)
        elif subperiod == 'day':
            res = {df.iloc[i, 0]: df.iloc[i, 1] for i in range(len(df.index))}
        reskeys = list(res.keys())
        reskeys.sort()
        res = {i: res[i] for i in reskeys}
        return res

    def current_price_download(ticker):
        MW_overview = 'https://www.marketwatch.com/investing/stock/{0}'.format(ticker)
        try:
            price = pd.read_html(MW_overview)[1].loc[0, 'Close'][1:]
        except:
            price = pd.read_html(MW_overview)[1].loc[0, 'Previous Close'][1:]
        price = float(u.get_rid_of_special_characters(price)) / 100
        return price


#ticker_name = 'dis'
#period_dates_l = ['2022-03-31', '2022-06-30']
#period_quarters_l = ['2022-1', '2022-2']
#price = Price(ticker_name, period_dates_l, period_quarters_l)
#
#for pd, pq in zip(period_dates_l, period_quarters_l):
#    print(pd)
#    val = price.val(period_date=pd, subperiod='week', val_type='Close', summarization='close')
#    print(val)
