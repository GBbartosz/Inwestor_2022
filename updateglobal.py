import pandas as pd
import utilities as u
import analyse


def calculateglobal(tickers_list):
    cursor, wsj_conn, engine = u.create_sql_connection()
    # loop tickers
    industries = {}
    for ticker in tickers_list:
        print(ticker)
        if u.all_tables_available(ticker) is False:
            print('{0} nie został sprawdzony')
            continue
        # calculate indicators
        isy, isq, bay, baq, bly, blq, cfy, cfq, price, all_years, all_quarters = u.classes_from_sql(ticker)
        df = analyse.calculate(ticker, isy, isq, bay, baq, bly, blq, cfy, cfq, price, all_years, all_quarters, True)
        df_results = df[1:]
        # import data profile
        ticker_profile, ticker_price_history_1d, ticker_price_history_1mo = u.create_advanced_ticker_table_name(ticker)
        sql_select_all = 'SELECT * FROM {}'.format(ticker_profile)
        profile_df = pd.read_sql(sql_select_all, con=wsj_conn)
        # check if ticker is in industry
        industry = profile_df['Industry'].iloc[0]
        if industry in industries.keys():
            industries[industry][0] = industries[industry][0] + 1
            industries[industry][1] = industries[industry][1] + df_results
        else:
            industries[industry] = [1, df]
    df_label = df.iloc[:, 0]
    for k in industries.keys():
        companies_in_industry = industries[k][0]
        industry_df = industries[k][1]
        industry_df = industry_df.div(companies_in_industry)
        industry_df = df_label.join(industry_df)
        industry_sql_table = k + '_global'
        industry_df.to_sql(industry_sql_table, con=engine, if_exists='replace', index=False)

        #pierwsza kolumna df wyników przekształcić na index bo float + str
