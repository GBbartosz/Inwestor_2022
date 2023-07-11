import pandas as pd


class IndicatorCalculation:
    def __init__(self, finsts, price, price_subperiod, price_val_type, price_summarization, periods_real):
        self.finsts = finsts
        self.ticker_name = self.finsts.ticker_name
        self.price = price
        self.price_subperiod = price_subperiod
        self.price_val_type = price_val_type
        self.price_summarization = price_summarization
        self.price_val = None
        self.pv = None
        self.periods_real = periods_real
        self.period_real = None
        self.df = None
        self.period_indicators_values_l = None
        self.period_price_indicators_values_l = None
        self.noprice_indicators = ['Revenue', 'Gross Income', 'EBIT', 'EBITDA', 'NOPAT', 'Net Income', 'Research and Development', 'Total Debt', 'ROE', 'Retained Earnings', 'Stopa wzrostu', 'ROA', 'ROC', 'ROCE', 'ROIC', 'Gross Margins', 'EBITDA Margin', 'EBIT Margin', 'Net Margin', 'Debt to Equity Ratio', 'Total Debt to Total Assets Ratio', 'CAPEX to Revenue Ratio', 'Beneish M Score', 'Current Ratio', 'EPS', 'Debt Service Coverage Ratio', 'Cash Ratio', 'Operating Cash Flow Debt Ratio']
        self.price_indicators = ['P/S', 'Altman Z Score', 'P/E', 'PEG']

    def __get_table_type_name(self):
        return f'{self.price_subperiod}_{self.price_val_type}_{self.price_summarization}'

    def __null_handler(myfunction):
        def inner(self):
            try:
                res = myfunction(self)
            except (ZeroDivisionError, TypeError):
                res = None
            return res
        return inner

    def __null_handler_no_price_indicators(myfunction):
        def inner(self):
            try:
                myfunction(self)
            except (ZeroDivisionError, TypeError):
                res = None
                self.period_indicators_values_l.append(res)
        return inner

    def __null_handler_price_indicators(myfunction):
        def inner(self):
            try:
                myfunction(self)
            except (ZeroDivisionError, TypeError):
                res = None
                self.period_price_indicators_values_l.append(res)
        return inner

    # usable in other calculations

    @__null_handler
    def ebit(self):
        revenue = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        cogs = self.finsts.isq.Cost_of_Goods_Sold_COGS_incl_D_A.quarter_year_val(self.period_real)
        operating_expenses = self.finsts.isq.SG_A_Expense.quarter_year_val(self.period_real)
        res = revenue - cogs - operating_expenses
        return res

    @__null_handler
    def nopat(self):
        ebit = self.ebit()
        income_tax = self.finsts.isq.Income_Tax.quarter_year_val(self.period_real)
        res = ebit - income_tax
        return res

    @__null_handler
    def total_debt(self):
        short_term_debt = self.finsts.blq.Short_Term_Debt.val(self.period_real)
        long_term_debt = self.finsts.blq.Long_Term_Debt.val(self.period_real)
        res = short_term_debt + long_term_debt
        return res

    @__null_handler
    def roe(self):
        # stopa zwrotu z kapitalu wlasnego
        # w %
        # efektywnosc w generownaiu zyskow
        # okreslenie czy wskaznik jest dobry czy zly zalezy od spolek porownywalnych
        # porwnywanie do sredniej dla spolek z sektora
        # poziom 15% czyli średnia S&P500 jest akceptowalny
        # ujemny lub bardzo wysoki ROE (ujemny dochod i kapital wlasny) to sygnal ostrzegawczy
        # maloprawdopodobne ale ujemny roe moze wynikac z progrmau wykupu akcji wlasnych oraz doskonalego zarzadzania
        net_income = self.finsts.isq.Net_Income.quarter_year_val(self.period_real)
        total_equity = self.finsts.blq.Total_Equity.val(self.period_real)
        res = net_income / total_equity
        return res

    @__null_handler
    def retained_earnings(self):
        dividends_payable = self.finsts.blq.Dividends_Payable.val(self.period_real)
        net_income = self.finsts.isq.Net_Income.quarter_year_val(self.period_real)
        res = 1 - (dividends_payable / net_income)
        return res

    @__null_handler
    def eps(self):
        diluted_shares_outstanding = self.finsts.isq.Diluted_Shares_Outstanding.val(self.period_real)
        net_income = self.finsts.isq.Net_Income.quarter_year_val(self.period_real)
        res = net_income / diluted_shares_outstanding
        return res






    # no price indicators

    @__null_handler_no_price_indicators
    def calc_sales_revenue(self):
        res = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_gross_income(self):
        res = self.finsts.isq.Gross_Income.quarter_year_val(self.period_real)
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_ebit(self):
        res = self.ebit()
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_ebitda(self):
        res = self.finsts.isq.EBITDA.quarter_year_val(self.period_real)
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_nopat(self):
        res = self.nopat()
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_net_income(self):
        res = self.finsts.isq.Net_Income.quarter_year_val(self.period_real)
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_research_and_development(self):
        res = self.finsts.isq.Research_Development.quarter_year_val(self.period_real)
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_total_debt(self):
        res = self.total_debt()
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_roe(self):
        res = self.roe()
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_retained_earnings(self):
        res = self.retained_earnings()
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_stopa_wzrostu(self):
        # %
        res = self.roe() * self.retained_earnings()
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_roa(self):
        # rentowność firmy w stosunku do jej całkowitych aktywów
        # efektywność wykorzystania aktywów
        # im większe ROE w stosunku do ROA tym większą dźwignię finansową stosuje firma
        # ograniczone zastosowanie bo różne wynik idla różnych branż (sprzyja bankom)
        # ogólnie powyzej 5% - dobrze, powyżej 20% - doskonale (jednak zawsze powinno być porównywane)
        net_income = self.finsts.isq.Net_Income.quarter_year_val(self.period_real)
        total_assets = self.finsts.baq.Total_Assets.val(self.period_real)
        res = net_income / total_assets
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_roc(self):
        # zwrot z kapitału
        ebit = self.ebit()
        total_equity = self.finsts.blq.Total_Equity.val(self.period_real)
        res = ebit / total_equity
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_roce(self):
        # return on capital employed
        # szczególnie przydatny w oceniuniu spółek w sektorach kapitałochłonnych - media, telekomunikacja, użyteczność publiczna
        # ważny jest trend
        ebit = self.ebit()
        total_assets = self.finsts.baq.Total_Assets.val(self.period_real)
        total_current_liabilities = self.finsts.blq.Total_Current_Liabilities.val(self.period_real)
        res = ebit / (total_assets - total_current_liabilities)
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_roic(self):
        # zwrot z zainwestowanego kapitału
        nopat = self.nopat()
        dividends_payable = self.finsts.blq.Dividends_Payable.val(self.period_real)
        cash_only = self.finsts.baq.Cash_Only.val(self.period_real)
        total_equity = self.finsts.blq.Total_Equity.val(self.period_real)
        total_debt = self.total_debt()
        res = (nopat - dividends_payable) / (total_debt - cash_only + total_equity)
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_gross_margin(self):
        # przychód po odjęciu tylko kosztów bezpośrednio związanych z wytworzeniem dóbr
        gross_income = self.finsts.isq.Gross_Income.quarter_year_val(self.period_real)
        sales_revenue = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        res = gross_income / sales_revenue
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_ebitda_margin(self):
        # przychód brutto po odjęciu dodatkowych kosztów administacyjnych, wydatków na badania
        # eliminuje wpływ polityki finansowej i księgowej
        ebitda = self.finsts.isq.EBITDA.quarter_year_val(self.period_real)
        sales_revenue = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        res = ebitda / sales_revenue
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_ebit_margin(self):
        # marża operacyjna
        # rentowność sprzedaży
        ebit = self.ebit()
        sales_revenue = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        res = ebit / sales_revenue
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_net_margin(self):
        # marża netto
        net_income = self.finsts.isq.Net_Income.quarter_year_val(self.period_real)
        sales_revenue = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        res = net_income / sales_revenue
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_debt_to_equity_ratio(self):
        # poniżej 1 - dobry
        # powyżej 2,5 ryzykowny
        # bardzo niski poziom wskaźnika jest negatywnym sygnałem - firma nie wykorzystuje dźwigni długu do ekspansji
        # bankowość ma znacznie wyższy poziom wskaźnika
        # dopuszczalny wyższy w sektorach o powolnym i stabilnym wzroscie - np. użyteczność publiczna
        # ujemny wskaźnik oznacza ujemny equity (więcej zobowiązań od aktywów) - zagrożenie upadłością
        total_liabilities = self.finsts.blq.Total_Liabilities.val(self.period_real)
        total_shareholders_equity = self.finsts.blq.Total_Shareholders_Equity.val(self.period_real)
        res = total_liabilities / total_shareholders_equity
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_total_debt_to_total_assets_ratio(self):
        # miara aktywów firmy finansowanych z zadłużenia
        # pokazuje jak firma rozwijała się i nabywała swoje aktywa w funkcji czasu
        # mówi czy firma posiada wystarczające fundusze aby sprostać swoim bieżącym zobowiązaniom
        # ponad 1 - firma ma więcej zobowiązań niż aktywów, ryzyko niewypłacalności w przypadku wzrostu stóp procentowych
        # poniżej 0,5 - większa częśc aktywów firmy jest finansowana kapitałem własnym
        # nie dostarcza żadnych wskazówek odnośnie jakości aktywów
        total_liabilities = self.finsts.blq.Total_Liabilities.val(self.period_real)
        total_assets = self.finsts.baq.Total_Assets.val(self.period_real)
        res = total_liabilities / total_assets
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_capex_to_revenue_ratio(self):
        # stosunek inwestycji w kapitał stały do jej całkowitej sprzedaży
        # wydatek jest rozkładany na cały okres użytkowania składnika aktywów
        # najbardziej kapitałochłonne branże = najwyższe skaźniki -> spółki surowcowe, telekomunikacja, przemysł wytwórczy, użytecnzość publiczna
        property_plant_equipment_gross_y = self.finsts.baq.Property_Plant_Equipment_Gross.val(self.period_real)
        property_plant_equipment_gross_py = self.finsts.baq.Property_Plant_Equipment_Gross.val_prev_year(self.period_real)
        accumulated_depreciation_y = self.finsts.baq.Accumulated_Depreciation.val(self.period_real)
        accumulated_depreciation_py = self.finsts.baq.Accumulated_Depreciation.val_prev_year(self.period_real)
        sales_revenue = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)

        capex = (property_plant_equipment_gross_y - property_plant_equipment_gross_py) + (accumulated_depreciation_y - accumulated_depreciation_py)
        res = capex / sales_revenue
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_beneish_m_score(self):
        # ponizej -1.78 - przedsiębiorstwo nie jest manipulatorem
        # powyżej -1.78 - jest manipulatorem
        accounts_receivables_net_y = self.finsts.baq.Accounts_Receivables_Net.val(self.period_real)
        accounts_receivables_net_py = self.finsts.baq.Accounts_Receivables_Net.val_prev_year(self.period_real)
        sales_revenue_y = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        sales_revenue_py = self.finsts.isq.Sales_Revenue.previous_year_quarter_year_val(self.period_real)
        cogs_exluding_d_a_y = self.finsts.isq.COGS_excluding_D_A.quarter_year_val(self.period_real)
        cogs_exluding_d_a_py = self.finsts.isq.COGS_excluding_D_A.previous_year_quarter_year_val(self.period_real)
        total_current_assets_y = self.finsts.baq.Total_Current_Assets.val(self.period_real)
        total_current_assets_py = self.finsts.baq.Total_Current_Assets.val_prev_year(self.period_real)
        net_property_plant_equipment_y = self.finsts.baq.Net_Property_Plant_Equipment.val(self.period_real)
        net_property_plant_equipment_py = self.finsts.baq.Net_Property_Plant_Equipment.val_prev_year(self.period_real)
        depreciation_y = self.finsts.isq.Depreciation.quarter_year_val(self.period_real)
        depraciation_py = self.finsts.isq.Depreciation.previous_year_quarter_year_val(self.period_real)
        sg_a_expense_y = self.finsts.isq.SG_A_Expense.quarter_year_val(self.period_real)
        sg_a_expense_py = self.finsts.isq.SG_A_Expense.previous_year_quarter_year_val(self.period_real)
        total_current_liabilities_y = self.finsts.blq.Total_Current_Liabilities.val(self.period_real)
        total_current_liabilities_py = self.finsts.blq.Total_Current_Liabilities.val_prev_year(self.period_real)
        long_term_debt_y = self.finsts.blq.Long_Term_Debt.val(self.period_real)
        long_term_debt_py = self.finsts.blq.Long_Term_Debt.val_prev_year(self.period_real)
        net_income_y = self.finsts.isq.Net_Income.quarter_year_val(self.period_real)
        net_operationg_cash_flow_y = self.finsts.cfq.Net_Operating_Cash_Flow.quarter_year_val(self.period_real)
        total_assets_y = self.finsts.baq.Total_Assets.val(self.period_real)
        total_assets_py = self.finsts.baq.Total_Assets.val_prev_year(self.period_real)

        DSRI = (accounts_receivables_net_y / sales_revenue_y) / (accounts_receivables_net_py / sales_revenue_py)
        GMI = ((sales_revenue_py - cogs_exluding_d_a_py) / sales_revenue_py) / ((sales_revenue_y - cogs_exluding_d_a_y) / sales_revenue_y)
        AQI = (1 - (total_current_assets_y + net_property_plant_equipment_y) / total_assets_y) / (1 - (total_current_assets_py + net_property_plant_equipment_py) / total_assets_py)
        SGI = sales_revenue_y / sales_revenue_py
        DEPI = (depraciation_py / (net_property_plant_equipment_py + depraciation_py)) / (depreciation_y / (net_property_plant_equipment_y + depreciation_y))
        SGAI = (sg_a_expense_y / sales_revenue_y) / (sg_a_expense_py / sales_revenue_py)
        LVGI = ((total_current_liabilities_y + long_term_debt_y) / total_assets_y) / ((total_current_liabilities_py + long_term_debt_py) / total_assets_py)
        TATA = (net_income_y - net_operationg_cash_flow_y) / total_assets_y
        res = -4.84 + 0.92 * DSRI + 0.528 * GMI + 0.404 * AQI + 0.892 * SGI + 0.115 * DEPI - 0.172 * SGAI + 4.679 * TATA - 0.327 * LVGI
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_current_ratio(self):
        total_current_assets = self.finsts.baq.Total_Current_Assets.val(self.period_real)
        total_current_liabilities = self.finsts.blq.Total_Current_Liabilities.val(self.period_real)
        res = total_current_assets / total_current_liabilities
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_eps(self):
        res = self.eps()
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_debt_service_coverage_ratio(self):
        # brakuje principal payments w sprawozdaniach do pelnego obliczenia wskaznika
        interest_expense = self.finsts.isq.Interest_Expense.quarter_year_val(self.period_real)
        if interest_expense == 0:
            debt_service_coverage_ratio = None
        else:
            debt_service_coverage_ratio = self.ebit() / interest_expense
        res = debt_service_coverage_ratio
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_cash_ratio(self):
        cash_short_term_investments = self.finsts.baq.Cash_Short_Term_Investments.val(self.period_real)
        total_current_liabilities = self.finsts.blq.Total_Current_Liabilities.val(self.period_real)
        res = cash_short_term_investments / total_current_liabilities
        self.period_indicators_values_l.append(res)

    @__null_handler_no_price_indicators
    def calc_operating_cash_flow_debt_ratio(self):
        net_operating_cash_flow = self.finsts.cfq.Net_Operating_Cash_Flow.quarter_year_val(self.period_real)
        short_term_debt = self.finsts.blq.Short_Term_Debt.val(self.period_real)
        long_term_debt = self.finsts.blq.Long_Term_Debt.val(self.period_real)
        res = net_operating_cash_flow / (short_term_debt + long_term_debt)
        self.period_indicators_values_l.append(res)



    # price indicators

    @__null_handler_price_indicators
    def calc_p_s_ratio(self):
        # przydatny w wycenie akcji wzrostowych, które nie przyniosły jeszcze zysku lub doświadczyły tymczasowego niepowodzenia
        # przychód jest tylko wtedy wartościowy gdy w pewnym momencie można go przełożyć na zyski
        # różne branże mają różne marże więc wysokość przychodów moze być myląca
        # nie uwzględnia zysku a więc problemu spłaty długu
        sales_revenue = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        diluted_shares_outstanding = self.finsts.isq.Diluted_Shares_Outstanding.val(self.period_real)
        res = self.pv / (sales_revenue / diluted_shares_outstanding)
        self.period_price_indicators_values_l.append(res)

    @__null_handler_price_indicators
    def calc_altman_z_score(self):
        # test wytrzymałości kredytowej
        # powyżej 3 - bezpiecznie
        # poniżej 1.8 - zagrożenie bankructwem
        total_current_assets = self.finsts.baq.Total_Current_Assets.val(self.period_real)
        total__current_liabilities = self.finsts.blq.Total_Current_Liabilities.val(self.period_real)
        total_assets = self.finsts.baq.Total_Assets.val(self.period_real)
        net_income = self.finsts.isq.Net_Income.quarter_year_val(self.period_real)
        diluted_shares_outstanding = self.finsts.isq.Diluted_Shares_Outstanding.val(self.period_real)
        total_liabilities = self.finsts.blq.Total_Liabilities.val(self.period_real)
        sales_revenue = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)

        X = (total_current_assets - total__current_liabilities) / total_assets
        Y = net_income * self.retained_earnings() / total_assets
        V = self.ebit() / total_assets
        B = self.pv * diluted_shares_outstanding / total_liabilities
        Q = sales_revenue / total_assets

        res = 1.2 * X + 1.4 * Y + 3.3 * V + 0.6 * B + 1 * Q
        self.period_price_indicators_values_l.append(res)

    @__null_handler_price_indicators
    def calc_p_e_ratio(self):
        diluted_shares_outstanding = self.finsts.isq.Diluted_Shares_Outstanding.val(self.period_real)
        net_income = self.finsts.isq.Net_Income.quarter_year_val(self.period_real)
        res = self.pv * diluted_shares_outstanding / net_income
        self.period_price_indicators_values_l.append(res)

    @__null_handler_price_indicators
    def calc_peg(self):
        eps_basic_growth = self.finsts.isq.EPS_Basic_Growth.val(self.period_real) / self.finsts.isq.EPS_Basic_Growth.val_prev_year(self.period_real)
        print(self.period_real)
        print(self.pv)
        print(self.eps())
        print(eps_basic_growth)
        res = (self.pv / self.eps()) / eps_basic_growth / 100
        self.period_price_indicators_values_l.append(res)

    def update_indicators_without_price(self):
        self.df = pd.DataFrame()
        self.df['Ticker'] = len(self.noprice_indicators) * [self.ticker_name]
        self.df['Indicator'] = self.noprice_indicators
        for period_real in self.periods_real:
            self.period_indicators_values_l = []
            self.period_real = period_real

            self.calc_sales_revenue()
            self.calc_gross_income()
            self.calc_ebit()
            self.calc_ebitda()
            self.calc_nopat()
            self.calc_net_income()
            self.calc_research_and_development()
            self.calc_total_debt()
            self.calc_roe()
            self.calc_retained_earnings()
            self.calc_stopa_wzrostu()
            self.calc_roa()
            self.calc_roc()
            self.calc_roce()
            self.calc_roic()
            self.calc_gross_margin()
            self.calc_ebitda_margin()
            self.calc_ebit_margin()
            self.calc_net_margin()
            self.calc_debt_to_equity_ratio()
            self.calc_total_debt_to_total_assets_ratio()
            self.calc_capex_to_revenue_ratio()
            self.calc_beneish_m_score()
            self.calc_current_ratio()
            self.calc_eps()
            self.calc_debt_service_coverage_ratio()
            self.calc_cash_ratio()
            self.calc_operating_cash_flow_debt_ratio()

            self.df[period_real] = self.period_indicators_values_l
        table_type_name = 'no_price'
        return self.df, table_type_name

    def update_indicators_with_price(self):
        self.df = pd.DataFrame()
        self.df['Ticker'] = len(self.price_indicators) * [self.ticker_name]
        self.df['Indicator'] = self.price_indicators
        for period_real in self.periods_real:
            self.period_real = period_real
            self.price_val = self.price.val(self.period_real,
                                            self.price_subperiod,
                                            self.price_val_type,
                                            self.price_summarization)
            for price_period in self.price_val.keys():

                self.period_price_indicators_values_l = []
                self.pv = self.price_val[price_period]

                self.calc_p_s_ratio()
                self.calc_altman_z_score()
                self.calc_p_e_ratio()
                self.calc_peg()

                self.df[price_period] = self.period_price_indicators_values_l

        table_type_name = self.__get_table_type_name()
        return self.df, table_type_name
