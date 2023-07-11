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
    finsts = FinancialStatements(ticker_name)
    valid_quarters = finsts.isq.all_periods[3:]
    periods_real = finsts.isq.all_periods_real
    price = Price(ticker_name, periods_real, valid_quarters)

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
#analyse('META')
#analyse('AMZN')
#analyse('NFLX')
#analyse('GOOGL')
analyse('APA')
