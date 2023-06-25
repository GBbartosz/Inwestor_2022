import utilities as u

from financialstatementsclass import FinancialStatements

def create_or_replace_indicators_sql_table(ticker, dfs):
    cursor, wsj_conn, engine = u.create_sql_connection('wsja')
    analysed_tables = ['year', 'quarter']
    analysed_tables = [f'analysis_{ticker}_{p}' for p in analysed_tables]
    for analysed_table, df in zip(analysed_tables, dfs):
        if df.empty is False:
            df.to_sql(analysed_table, con=engine, if_exists='replace', index=False)

def analyse(ticker_name):
    finsts = FinancialStatements(ticker_name)

    for quarter in



    dfs = [df_y, df_q]
    create_or_replace_indicators_sql_table(ticker_name, dfs)
