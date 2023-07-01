import pandas as pd


class IndicatorCalculation:
    def __init__(self, finsts, price, price_subperiod, price_val_type, price_summarization, periods_real):
        self.finsts = finsts
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

    def __get_table_type_name(self):
        return f'{self.price_subperiod}_{self.price_val_type}_{self.price_summarization}'

    def calc_sales_revenue(self):
        res = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        self.period_indicators_values_l.append(res)

    def calc_p_s_ratio(self):
        # przydatny w wycenie akcji wzrostowych, które nie przyniosły jeszcze zysku lub doświadczyły tymczasowego niepowodzenia
        # przychód jest tylko wtedy wartościowy gdy w pewnym momencie można go przełożyć na zyski
        # różne branże mają różne marże więc wysokość przychodów moze być myląca
        # nie uwzględnia zysku a więc problemu spłaty długu
        sales_revenue = self.finsts.isq.Sales_Revenue.quarter_year_val(self.period_real)
        diluted_shares_outstanding = self.finsts.isq.Diluted_Shares_Outstanding.val(self.period_real)
        res = self.pv / (sales_revenue / diluted_shares_outstanding)
        self.period_price_indicators_values_l.append(res)
        print(sales_revenue)
        print(diluted_shares_outstanding)
        print(res)

    def update_indicators_without_price(self):
        self.df = pd.DataFrame()
        for period_real in self.periods_real:
            self.period_indicators_values_l = []
            self.period_real = period_real

            self.calc_sales_revenue()

            self.df[period_real] = self.period_indicators_values_l
        table_type_name = 'no_price'
        print(self.df)
        return self.df, table_type_name

    def update_indicators_with_price(self):
        self.df = pd.DataFrame()
        for period_real in self.periods_real:
            print(period_real)
            self.period_real = period_real
            self.price_val = self.price.val(self.period_real,
                                            self.price_subperiod,
                                            self.price_val_type,
                                            self.price_summarization)
            for price_period in self.price_val.keys():

                self.period_price_indicators_values_l = []
                self.pv = self.price_val[price_period]


                if price_period == '2023-03-31':
                    self.calc_p_s_ratio()


                self.df[price_period] = self.period_price_indicators_values_l

        table_type_name = self.__get_table_type_name()
        return self.df, table_type_name





