import pandas as pd

import indicators as ind
import utilities as u



def calculate_indicators(n, isy, isq, bay, baq, bly, blq, cfy, cfq, price, y, py, dic_ind):
    indicator_results = ind.create_indicator_results()
    # dic_ind.setdefault(y, )

    # only for calculation
    price = ind.price(price)
    nopat = ind.nopat(y, isy)
    total_debt = ind.total_debt(y, bly)

    # automatic
    roe = ind.roe(y, isy, bly)
    retained_earnings = ind.retained_earnings(y, bly, isy)
    stopa_wzrostu = ind.stopa_wzrostu(roe, retained_earnings)
    roa = ind.roa(y, isy, bay)
    roc = ind.roc(y, isy, bly)
    roce = ind.roce(y, isy, bay, bly)
    roic = ind.roic(y, bay, bly, nopat, total_debt)

    # wacc = fWacc(y, py, isy, bly, price) if n != 0 else '-'
    # rrr
    gross_margin = ind.gross_margin(y, isy)
    ebitda_margin = ind.ebitda_margin(y, isy)
    ebit_margin = ind.ebit_margin(y, isy)
    net_margin = ind.net_margin(y, isy)

    d_e_ratio = ind.debt_to_equity_ratio(y, bly)
    td_ta_ratio = ind.total_debt_to_total_assets_ratio(y, bay, bly)
    capex_revenue_ratio = ind.capex_to_revenue_ratio(n, y, py, isy, bay)

    altman_z_score = ind.altman_z_score(y, retained_earnings, isy, bay, bly, price)
    beneish_m_score = ind.beneish_m_score(n, y, py, isy, bay, bly, cfy)

    current_ratio = ind.current_ratio(y, bay, bly)

    p_s_ratio = ind.p_s_ratio(y, isy, price)

    p_e_ratio = ind.p_e_ratio(y, isy, price)
    eps = ind.eps(y, isy)
    peg = ind.peg(y, eps, isy, price)

    dscr = ind.debt_service_coverage_ratio(y, isy)
    cash_ratio = ind.cash_ratio(y, bay, bly)
    operating_cf_debt_ratio = ind.operating_cash_flow_debt_ratio(y, cfy, bly)

    # directly from income statement
    sales_revenue = ind.sales_revenue(y, isy)
    gross_income = ind.gross_income(y, isy)
    ebit = ind.ebit(y, isy)
    ebitda = ind.ebitda(y, isy)
    net_income = ind.net_income(y, isy)
    research_development = ind.research_development(y, isy)



    # ind_list = [price, roe, retained_earnings, stopa_wzrostu, roa, roc, roce, roic, wacc, gross_margin,
    #                 ebitda_margin, ebit_margin, net_margin, d_e_ratio, td_ta_ratio, capex_revenue_ratio,
    #                altman_z_score, beneish_m_score, current_ratio, p_s_ratio, p_e_ratio, eps, peg, dscr, cash_ratio,
    #               operating_cf_debt_ratio]
    indicator_results = ind.return_indicator_results()
    if y in dic_ind.keys():
        dic_ind['Current'] = indicator_results
    else:
        dic_ind[y] = indicator_results
    # df = pd.DataFrame(dic_ind)
    return dic_ind


def calculate(ticker, isy, isq, bay, baq, bly, blq, cfy, cfq, price, all_years, all_quarters, update_global):
    current_year = all_years[-1]
    current_quarter = all_quarters[-1]
    dic_ind = {
        'Indicators': ['Price', 'NOPAT', 'Total debt', 'ROE', 'Retained_earning', 'Stopa_wzrostu',
                       'ROA', 'ROC', 'ROCE', 'ROIC',
                       'Gross Margin', 'EBITDA Margin', 'EBIT Margin', 'Net Margin',
                       'Debt to Equity Ratio', 'Total Debt to Total Assets Ratio', 'CAPEX to Revenue ration',
                       'Altman Z Score', 'Beneish M Score', 'Current Ratio',
                       'P/S', 'P/E', 'EPS', 'PEG',
                       'DSCR', 'Cash Ratio', 'Operating CF to Debt Ratio',
                       'Sales/Revenue', 'Gross income', 'EBIT', 'EBITDA', 'Net income',
                       'Development&Research']}

    for n in range(len(all_years)):
        y = all_years[n]
        py = all_years[n - 1] if n != 0 else None
        dic_ind = calculate_indicators(n, isy, isq, bay, baq, bly, blq, cfy, cfq, price.m.close.val(y), y, py, dic_ind)
        df = pd.DataFrame(dic_ind)
        if n == len(all_years) - 1:
            dic_ind = calculate_indicators(n, isy, isq, bay, baq, bly, blq, cfy, cfq, price.d.current, y, py, dic_ind)
            df = pd.DataFrame(dic_ind)
    if update_global is False:
        df['Ticker'] = ticker
        cols = list(df.columns)
        cols = [cols[-1]] + cols[:-1]
        df = df[cols]

    #jednorazowe
    # dane dla indeksu
    if len(all_years) >= 5:
        cursor, wsj_conn, engine = u.create_sql_connection()
        df_ticker_price_history = ticker + '_price_history_1d'
        sql_select_all = 'SELECT * FROM {}'.format(df_ticker_price_history)
        df_ticker_price_history = pd.read_sql(sql_select_all, con=wsj_conn)
        df_ticker_price_5y = u.price_history_5y(df_ticker_price_history)
        rows_number = len(df_ticker_price_5y.index)
        if rows_number == 1826:
            indekses = [('SP_500', '^GSPC'), ('NASDAQ', '^IXIC')]
            indicator_name_list = []
            res_list = []
            for indeks_name, indeks_ticker in indekses:
                indeks_sql_price_name = indeks_name + '_price_history_1d'
                sql_select_all = 'SELECT * FROM {}'.format(indeks_sql_price_name)
                df_indeks_price_history = pd.read_sql(sql_select_all, con=wsj_conn)
                df_indeks_price_5y = u.price_history_5y(df_indeks_price_history)

                beta = ind.beta(df_indeks_price_5y, df_ticker_price_5y)
                indicator_name_list.append('Beta {0}'.format(indeks_name))
                res_list.append(beta)
            wsj_conn.close()
            # inserting results to df2
            dic_ind2 = {'Indicators': indicator_name_list, 'Current': res_list}
            df2 = pd.DataFrame(dic_ind2)
            df2['Ticker'] = ticker
        else:
            df2 = pd.DataFrame()
    else:
        df2 = pd.DataFrame()

    return df, df2
