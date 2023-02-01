def create_indicator_results():
    global indicator_results
    indicator_results = []
    return indicator_results


period_type = None
indicator_results = create_indicator_results()

def is_null(func):
    def inner(*args):
        global indicator_results
        try:
            res = func(*args)
            if res != '-':
                res = float("{:.2f}".format(res))
            else:
                res = 0
        except ZeroDivisionError:
            res = 0
        #indicator_name = func.__name__.upper()
        #temp_dic = {indicator_name: res}
        #dic_ind.update(temp_dic)
        indicator_results.append(res)
        return res
    return inner


def return_indicator_results():
    global indicator_results
    return indicator_results


def sum_quarters(period_l, indicator_class):
    total = 0
    for period in period_l:
        total += indicator_class.val(period)
    return total


@is_null
def price(price):
    return price


@is_null
def nopat(y, isy):
    if period_type == 'year':
        ebit = isy.EBIT.val(y)
        income_tax = isy.Income_Tax.val(y)
    if period_type == 'quarter':
        ebit = sum_quarters(y, isy.EBIT)
        income_tax = sum_quarters(y, isy.Income_Tax)
    nopat = ebit - income_tax
    return nopat


@is_null
def total_debt(y, bly):
    total_debt = bly.Short_Term_Debt.val(y) + bly.Long_Term_Debt.val(y)
    return total_debt


@is_null
def roe(y, isy, bly):
    # stopa zwrotu z kapitalu wlasnego
    # w %
    # efektywnosc w generownaiu zyskow
    # okreslenie czy wskaznik jest dobry czy zly zalezy od spolek porownywalnych
    # porwnywanie do sredniej dla spolek z sektora
    # poziom 15% czyli średnia S&P500 jest akceptowalny
    # ujemny lub bardzo wysoki ROE (ujemny dochod i kapital wlasny) to sygnal ostrzegawczy
    # maloprawdopodobne ale ujemny roe moze wynikac z progrmau wykupu akcji wlasnych oraz doskonalego zarzadzania
    roe = isy.Net_Income.val(y) / bly.Total_Equity.val(y)
    return roe


@is_null
def retained_earnings(y, bly, isy):
    # zysk zatrzymany(wskaźnik zwrotu z inwestycji)
    # %
    retained_earnings = 1 - (bly.Dividends_Payable.val(y) / isy.Net_Income.val(y))
    return retained_earnings


@is_null
def stopa_wzrostu(roe, retained_earnings):
    # %
    stopa_wzrostu = roe * retained_earnings
    return stopa_wzrostu


@is_null
def roa(y, isy, bay):
    # rentowność firmy w stosunku do jej całkowitych aktywów
    # efektywność wykorzystania aktywów
    # im większe ROE w stosunku do ROA tym większą dźwignię finansową stosuje firma
    # ograniczone zastosowanie bo różne wynik idla różnych branż (sprzyja bankom)
    # ogólnie powyzej 5% - dobrze, powyżej 20% - doskonale (jednak zawsze powinno być porównywane)
    roa = isy.Net_Income.val(y) / bay.Total_Assets.val(y)
    return roa


@is_null
def roc(y, isy, bly):
    # zwrot z kapitału
    roc = isy.EBIT.val(y) / bly.Total_Equity.val(y)
    return roc


@is_null
def roce(y, isy, bay, bly):
    # return on capital employed
    # szczególnie przydatny w oceniuniu spółek w sektorach kapitałochłonnych - media, telekomunikacja, użyteczność publiczna
    # ważny jest trend
    roce = isy.EBIT.val(y) / (bay.Total_Assets.val(y) - bly.Total_Current_Liabilities.val(y))
    return roce


@is_null
def roic(y, bay, bly, nopat, total_debt):
    # zwrot z zainwestowanego kapitału
    roic = (nopat - bly.Dividends_Payable.val(y)) / (
            total_debt + bay.Leases.val(y) - bay.Cash_Only.val(y) + bly.Total_Equity.val(y))
    return roic


@is_null
def wacc(y, py, isy, bly, price):
    tax_rate = isy.Income_Tax.val(y) / isy.Pretax_Income.val(y)
    dividend_per_share = bly.Dividends_Payable.val(y) / isy.Diluted_Shares_Outstanding.val(y)
    dividend_per_share_py = bly.Dividends_Payable.val(py) / isy.Diluted_Shares_Outstanding.val(py)
    cost_of_equity = dividend_per_share / price.close.val(y) + (dividend_per_share + dividend_per_share_py) / 2
    cost_of_debt = isy.Interest_Expense.val(y) / (
            bly.Long_Term_Debt.val(y) + bly.Current_Portion_of_Long_Term_Debt.val(y) + bly.Long_Term_Debt.val(
        py) + bly.Current_Portion_of_Long_Term_Debt.val(py))
    market_value_of_equity = isy.Diluted_Shares_Outstanding.val(y) * price.close.val(y)
    market_value_of_debt = isy.Diluted_Shares_Outstanding.val(y) * cost_of_debt
    total_market_value_of_equity_and_debt = market_value_of_equity + market_value_of_debt
    wacc = (
                   market_value_of_equity / total_market_value_of_equity_and_debt * cost_of_equity) + market_value_of_debt / total_market_value_of_equity_and_debt * cost_of_debt * (
                   1 - tax_rate)
    wacc = "{:.4f}".format(wacc)
    print('price: ' + str(price.close.val(y)))
    print('Diluted_Shares_Outstanding: ' + str(isy.Diluted_Shares_Outstanding.val(py)))
    print('Interest_Expense: ' + str(isy.Interest_Expense.val(y)))
    print('tax rate: ' + str(tax_rate))
    print('dividend_per_share: ' + str(dividend_per_share))
    print('dividend_per_share_py: ' + str(dividend_per_share_py))
    print('cost_of_equity: ' + str(cost_of_equity))
    print('cost_of_debt: ' + str(cost_of_debt))
    print('market_value_of_equity: ' + str(market_value_of_equity))
    print('market_value_of_debt: ' + str(market_value_of_debt))
    print('total_market_value_of_equity_and_debt: ' + str(total_market_value_of_equity_and_debt))
    print('wacc: ' + str(wacc))
    print()
    return wacc


@is_null
def gross_margin(y, isy):
    # przychód po odjęciu tylko kosztów bezpośrednio związanych z wytworzeniem dóbr
    gross_margin = isy.Gross_Income.val(y) / isy.Sales_Revenue.val(y)
    return gross_margin


@is_null
def ebitda_margin(y, isy):
    # przychód brutto po odjęciu dodatkowych kosztów administacyjnych, wydatków na badania
    # eliminuje wpływ polityki finansowej i księgowej
    ebitda_margin = isy.EBITDA.val(y) / isy.Sales_Revenue.val(y)
    return ebitda_margin


@is_null
def ebit_margin(y, isy):
    # marża operacyjna
    # rentowność sprzedaży
    ebit_margin = isy.EBIT.val(y) / isy.Sales_Revenue.val(y)
    return ebit_margin


@is_null
def net_margin(y, isy):
    # marża netto
    net_margin = isy.Net_Income.val(y) / isy.Sales_Revenue.val(y)
    return net_margin


@is_null
def debt_to_equity_ratio(y, bly):
    # poniżej 1 - dobry
    # powyżej 2,5 ryzykowny
    # bardzo niski poziom wskaźnika jest negatywnym sygnałem - firma nie wykorzystuje dźwigni długu do ekspansji
    # bankowość ma znacznie wyższy poziom wskaźnika
    # dopuszczalny wyższy w sektorach o powolnym i stabilnym wzroscie - np. użyteczność publiczna
    # ujemny wskaźnik oznacza ujemny equity (więcej zobowiązań od aktywów) - zagrożenie upadłością
    d_e_ratio = bly.Total_Liabilities.val(y) / bly.Total_Shareholders_Equity.val(y)
    return d_e_ratio


@is_null
def total_debt_to_total_assets_ratio(y, bay, bly):
    # miara aktywów firmy finansowanych z zadłużenia
    # pokazuje jak firma rozwijała się i nabywała swoje aktywa w funkcji czasu
    # mówi czy firma posiada wystarczające fundusze aby sprostać swoim bieżącym zobowiązaniom
    # ponad 1 - firma ma więcej zobowiązań niż aktywów, ryzyko niewypłacalności w przypadku wzrostu stóp procentowych
    # poniżej 0,5 - większa częśc aktywów firmy jest finansowana kapitałem własnym
    # nie dostarcza żadnych wskazówek odnośnie jakości aktywów
    td_ta = bly.Total_Liabilities.val(y) / bay.Total_Assets.val(y)
    return td_ta


@is_null
def capex_to_revenue_ratio(n, y, py, isy, bay):
    # stosunek inwestycji w kapitał stały do jej całkowitej sprzedaży
    # wydatek jest rozkładany na cały okres użytkowania składnika aktywów
    # najbardziej kapitałochłonne branże = najwyższe skaźniki -> spółki surowcowe, telekomunikacja, przemysł wytwórczy, użytecnzość publiczna
    if n != 0:
        capex = bay.Property_Plant_Equipment_Gross.val(y) - bay.Property_Plant_Equipment_Gross.val(py) + (
                bay.Accumulated_Depreciation.val(y) - bay.Accumulated_Depreciation.val(py))
        capex_revenue_ratio = capex / isy.Sales_Revenue.val(y)
    else:
        capex_revenue_ratio = '-'
    return capex_revenue_ratio


@is_null
def altman_z_score(y, retained_earnings, isy, bay, bly, price):
    # test wytrzymałości kredytowej
    # powyżej 3 - bezpiecznie
    # poniżej 1.8 - zagrożenie bankructwem
    X = (bay.Total_Current_Assets.val(y) - bly.Total_Current_Liabilities.val(y)) / bay.Total_Assets.val(y)
    Y = isy.Net_Income.val(y) * retained_earnings / bay.Total_Assets.val(y)
    V = isy.EBIT.val(y) / bay.Total_Assets.val(y)
    B = price * isy.Diluted_Shares_Outstanding.val(y) / bly.Total_Liabilities.val(y)
    Q = isy.Sales_Revenue.val(y) / bay.Total_Assets.val(y)
    altman_z_score = 1.2 * X + 1.4 * Y + 3.3 * V + 0.6 * B + 1 * Q
    return altman_z_score


@is_null
def beneish_m_score(n, y, py, isy, bay, bly, cfy):
    # ponizej -1.78 - przedsiębiorstwo nie jest manipulatorem
    # powyżej -1.78 - jest manipulatorem
    if n != 0:
        DSRI = (bay.Accounts_Receivables_Net.val(y) / isy.Sales_Revenue.val(y)) / (
                bay.Accounts_Receivables_Net.val(py) / isy.Sales_Revenue.val(py))
        GMI = ((isy.Sales_Revenue.val(py) - isy.COGS_excluding_D_A.val(py)) / isy.Sales_Revenue.val(py)) / (
                (isy.Sales_Revenue.val(y) - isy.COGS_excluding_D_A.val(y)) / isy.Sales_Revenue.val(y))
        AQI = (1 - (bay.Total_Current_Assets.val(y) + bay.Net_Property_Plant_Equipment.val(y)) / bay.Total_Assets.val(
            y)) / (1 - (
                bay.Total_Current_Assets.val(py) + bay.Net_Property_Plant_Equipment.val(py)) / bay.Total_Assets.val(
            py))
        SGI = isy.Sales_Revenue.val(y) / isy.Sales_Revenue.val(py)
        DEPI = (isy.Depreciation.val(py) / (bay.Net_Property_Plant_Equipment.val(py) + isy.Depreciation.val(py))) / (
                isy.Depreciation.val(y) / (bay.Net_Property_Plant_Equipment.val(y) + isy.Depreciation.val(y)))
        SGAI = (isy.SG_A_Expense.val(y) / isy.Sales_Revenue.val(y)) / (
                isy.SG_A_Expense.val(py) / isy.Sales_Revenue.val(py))
        LVGI = ((bly.Total_Current_Liabilities.val(y) + bly.Long_Term_Debt.val(y)) / bay.Total_Assets.val(y)) / (
                (bly.Total_Current_Liabilities.val(py) + bly.Long_Term_Debt.val(py)) / bay.Total_Assets.val(py))
        TATA = (isy.Net_Income.val(y) - cfy.Net_Operating_Cash_Flow.val(y)) / bay.Total_Assets.val(y)
        beneish_m_score = -4.84 + 0.92 * DSRI + 0.528 * GMI + 0.404 * AQI + 0.892 * SGI + 0.115 * DEPI - 0.172 * SGAI + 4.679 * TATA - 0.327 * LVGI
    else:
        beneish_m_score = '-'
    return beneish_m_score


@is_null
def sloan_ratio(y, py, isy, bay, cfy):
    # zla formula obliczeniowa
    cfi = bay.Net_Property_Plant_Equipment.val(y) - bay.Net_Property_Plant_Equipment.val(py)
    sloan_ratio = (isy.Net_Income.val(y) - cfy.Net_Operating_Cash_Flow.val(y) - cfi) / bay.Total_Assets.val(y)
    return sloan_ratio


@is_null
def current_ratio(y, bay, bly):
    current_ratio = bay.Total_Current_Assets.val(y) / bly.Total_Current_Liabilities.val(y)
    return current_ratio


@is_null
def p_s_ratio(y, isy, price):
    # przydatny w wycenie akcji wzrostowych, które nie przyniosły jeszcze zysku lub doświadczyły tymczasowego niepowodzenia
    # przychód jest tylko wtedy wartościowy gdy w pewnym momencie można go przełożyć na zyski
    # różne branże mają różne marże więc wysokość przychodów moze być myląca
    # nie uwzględnia zysku a więc problemu spłaty długu
    p_s = price / (isy.Sales_Revenue.val(y) / isy.Diluted_Shares_Outstanding.val(y))
    return p_s


@is_null
def p_e_ratio(y, isy, price):
    p_e = price * isy.Diluted_Shares_Outstanding.val(y) / isy.Net_Income.val(y)
    return p_e


@is_null
def eps(y, isy):
    eps = isy.Net_Income.val(y) / isy.Diluted_Shares_Outstanding.val(y)
    return eps


@is_null
def peg(y, eps, isy, price):
    # Peter Lynch
    # liczony z bieżącego roku jak i piecioletniej oczekiwanej stopie wzrostu
    # dodanie oczekiwanego wzrostu spółki pomaga skorygować wynik w przypadku spółek które mogą miec wysoką stopę wzrostu i wysoki wskaźnik P/E
    # ponizej 1 na pewno dobrze - Lynch
    peg = (price / eps) / isy.EPS_Basic_Growth.val(y) / 100
    return peg


@is_null
def debt_service_coverage_ratio(y, isy):
    dscr = isy.EBIT.val(y) / isy.Interest_Expense.val(y)
    return dscr


@is_null
def cash_ratio(y, bay, bly):
    cash_ratio = bay.Cash_Short_Term_Investments.val(y) / bly.Total_Current_Liabilities.val(y)
    return cash_ratio


@is_null
def operating_cash_flow_debt_ratio(y, cfy, bly):
    cf_debt_ratio = cfy.Net_Operating_Cash_Flow.val(y) / (bly.Short_Term_Debt.val(y) + bly.Long_Term_Debt.val(y))
    return cf_debt_ratio


# directly from income statement
@is_null
def sales_revenue(y, isy):
    sales_revenue = isy.Sales_Revenue.val(y)
    return sales_revenue


@is_null
def gross_income(y, isy):
    gross_income = isy.Gross_Income.val(y)
    return gross_income


@is_null
def ebit(y, isy):
    ebit = isy.EBIT.val(y)
    return ebit


@is_null
def ebitda(y, isy):
    ebitda = isy.EBITDA.val(y)
    return ebitda


@is_null
def net_income(y, isy):
    net_income = isy.Net_Income.val(y)
    return net_income


@is_null
def research_development(y, isy):
    research_development = isy.Research_Development.val(y)
    return research_development


# advanced
def beta(df_indeks_price_5y, df_ticker_price_5y):
    indeks_avg = df_indeks_price_5y['Close'].mean()
    ticker_avg = df_ticker_price_5y['Close'].mean()
    number_of_rows = len(df_indeks_price_5y)
    res = 0
    for r in df_indeks_price_5y.index:
        res += (df_ticker_price_5y['Close'].iloc[r] - ticker_avg) * (df_indeks_price_5y['Close'].iloc[r] - indeks_avg)
    covariance = res / (number_of_rows - 1)
    indeks_variance = df_indeks_price_5y['Close'].var()
    beta = covariance / indeks_variance
    return beta