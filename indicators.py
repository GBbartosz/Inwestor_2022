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
def nopat(y, isy, isq):
    if period_type == 'year':
        ebit = isy.EBIT.val(y)
        income_tax = isy.Income_Tax.val(y)
    elif period_type == 'quarter':
        ebit = sum_quarters(y, isq.EBIT)
        income_tax = sum_quarters(y, isq.Income_Tax)
    print('ebit')
    print(ebit)
    print('income tax')
    print(income_tax)
    nopat = ebit - income_tax
    return nopat


@is_null
def total_debt(y, bly, blq):
    if period_type == 'year':
        short_term_debt = bly.Short_Term_Debt.val(y)
        long_term_debt = bly.Long_Term_Debt.val(y)
    elif period_type == 'quarter':
        short_term_debt = blq.Short_Term_Debt.val(y[0])
        long_term_debt = blq.Long_Term_Debt.val(y[0])
        # short_term_debt = sum_quarters(y, blq.Short_Term_Debt)
        # long_term_debt = sum_quarters(y, blq.Long_Term_Debt)
    total_debt = short_term_debt + long_term_debt
    return total_debt


@is_null
def roe(y, isy, bly, isq, blq):
    # stopa zwrotu z kapitalu wlasnego
    # w %
    # efektywnosc w generownaiu zyskow
    # okreslenie czy wskaznik jest dobry czy zly zalezy od spolek porownywalnych
    # porwnywanie do sredniej dla spolek z sektora
    # poziom 15% czyli średnia S&P500 jest akceptowalny
    # ujemny lub bardzo wysoki ROE (ujemny dochod i kapital wlasny) to sygnal ostrzegawczy
    # maloprawdopodobne ale ujemny roe moze wynikac z progrmau wykupu akcji wlasnych oraz doskonalego zarzadzania
    if period_type == 'year':
        net_income = isy.Net_Income.val(y)
        total_equity = bly.Total_Equity.val(y)
    elif period_type == 'quarter':
        net_income = sum_quarters(y, isq.Net_Income)
        total_equity = blq.Total_Equity.val(y[0])
        # net_income = sum_quarters(y, isq.Net_Income)
        # total_equity = sum_quarters(y, blq.Total_Equity)
    roe = net_income / total_equity
    return roe


@is_null
def retained_earnings(y, bly, isy, blq, isq):
    # zysk zatrzymany(wskaźnik zwrotu z inwestycji)
    # %
    if period_type == 'year':
        dividends_payable = bly.Dividends_Payable.val(y)
        net_income = isy.Net_Income.val(y)
    elif period_type == 'quarter':
        dividends_payable = blq.Dividends_Payable.val(y[0])
        # dividends_payable = sum_quarters(y, blq.Dividends_Payable)
        net_income = sum_quarters(y, isq.Net_Income)
    retained_earnings = 1 - (dividends_payable / net_income)
    return retained_earnings


@is_null
def stopa_wzrostu(roe, retained_earnings):
    # %
    stopa_wzrostu = roe * retained_earnings
    return stopa_wzrostu


@is_null
def roa(y, isy, bay, isq, baq):
    # rentowność firmy w stosunku do jej całkowitych aktywów
    # efektywność wykorzystania aktywów
    # im większe ROE w stosunku do ROA tym większą dźwignię finansową stosuje firma
    # ograniczone zastosowanie bo różne wynik idla różnych branż (sprzyja bankom)
    # ogólnie powyzej 5% - dobrze, powyżej 20% - doskonale (jednak zawsze powinno być porównywane)
    if period_type == 'year':
        net_income = isy.Net_Income.val(y)
        total_assets = bay.Total_Assets.val(y)
    elif period_type == 'quarter':
        net_income = sum_quarters(y, isq.Net_Income)
        # total_assets = sum_quarters(y, baq.Total_Assets)
        total_assets = baq.Total_Assets.val(y[0])
    roa = net_income / total_assets
    return roa


@is_null
def roc(y, isy, bly, isq, blq):
    # zwrot z kapitału
    if period_type == 'year':
        ebit = isy.EBIT.val(y)
        total_equity = bly.Total_Equity.val(y)
    elif period_type == 'quarter':
        ebit = sum_quarters(y, isq.EBIT)
        total_equity = blq.Total_Equity.val(y[0])
    roc = ebit / total_equity
    return roc


@is_null
def roce(y, isy, bay, bly, isq, baq, blq):
    # return on capital employed
    # szczególnie przydatny w oceniuniu spółek w sektorach kapitałochłonnych - media, telekomunikacja, użyteczność publiczna
    # ważny jest trend
    if period_type == 'year':
        ebit = isy.EBIT.val(y)
        total_assets = bay.Total_Assets.val(y)
        total_current_liabilities = bly.Total_Current_Liabilities.val(y)
    elif period_type == 'quarter':
        ebit = sum_quarters(y, isq.EBIT)
        total_assets = baq.Total_Assets.val(y[0])
        total_current_liabilities = blq.Total_Current_Liabilities.val(y[0])
    roce = ebit / (total_assets - total_current_liabilities)
    return roce


@is_null
def roic(y, bay, bly, baq, blq, nopat, total_debt):
    # zwrot z zainwestowanego kapitału
    if period_type == 'year':
        dividends_payable = bly.Dividends_Payable.val(y)
        leases = bay.Leases.val(y)
        cash_only = bay.Cash_Only.val(y)
        total_equity = bly.Total_Equity.val(y)
    elif period_type == 'quarter':
        dividends_payable = blq.Dividends_Payable.val(y[0])
        leases = baq.Leases.val(y[0])
        cash_only = baq.Cash_Only.val(y[0])
        total_equity = blq.Total_Equity.val(y[0])
    roic = (nopat - dividends_payable) / (total_debt - cash_only + total_equity)
    return roic


@is_null
def wacc(y, py, isy, bly, price):
    #if period_type == 'year':
    # =
    # =
    #if period_type == 'quarter':
    # = sum_quarters(y, )
    # = sum_quarters(y, )




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
def gross_margin(y, isy, isq):
    # przychód po odjęciu tylko kosztów bezpośrednio związanych z wytworzeniem dóbr
    if period_type == 'year':
        gross_income = isy.Gross_Income.val(y)
        sales_revenue = isy.Sales_Revenue.val(y)
    elif period_type == 'quarter':
        gross_income = sum_quarters(y, isq.Gross_Income)
        sales_revenue = sum_quarters(y, isq.Sales_Revenue)
    gross_margin = gross_income / sales_revenue
    return gross_margin


@is_null
def ebitda_margin(y, isy, isq):
    # przychód brutto po odjęciu dodatkowych kosztów administacyjnych, wydatków na badania
    # eliminuje wpływ polityki finansowej i księgowej
    if period_type == 'year':
        ebitda = isy.EBITDA.val(y)
        sales_revenue = isy.Sales_Revenue.val(y)
    elif period_type == 'quarter':
        ebitda = sum_quarters(y, isq.EBITDA)
        sales_revenue = sum_quarters(y, isq.Sales_Revenue)
    ebitda_margin = ebitda / sales_revenue
    return ebitda_margin


@is_null
def ebit_margin(y, isy, isq):
    # marża operacyjna
    # rentowność sprzedaży
    if period_type == 'year':
        ebit = isy.EBIT.val(y)
        sales_revenue = isy.Sales_Revenue.val(y)
    elif period_type == 'quarter':
        ebit = sum_quarters(y, isq.EBIT)
        sales_revenue = sum_quarters(y, isq.Sales_Revenue)
    ebit_margin = ebit / sales_revenue
    return ebit_margin


@is_null
def net_margin(y, isy, isq):
    # marża netto
    if period_type == 'year':
        net_income = isy.Net_Income.val(y)
        sales_revenue = isy.Sales_Revenue.val(y)
    elif period_type == 'quarter':
        net_income = sum_quarters(y, isq.Net_Income)
        sales_revenue = sum_quarters(y, isq.Sales_Revenue)
    net_margin = net_income / sales_revenue
    return net_margin


@is_null
def debt_to_equity_ratio(y, bly, blq):
    # poniżej 1 - dobry
    # powyżej 2,5 ryzykowny
    # bardzo niski poziom wskaźnika jest negatywnym sygnałem - firma nie wykorzystuje dźwigni długu do ekspansji
    # bankowość ma znacznie wyższy poziom wskaźnika
    # dopuszczalny wyższy w sektorach o powolnym i stabilnym wzroscie - np. użyteczność publiczna
    # ujemny wskaźnik oznacza ujemny equity (więcej zobowiązań od aktywów) - zagrożenie upadłością
    if period_type == 'year':
        total_liabilities = bly.Total_Liabilities.val(y)
        total_shareholders_equity = bly.Total_Shareholders_Equity.val(y)
    elif period_type == 'quarter':
        # total_liabilities = sum_quarters(y, blq.Total_Liabilities)
        # total_shareholders_equity = sum_quarters(y, blq.Total_Shareholders_Equity)
        total_liabilities = blq.Total_Liabilities.val(y[0])
        total_shareholders_equity = blq.Total_Shareholders_Equity.val(y[0])
    d_e_ratio = total_liabilities / total_shareholders_equity
    return d_e_ratio


@is_null
def total_debt_to_total_assets_ratio(y, bay, bly, baq, blq):
    # miara aktywów firmy finansowanych z zadłużenia
    # pokazuje jak firma rozwijała się i nabywała swoje aktywa w funkcji czasu
    # mówi czy firma posiada wystarczające fundusze aby sprostać swoim bieżącym zobowiązaniom
    # ponad 1 - firma ma więcej zobowiązań niż aktywów, ryzyko niewypłacalności w przypadku wzrostu stóp procentowych
    # poniżej 0,5 - większa częśc aktywów firmy jest finansowana kapitałem własnym
    # nie dostarcza żadnych wskazówek odnośnie jakości aktywów
    if period_type == 'year':
        total_liabilities = bly.Total_Liabilities.val(y)
        total_assets = bay.Total_Assets.val(y)
    elif period_type == 'quarter':
        # total_liabilities = sum_quarters(y, blq.Total_Liabilities)
        # total_assets = sum_quarters(y, baq.Total_Assets)
        total_liabilities = blq.Total_Liabilities.val(y[0])
        total_assets = baq.Total_Assets.val(y[0])
    td_ta = total_liabilities / total_assets
    return td_ta


@is_null
def capex_to_revenue_ratio(n, y, py, isy, bay, isq, baq):
    # stosunek inwestycji w kapitał stały do jej całkowitej sprzedaży
    # wydatek jest rozkładany na cały okres użytkowania składnika aktywów
    # najbardziej kapitałochłonne branże = najwyższe skaźniki -> spółki surowcowe, telekomunikacja, przemysł wytwórczy, użytecnzość publiczna
    if py is not None:
        if period_type == 'year':
            property_plant_equipment_gross_y = bay.Property_Plant_Equipment_Gross.val(y)
            property_plant_equipment_gross_py = bay.Property_Plant_Equipment_Gross.val(py)
            accumulated_depreciation_y = bay.Accumulated_Depreciation.val(y)
            accumulated_depreciation_py = bay.Accumulated_Depreciation.val(py)
            sales_revenue = isy.Sales_Revenue.val(y)
        elif period_type == 'quarter':
            # property_plant_equipment_gross_y = sum_quarters(y, baq.Property_Plant_Equipment_Gross)
            # property_plant_equipment_gross_py = sum_quarters(py, baq.Property_Plant_Equipment_Gross)
            # accumulated_depreciation_y = sum_quarters(y, baq.Accumulated_Depreciation)
            # accumulated_depreciation_py = sum_quarters(py, baq.Accumulated_Depreciation)
            property_plant_equipment_gross_y = baq.Property_Plant_Equipment_Gross.val(y[0])
            property_plant_equipment_gross_py = baq.Property_Plant_Equipment_Gross.val(py[0])
            accumulated_depreciation_y = baq.Accumulated_Depreciation.val(y[0])
            accumulated_depreciation_py = baq.Accumulated_Depreciation.val(py[0])
            sales_revenue = sum_quarters(y, isq.Sales_Revenue)

        capex = (property_plant_equipment_gross_y - property_plant_equipment_gross_py) \
                + (accumulated_depreciation_y - accumulated_depreciation_py)
        capex_revenue_ratio = capex / sales_revenue

    else:
        capex_revenue_ratio = '-'

    #if n != 0:
    #    capex = bay.Property_Plant_Equipment_Gross.val(y) - bay.Property_Plant_Equipment_Gross.val(py) + (
    #            bay.Accumulated_Depreciation.val(y) - bay.Accumulated_Depreciation.val(py))
    #    capex_revenue_ratio = capex / isy.Sales_Revenue.val(y)
    #else:
    #    capex_revenue_ratio = '-'
    return capex_revenue_ratio


@is_null
def altman_z_score(y, retained_earnings, isy, bay, bly, isq, baq, blq, price):
    # test wytrzymałości kredytowej
    # powyżej 3 - bezpiecznie
    # poniżej 1.8 - zagrożenie bankructwem
    if period_type == 'year':
        total_current_assets = bay.Total_Current_Assets.val(y)
        total_current_liabilities = bly.Total_Current_Liabilities.val(y)
        total_assets = bay.Total_Assets.val(y)
        net_income = isy.Net_Income.val(y)
        ebit = isy.EBIT.val(y)
        diluted_shares_outstanding = isy.Diluted_Shares_Outstanding.val(y)
        total_liabilities = bly.Total_Liabilities.val(y)
        sales_revenue = isy.Sales_Revenue.val(y)
    elif period_type == 'quarter':
        # total_current_assets = sum_quarters(y, baq.Total_Current_Assets)
        # total_current_liabilities = sum_quarters(y, blq.Total_Current_Liabilities)
        # total_assets = sum_quarters(y, baq.Total_Assets)
        total_current_assets = baq.Total_Current_Assets.val(y[0])
        total_current_liabilities = blq.Total_Current_Liabilities.val(y[0])
        total_assets = baq.Total_Assets.val(y[0])
        net_income = sum_quarters(y, isq.Net_Income)
        ebit = sum_quarters(y, isq.EBIT)
        # diluted_shares_outstanding = sum_quarters(y, isq.Diluted_Shares_Outstanding)
        # total_liabilities = sum_quarters(y, blq.Total_Liabilities)
        diluted_shares_outstanding = isq.Diluted_Shares_Outstanding.val(y[0])
        total_liabilities = blq.Total_Liabilities.val(y[0])
        sales_revenue = sum_quarters(y, isq.Sales_Revenue)

    X = (total_current_assets - total_current_liabilities) / total_assets
    Y = net_income * retained_earnings / total_assets
    V = ebit / total_assets
    B = price * diluted_shares_outstanding / total_liabilities
    Q = sales_revenue / total_assets

    #X = (bay.Total_Current_Assets.val(y) - bly.Total_Current_Liabilities.val(y)) / bay.Total_Assets.val(y)
    #Y = isy.Net_Income.val(y) * retained_earnings / bay.Total_Assets.val(y)
    #V = isy.EBIT.val(y) / bay.Total_Assets.val(y)
    #B = price * isy.Diluted_Shares_Outstanding.val(y) / bly.Total_Liabilities.val(y)
    #Q = isy.Sales_Revenue.val(y) / bay.Total_Assets.val(y)
    altman_z_score = 1.2 * X + 1.4 * Y + 3.3 * V + 0.6 * B + 1 * Q
    return altman_z_score


@is_null
def beneish_m_score(n, y, py, isy, bay, bly, cfy, isq, baq, blq, cfq):
    # ponizej -1.78 - przedsiębiorstwo nie jest manipulatorem
    # powyżej -1.78 - jest manipulatorem
    if py is not None:
        if period_type == 'year':
            accounts_receivables_net_y = bay.Accounts_Receivables_Net.val(y)
            accounts_receivables_net_py = bay.Accounts_Receivables_Net.val(py)
            sales_revenue_y = isy.Sales_Revenue.val(y)
            sales_revenue_py = isy.Sales_Revenue.val(py)
            cogs_exluding_d_a_y = isy.COGS_excluding_D_A.val(y)
            cogs_exluding_d_a_py = isy.COGS_excluding_D_A.val(py)
            total_current_assets_y = bay.Total_Current_Assets.val(y)
            total_current_assets_py = bay.Total_Current_Assets.val(py)
            net_property_plant_equipment_y = bay.Net_Property_Plant_Equipment.val(y)
            net_property_plant_equipment_py = bay.Net_Property_Plant_Equipment.val(py)
            depreciation_y = isy.Depreciation.val(y)
            depraciation_py = isy.Depreciation.val(py)
            sg_a_expense_y = isy.SG_A_Expense.val(y)
            sg_a_expense_py = isy.SG_A_Expense.val(py)
            total_current_liabilities_y = bly.Total_Current_Liabilities.val(y)
            total_current_liabilities_py = bly.Total_Current_Liabilities.val(py)
            long_term_debt_y = bly.Long_Term_Debt.val(y)
            long_term_debt_py = bly.Long_Term_Debt.val(py)
            net_income_y = isy.Net_Income.val(y)
            net_operationg_cash_flow_y = cfy.Net_Operating_Cash_Flow.val(y)
            total_assets_y = bay.Total_Assets.val(y)
            total_assets_py = bay.Total_Assets.val(py)
        elif period_type == 'quarter':
            # accounts_receivables_net_y = sum_quarters(y, baq.Accounts_Receivables_Net)
            # accounts_receivables_net_py = sum_quarters(py, baq.Accounts_Receivables_Net)
            accounts_receivables_net_y = baq.Accounts_Receivables_Net.val(y[0])
            accounts_receivables_net_py = baq.Accounts_Receivables_Net.val(py[0])
            sales_revenue_y = sum_quarters(y, isq.Sales_Revenue)
            sales_revenue_py = sum_quarters(py, isq.Sales_Revenue)
            cogs_exluding_d_a_y = sum_quarters(y, isq.COGS_excluding_D_A)
            cogs_exluding_d_a_py = sum_quarters(py, isq.COGS_excluding_D_A)
            # total_current_assets_y = sum_quarters(y, baq.Total_Current_Assets)
            # total_current_assets_py = sum_quarters(py, baq.Total_Current_Assets)
            total_current_assets_y = baq.Total_Current_Assets.val(y[0])
            total_current_assets_py = baq.Total_Current_Assets.val(py[0])
            # net_property_plant_equipment_y = sum_quarters(y, baq.Net_Property_Plant_Equipment)
            # net_property_plant_equipment_py = sum_quarters(py, baq.Net_Property_Plant_Equipment)
            net_property_plant_equipment_y = baq.Net_Property_Plant_Equipment.val(y[0])
            net_property_plant_equipment_py = baq.Net_Property_Plant_Equipment.val(py[0])
            depreciation_y = sum_quarters(y, isq.Depreciation)
            depraciation_py = sum_quarters(py, isq.Depreciation)
            sg_a_expense_y = sum_quarters(y, isq.SG_A_Expense)
            sg_a_expense_py = sum_quarters(py, isq.SG_A_Expense)
            # total_current_liabilities_y = sum_quarters(y, blq.Total_Current_Liabilities)
            # total_current_liabilities_py = sum_quarters(py, blq.Total_Current_Liabilities)
            total_current_liabilities_y = blq.Total_Current_Liabilities.val(y[0])
            total_current_liabilities_py = blq.Total_Current_Liabilities.val(py[0])
            # long_term_debt_y = sum_quarters(y, blq.Long_Term_Debt)
            # long_term_debt_py = sum_quarters(py, blq.Long_Term_Debt)
            long_term_debt_y = blq.Long_Term_Debt.val(y[0])
            long_term_debt_py = blq.Long_Term_Debt.val(py[0])
            net_income_y = sum_quarters(y, isq.Net_Income)
            net_operationg_cash_flow_y = sum_quarters(y, cfq.Net_Operating_Cash_Flow)
            # total_assets_y = sum_quarters(y, baq.Total_Assets)
            # total_assets_py = sum_quarters(py, baq.Total_Assets)
            total_assets_y = baq.Total_Assets.val(y[0])
            total_assets_py = baq.Total_Assets.val(py[0])

        DSRI = (accounts_receivables_net_y / sales_revenue_y) / (accounts_receivables_net_py / sales_revenue_py)
        GMI = ((sales_revenue_py - cogs_exluding_d_a_py) / sales_revenue_py) / ((sales_revenue_y - cogs_exluding_d_a_y) / sales_revenue_y)
        AQI = (1 - (total_current_assets_y + net_property_plant_equipment_y) / total_assets_y) / (1 - (total_current_assets_py + net_property_plant_equipment_py) / total_assets_py)
        SGI = sales_revenue_y / sales_revenue_py
        DEPI = (depraciation_py / (net_property_plant_equipment_py + depraciation_py)) / (depreciation_y / (net_property_plant_equipment_y + depreciation_y))
        SGAI = (sg_a_expense_y / sales_revenue_y) / (sg_a_expense_py / sales_revenue_py)
        LVGI = ((total_current_liabilities_y + long_term_debt_y) / total_assets_y) / ((total_current_liabilities_py + long_term_debt_py) / total_assets_py)
        TATA = (net_income_y - net_operationg_cash_flow_y) / total_assets_y
        beneish_m_score = -4.84 + 0.92 * DSRI + 0.528 * GMI + 0.404 * AQI + 0.892 * SGI + 0.115 * DEPI - 0.172 * SGAI + 4.679 * TATA - 0.327 * LVGI
    else:
        beneish_m_score = '-'
    return beneish_m_score


@is_null
def sloan_ratio(y, py, isy, bay, cfy, isq, baq, cfq):
    # zla formula obliczeniowa
    if py is not None:
        if period_type == 'year':
            net_property_plant_equipment_y = bay.Net_Property_Plant_Equipment.val(y)
            net_property_plant_equipment_py = bay.Net_Property_Plant_Equipment.val(py)
            net_income_y =  isy.Net_Income.val(y)
            net_operationg_cash_flow_y = cfy.Net_Operating_Cash_Flow.val(y)
            total_assets_y = bay.Total_Assets.val(y)
        elif period_type == 'quarter':
            # net_property_plant_equipment_y = sum_quarters(y, baq.Net_Property_Plant_Equipment)
            # net_property_plant_equipment_py = sum_quarters(py, baq.Net_Property_Plant_Equipment)
            net_property_plant_equipment_y = baq.Net_Property_Plant_Equipment.val(y[0])
            net_property_plant_equipment_py = baq.Net_Property_Plant_Equipment.val(py[0])
            net_income_y = sum_quarters(y, isq.Net_Income)
            net_operationg_cash_flow_y = sum_quarters(y, cfq.Net_Operating_Cash_Flow)
            # total_assets_y = sum_quarters(y, baq.Total_Assets)
            total_assets_y = baq.Total_Assets.val(y[0])

        cfi = net_property_plant_equipment_y - net_property_plant_equipment_py
        sloan_ratio = (net_income_y - net_operationg_cash_flow_y - cfi) / total_assets_y
    else:
        sloan_ratio = '-'
    return sloan_ratio


@is_null
def current_ratio(y, bay, bly, baq, blq):
    if period_type == 'year':
        total_current_assets_y = bay.Total_Current_Assets.val(y)
        total_current_liabilities_y = bly.Total_Current_Liabilities.val(y)
    elif period_type == 'quarter':
        total_current_assets_y = baq.Total_Current_Assets.val(y[0])
        total_current_liabilities_y = blq.Total_Current_Liabilities.val(y[0])

    current_ratio = total_current_assets_y / total_current_liabilities_y
    return current_ratio


@is_null
def p_s_ratio(y, isy, isq, price):
    # przydatny w wycenie akcji wzrostowych, które nie przyniosły jeszcze zysku lub doświadczyły tymczasowego niepowodzenia
    # przychód jest tylko wtedy wartościowy gdy w pewnym momencie można go przełożyć na zyski
    # różne branże mają różne marże więc wysokość przychodów moze być myląca
    # nie uwzględnia zysku a więc problemu spłaty długu
    if period_type == 'year':
        sales_revenue = isy.Sales_Revenue.val(y)
        diluted_shares_outstanding = isy.Diluted_Shares_Outstanding.val(y)
    elif period_type == 'quarter':
        sales_revenue = sum_quarters(y, isq.Sales_Revenue)
        diluted_shares_outstanding = isq.Diluted_Shares_Outstanding.val(y[0])

    p_s = price / (sales_revenue / diluted_shares_outstanding)
    return p_s


@is_null
def p_e_ratio(y, isy, isq, price):
    if period_type == 'year':
        diluted_shares_outstanding = isy.Diluted_Shares_Outstanding.val(y)
        net_income = isy.Net_Income.val(y)
    elif period_type == 'quarter':
        diluted_shares_outstanding = isq.Diluted_Shares_Outstanding.val(y[0])
        net_income = sum_quarters(y, isq.Net_Income)

    p_e = price * diluted_shares_outstanding / net_income
    return p_e


@is_null
def eps(y, isy, isq):
    if period_type == 'year':
        net_income = isy.Net_Income.val(y)
        diluted_shares_outstanding = isy.Diluted_Shares_Outstanding.val(y)
    elif period_type == 'quarter':
        net_income = sum_quarters(y, isq.Net_Income)
        diluted_shares_outstanding = isq.Diluted_Shares_Outstanding.val(y[0])

    eps = net_income / diluted_shares_outstanding
    return eps


@is_null
def peg(y, py, eps, isy, isq, price):
    # Peter Lynch
    # liczony z bieżącego roku jak i piecioletniej oczekiwanej stopie wzrostu
    # dodanie oczekiwanego wzrostu spółki pomaga skorygować wynik w przypadku spółek które mogą miec wysoką stopę wzrostu i wysoki wskaźnik P/E
    # ponizej 1 na pewno dobrze - Lynch
    if py is not None:
        if period_type == 'year':
            eps_basic_growth = isy.EPS_Basic_Growth.val(y)
        elif period_type == 'quarter':
            eps_basic_growth = isq.EPS_Basic.val(y[0]) / isq.EPS_Basic.val(py[0])

        peg = (price / eps) / eps_basic_growth / 100
    else:
        peg = '-'
    return peg


@is_null
def debt_service_coverage_ratio(y, isy, isq):
    if period_type == 'year':
        ebit = isy.EBIT.val(y)
        interest_expense = isy.Interest_Expense.val(y)
    elif period_type == 'quarter':
        ebit = sum_quarters(y, isq.EBIT)
        interest_expense = sum_quarters(y, isq.Interest_Expense)

    dscr = ebit / interest_expense
    return dscr


@is_null
def cash_ratio(y, bay, bly, baq, blq):
    if period_type == 'year':
        cash_short_term_investments = bay.Cash_Short_Term_Investments.val(y)
        total_current_liabilities = bly.Total_Current_Liabilities.val(y)
    elif period_type == 'quarter':
        cash_short_term_investments = baq.Cash_Short_Term_Investments.val(y[0])
        total_current_liabilities = blq.Total_Current_Liabilities.val(y[0])

    cash_ratio = cash_short_term_investments / total_current_liabilities
    return cash_ratio


@is_null
def operating_cash_flow_debt_ratio(y, cfy, bly, cfq, blq):
    if period_type == 'year':
        net_operating_cash_flow = cfy.Net_Operating_Cash_Flow.val(y)
        short_term_debt = bly.Short_Term_Debt.val(y)
        long_term_debt = bly.Long_Term_Debt.val(y)
    elif period_type == 'quarter':
        net_operating_cash_flow = sum_quarters(y, cfq.Net_Operating_Cash_Flow)
        short_term_debt = blq.Short_Term_Debt.val(y[0])
        long_term_debt = blq.Long_Term_Debt.val(y[0])

    cf_debt_ratio = net_operating_cash_flow / (short_term_debt + long_term_debt)
    return cf_debt_ratio


# directly from income statement
@is_null
def sales_revenue(y, isy, isq):
    if period_type == 'year':
        sales_revenue = isy.Sales_Revenue.val(y)
    elif period_type == 'quarter':
        sales_revenue = sum_quarters(y, isq.Sales_Revenue)

    return sales_revenue


@is_null
def gross_income(y, isy, isq):
    if period_type == 'year':
        gross_income = isy.Gross_Income.val(y)
    elif period_type == 'quarter':
        gross_income = sum_quarters(y, isq.Gross_Income)

    return gross_income


@is_null
def ebit(y, isy, isq):
    if period_type == 'year':
        ebit = isy.EBIT.val(y)
    elif period_type == 'quarter':
        ebit = sum_quarters(y, isq.EBIT)

    return ebit


@is_null
def ebitda(y, isy, isq):
    if period_type == 'year':
        ebitda = isy.EBITDA.val(y)
    elif period_type == 'quarter':
        ebitda = sum_quarters(y, isq.EBITDA)

    return ebitda


@is_null
def net_income(y, isy, isq):
    if period_type == 'year':
        net_income = isy.Net_Income.val(y)
    elif period_type == 'quarter':
        net_income = sum_quarters(y, isq.Net_Income)

    return net_income


@is_null
def research_development(y, isy, isq):
    if period_type == 'year':
        research_development = isy.Research_Development.val(y)
    elif period_type == 'quarter':
        research_development = sum_quarters(y, isq.Research_Development)

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