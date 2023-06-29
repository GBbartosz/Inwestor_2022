import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import utilities as u


class Price():
    # def __init__(self, tic, years_list, fiscal_year_end, price_df_m, price_df_d):
    def __init__(self, ticker_name, period_dates_l, period_quarters_l, price_df):
        self.max = None
        self.min = None
        self.open = None
        self.close = None
        self.current = None
        prop = ['max', 'min', 'open', 'close', 'current']
        loop_n = 0
        while loop_n < len(period_quarters_l):
            period_quarter = period_quarters_l[loop_n]
            period_date = period_dates_l[loop_n]
            if period_quarter == '2021-1':
                start_date = '2021-01-01'
            elif loop_n == 0:
                start_date = dt.datetime.strptime(period_date, 'yyyy-MM-dd') - relativedelta(months=2)
            else:
                start_date = period_date[loop_n - 1]
            end_date = period_date
            price_period_df = price_df.loc[start_date:end_date, :]

            # od tad
            for p in prop:
                if p == 'current':
                    val = self.current_price_download(ticker_name)
                    self.current = float(val)
                else:
                    setattr(self, p, Price_year_quarter(p, periods_list, price_df, fiscal_year_end, frequency))


    def current_price_download(ticker):
        MW_overview = 'https://www.marketwatch.com/investing/stock/{0}'.format(ticker)
        try:
            price = pd.read_html(MW_overview)[1].loc[0, 'Close'][1:]
        except:
            price = pd.read_html(MW_overview)[1].loc[0, 'Previous Close'][1:]
        price = float(u.get_rid_of_special_characters(price)) / 100
        return price


class Price_year_quarter():
    #sciagnely sie zbyt krotkie tabele - powod bledu
    # trzeba usunac wiersze z NaN - nie przeszkadzaja ale nie potrzebne w miesiacach
    def __init__(self, p, periods_list, price_df, fiscal_year_end, frequency):
        if frequency == 'q':
            for quarter in periods_list:
                quarter_end = u.convert_date_with_month_name_to_number(quarter)
                quarter_end = dt.datetime.strptime(quarter_end, '%Y-%m-%d')

                quarter_start = quarter_end + pd.DateOffset(months=-2)
                quarter_start = str(quarter_start)[:8] + '01'
                quarter_start = dt.datetime.strptime(quarter_start, '%Y-%m-%d')

                quarter_end_ind = find_index_of_date(quarter_start, price_df)
                quarter_start_ind = find_index_of_date(quarter_end, price_df)

                df = price_df.iloc[quarter_start_ind:quarter_end_ind, :]

                if p == 'max':
                    val = df['High'].max()
                elif p == 'min':
                    val = df['Low'].min()
                elif p == 'open':
                    val = df.loc[:, 'Open'].iloc[-1]
                elif p == 'close':
                    val = df.loc[:, 'Close'].iloc[0]
                val = float(val)
                setattr(self, str(quarter), val)

        if frequency == 'y':
            for year in periods_list:
                initial_date = '{0}-{1}-{2}'.format(year, fiscal_year_end, '01')
                # if frequency == 'm':
                #     fiscal_y_start = dt.datetime.strptime(initial_date, '%Y-%m-%d') + pd.DateOffset(years=-1, months=1)
                #     fiscal_y_end = dt.datetime.strptime(initial_date, '%Y-%m-%d')

                fiscal_y_start = dt.datetime.strptime(initial_date, '%Y-%m-%d') + pd.DateOffset(years=-1, months=1)
                fiscal_y_end = dt.datetime.strptime(initial_date, '%Y-%m-%d') + pd.DateOffset(months=1, days=-1)
                start_fiscal_year_ind = find_index_of_date(fiscal_y_start, price_df)
                end_fiscal_year_ind = find_index_of_date(fiscal_y_end, price_df)
                df = price_df.iloc[end_fiscal_year_ind:start_fiscal_year_ind, :]
                if p == 'max':
                    val = df['High'].max()
                elif p == 'min':
                    val = df['Low'].min()
                elif p == 'open':
                    val = df.loc[:, 'Open'].iloc[-1]
                elif p == 'close':
                    val = df.loc[:, 'Close'].iloc[0]
                val = float(val)
                setattr(self, str(year), val)

    def val(self, period):
        return getattr(self, period)


def find_index_of_date(mydate, df):
    mydate = str(mydate.date())
    while mydate not in df['Date'].values:
        mydate = dt.datetime.strptime(mydate, '%Y-%m-%d')
        mydate = mydate + pd.DateOffset(days=1)
        mydate = str(mydate.date())
    mydate = df.index[(df['Date'] == mydate)][0]
    return mydate
