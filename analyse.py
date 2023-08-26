import pandas as pd
import utilities as u
import warnings

from financialstatementsclass import FinancialStatements
from indicators import IndicatorCalculation
from priceclass import Price


def create_or_replace_indicators_sql_table(ticker, table_type_names, dfs):
    cursor, conn, engine = u.create_sql_connection('wsja2')
    analysed_tables = [f'analysis_{ticker}_{t}' for t in table_type_names]
    for analysed_table, df in zip(analysed_tables, dfs):
        if df.empty is False:
            u.pandas_df_display_options()
            #print(analysed_table)
            #print(df)
            df.to_sql(analysed_table, con=engine, if_exists='replace', index=False)


def analyse(ticker_name):

    def get_common_periods_real():
        # handling case when financial statements differ in columns
        periods_real_isq = finsts.isq.all_periods_real
        periods_real_baq = finsts.baq.all_periods_real
        periods_real_blq = finsts.blq.all_periods_real
        periods_real_cfq = finsts.cfq.all_periods_real
        periods_real = [x for x in periods_real_isq if
                        x in periods_real_baq and x in periods_real_blq and x in periods_real_cfq]
        return periods_real

    def update_currency(ticker, wsj_cursor, wsj_conn):
        # adds currency to profile table based on currency in column header in income_statement_q
        profile_df = pd.read_sql(f'SELECT * FROM wsj.dbo.{ticker}_profile', wsj_conn)
        currency = None
        if 'Currency' not in profile_df.columns:
            main_caption = pd.read_sql(f'SELECT * FROM wsj.dbo.{ticker}_income_statement_q', wsj_conn).columns[1]
            if ' USD ' in main_caption:
                currency = 'USD'
            elif ' EUR ' in main_caption:
                currency = 'EUR'
            elif ' HKD ' in main_caption:
                currency = 'HKD'
            else:
                print(f'{ticker} has unprecedented value! (tickerclass - 39)')
            if currency is not None:
                wsj_cursor.execute(f'ALTER TABLE {ticker}_profile ADD Currency varchar(3)')
                wsj_cursor.execute(f'UPDATE {ticker}_profile SET Currency = \'{currency}\'')

    finsts = FinancialStatements(ticker_name)
    update_currency(finsts.ticker_name, finsts.wsj_cursor, finsts.wsj_conn)
    print(finsts.ticker_name)
    print(finsts.isq.reporting_frequency)
    valid_quarters = finsts.isq.all_periods[3:]
    periods_real = get_common_periods_real()
    price = Price(ticker_name, periods_real)

    dfs = []
    table_type_names = []

    indc = IndicatorCalculation(finsts,
                                None,
                                None,
                                None,
                                None,
                                periods_real)
    df, table_type_name = indc.update_indicators_without_price()
    dfs.append(df)
    table_type_names.append(table_type_name)

    for subperiod in price.subperiods:
        for price_val_type in price.val_types:
            for price_summarization in price.summarizations:
                indc = IndicatorCalculation(finsts,
                                            price,
                                            subperiod,
                                            price_val_type,
                                            price_summarization,
                                            periods_real)
                df, table_type_name = indc.update_indicators_with_price()
                dfs.append(df)
                table_type_names.append(table_type_name)

    create_or_replace_indicators_sql_table(ticker_name, table_type_names, dfs)

warnings.filterwarnings('ignore')
#analyse('DIS')
analyse('META')
#analyse('AMZN')
#analyse('NFLX')
#analyse('GOOGL')
#analyse('BABA')
#analyse('ANET')
#analyse('NKE')


#drop tabeli price rozwiazuje prol=blem
# czyli index nie uploaduje sie przy dokladaniu wierszzy, a jesli nie to w update all jest jakis blad
