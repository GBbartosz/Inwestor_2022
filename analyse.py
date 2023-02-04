import pandas as pd

import indicators as ind
import utilities as u


def calculate_indicators(n, isy, isq, bay, baq, bly, blq, cfy, cfq, price, y, py, dic_ind):
    indicator_results = ind.create_indicator_results()
    # dic_ind.setdefault(y, )

    # only for calculation
    price = ind.price(price)
    nopat = ind.nopat(y, isy, isq)
    total_debt = ind.total_debt(y, bly, blq)

    # automatic
    roe = ind.roe(y, isy, bly, isq, blq)
    retained_earnings = ind.retained_earnings(y, bly, isy, blq, isq)
    stopa_wzrostu = ind.stopa_wzrostu(roe, retained_earnings)
    roa = ind.roa(y, isy, bay, isq, baq)
    roc = ind.roc(y, isy, bly, isq, blq)
    roce = ind.roce(y, isy, bay, bly, isq, baq, blq)
    roic = ind.roic(y, bay, bly, baq, blq, nopat, total_debt)

    # wacc = fWacc(y, py, isy, bly, price) if n != 0 else '-'
    # rrr
    gross_margin = ind.gross_margin(y, isy, isq)
    ebitda_margin = ind.ebitda_margin(y, isy, isq)
    ebit_margin = ind.ebit_margin(y, isy, isq)
    net_margin = ind.net_margin(y, isy, isq)

    d_e_ratio = ind.debt_to_equity_ratio(y, bly, blq)
    td_ta_ratio = ind.total_debt_to_total_assets_ratio(y, bay, bly, baq, blq)
    capex_revenue_ratio = ind.capex_to_revenue_ratio(n, y, py, isy, bay, isq, baq)

    altman_z_score = ind.altman_z_score(y, retained_earnings, isy, bay, bly, isq, baq, blq, price)
    beneish_m_score = ind.beneish_m_score(n, y, py, isy, bay, bly, cfy, isq, baq, blq, cfq)

    current_ratio = ind.current_ratio(y, bay, bly, baq, blq)

    p_s_ratio = ind.p_s_ratio(y, isy, isq, price)

    p_e_ratio = ind.p_e_ratio(y, isy, isq, price)
    eps = ind.eps(y, isy, isq)
    peg = ind.peg(y, eps, isy, isq, price)

    dscr = ind.debt_service_coverage_ratio(y, isy, isq)
    cash_ratio = ind.cash_ratio(y, bay, bly, baq, blq)
    operating_cf_debt_ratio = ind.operating_cash_flow_debt_ratio(y, cfy, bly, cfq, blq)

    # directly from income statement
    sales_revenue = ind.sales_revenue(y, isy, isq)
    gross_income = ind.gross_income(y, isy, isq)
    ebit = ind.ebit(y, isy, isq)
    ebitda = ind.ebitda(y, isy, isq)
    net_income = ind.net_income(y, isy, isq)
    research_development = ind.research_development(y, isy, isq)

    # ind_list = [price, roe, retained_earnings, stopa_wzrostu, roa, roc, roce, roic, wacc, gross_margin,
    #                 ebitda_margin, ebit_margin, net_margin, d_e_ratio, td_ta_ratio, capex_revenue_ratio,
    #                altman_z_score, beneish_m_score, current_ratio, p_s_ratio, p_e_ratio, eps, peg, dscr, cash_ratio,
    #               operating_cf_debt_ratio]
    indicator_results = ind.return_indicator_results()
    if type(y) is list:             # dla kwartalow - wybranie pierwszego jako nazwe kolumny
        y = y[0]
    if y in dic_ind.keys():
        dic_ind['Current'] = indicator_results
    else:
        dic_ind[y] = indicator_results
    # df = pd.DataFrame(dic_ind)
    return dic_ind


def calculate(ticker, isy, isq, bay, baq, bly, blq, cfy, cfq, price_y, price_q, all_years, all_quarters, update_global):
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

    # years
    ind.period_type = 'year'                                             #ustawienie okresu dla obliczen
    dic_ind_y = dic_ind.copy()
    for n in range(len(all_years)):
        y = all_years[n]
        py = all_years[n - 1] if n != 0 else None
        #dic_ind = calculate_indicators(n, isy, isq, bay, baq, bly, blq, cfy, cfq, price.m.close.val(y), y, py, dic_ind) # zmiana
        dic_ind_y = calculate_indicators(n, isy, isq, bay, baq, bly, blq, cfy, cfq, price_y.close.val(y), y, py, dic_ind_y)
        df_y = pd.DataFrame(dic_ind_y)
        if n == len(all_years) - 1:
            dic_ind_y = calculate_indicators(n, isy, isq, bay, baq, bly, blq, cfy, cfq, price_y.current, y, py, dic_ind_y)
            df_y = pd.DataFrame(dic_ind_y)
    if update_global is False:
        df_y['Ticker'] = ticker
        cols = list(df_y.columns)
        cols = [cols[-1]] + cols[:-1]
        df_y = df_y[cols]

    # quarters
    #print(all_quarters)
    ind.period_type = 'quarter'                                           #ustawienie okresu dla obliczen
    dic_ind_q = dic_ind
    print('dicind')
    print(dic_ind_q)
    for n in range(len(all_quarters)):
        print('price')
        print(price_q.close.val(all_quarters[n]))
        if n >= 3:
            qs_l = [all_quarters[n], all_quarters[n-1], all_quarters[n-2], all_quarters[n-3]]
            qs_l_py = [all_quarters[n-4], all_quarters[n-5], all_quarters[n-6], all_quarters[n-7]] if n >= 7 else None
            dic_ind_q = calculate_indicators(n, isy, isq, bay, baq, bly, blq, cfy, cfq, price_q.close.val(qs_l[0]), qs_l, qs_l_py, dic_ind_q)
            df_q = pd.DataFrame(dic_ind_q)
            if n == len(all_years) - 1:
                dic_ind_q = calculate_indicators(n, isy, isq, bay, baq, bly, blq, cfy, cfq, price_q.current, qs_l, qs_l_py, dic_ind_q)
                df_q = pd.DataFrame(dic_ind_q)
            print(dic_ind_q)
    if update_global is False:          # dodanie tickera i ustawienie na poczatku
        df_q['Ticker'] = ticker
        cols = list(df_q.columns)
        cols = [cols[-1]] + cols[:-1]
        df_q = df_q[cols]

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

    return df_y, df_q, df2
