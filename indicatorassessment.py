import pandas as pd


class Grade:
    def __init__(self, tickers):
        self.color = None
        self.ress = []
        self.tic = None
        self.score = 0
        self.score_dict = {k: v for k, v in zip(tickers, [0 for x in tickers])}
        self.score_df = None
        self.color_dict = {}
        self.color_df = None

    def best(self):
        #
        self.color = '#831ef7'
        self.score += 5

    def vgood(self):
        #self.color = '#00FFFF'
        self.color = '#1e3ef7'
        self.score += 3

    def good(self):
        #self.color = '#00BFFF'
        self.color = '#3385FF'
        self.score += 2

    def ok(self):
        #self.color = '#CAFF70'
        self.color = '#99CCFF'
        self.score += 1

    def bad(self):
        #self.color = '#FF7F50'
        self.color = '#FF8888'
        self.score -= 1

    def vbad(self):
        #self.color = '#FF4040'
        self.color = '#FF3333'
        self.score -= 3

    def nograde(self):
        self.color = '#FFFFFF'

    def add_column(self, col_name):
        self.color_dict[col_name] = self.ress
        self.ress = []

    def add_res(self):
        self.ress.append(self.color)

    def get_color_df(self):
        self.color_df = pd.DataFrame(self.color_dict)
        return self.color_df

    def get_score_df(self):
        self.score_df = pd.DataFrame({'Ticker': self.score_dict.keys(), 'Score': self.score_dict.values()})
        return self.score_df

    def add_score(self):
        self.score_dict[self.tic] += self.score
        self.score = 0


class IndicatorAssessment:
    def __init__(self, df):
        self.total_df = df
        self.base_df = self.total_df[['Sector', 'Industry']]
        self.df = None
        self.name = None
        self.v = None
        self.ress = []

        self.tickers = None
        self.sectors = None
        self.industries = None
        self.vals = None

        self.sector_avg = None
        self.sector_median = None
        self.sector_max = None
        self.sector_min = None

        self.sector_avg_val = None
        self.sector_median_val = None
        self.sector_max_val = None
        self.sector_min_val = None

        self.industry_avg = None
        self.industry_median = None
        self.industry_max = None
        self.industry_min = None

        self.industry_avg_val = None
        self.industry_median_val = None
        self.industry_max_val = None
        self.industry_min_val = None

    def add(self, col_name):
        self.name = col_name
        self.tickers = self.total_df['Ticker'].values.tolist()
        self.sectors = self.total_df['Sector'].values.tolist()
        self.industries = self.total_df['Industry'].values.tolist()
        self.vals = self.total_df[col_name].values.tolist()
        self.df = self.base_df.copy()
        self.df[col_name] = self.vals

    def sector_comparative_values(self):
        gb = self.df[['Sector', self.name]].groupby('Sector')
        self.sector_avg, self.sector_median, self.sector_max, self.sector_min = self.__comparative_values(gb)

    def industry_comparative_values(self):
        gb = self.df[['Industry', self.name]].groupby('Industry')
        self.industry_avg, self.industry_median, self.industry_max, self.industry_min = self.__comparative_values(gb)

    def __comparative_values(self, gb):
        avg = gb.mean()
        median = gb.median()
        mmax = gb.max()
        mmin = gb.min()
        return avg, median, mmax, mmin

    def prepare_sector_industry_grouped_values(self, sector_group, industry_group):

        self.sector_avg_val = self.sector_avg.loc[sector_group][0]
        self.sector_median_val = self.sector_median.loc[sector_group][0]
        self.sector_max_val = self.sector_max.loc[sector_group][0]
        self.sector_min_val = self.sector_min.loc[sector_group][0]

        self.industry_avg_val = self.industry_avg.loc[industry_group][0]
        self.industry_median_val = self.industry_median.loc[industry_group][0]
        self.industry_max_val = self.industry_max.loc[industry_group][0]
        self.industry_min_val = self.industry_min.loc[industry_group][0]

    def reset_ress(self):
        self.ress = []

    def is_equal_to(self, x):
        if self.v == x:
            res = True
        else:
            res = False
        self.ress.append(res)
        return res

    def is_greater_than(self, x):
        if self.v >= x:
            res = True
        else:
            res = False
        self.ress.append(res)
        return res

    def is_less_than(self, x):
        if self.v <= x:
            res = True
        else:
            res = False
        self.ress.append(res)
        return res


def indicator_assessment(df):

    def evaluate_roa():
        # rentowność firmy w stosunku do jej całkowitych aktywów
        # efektywność wykorzystania aktywów
        # im większe ROE w stosunku do ROA tym większą dźwignię finansową stosuje firma
        # ograniczone zastosowanie bo różne wynik idla różnych branż (sprzyja bankom)
        # ogólnie powyzej 5% - dobrze, powyżej 20% - doskonale (jednak zawsze powinno być porównywane)
        if col == 'ROA':
            ind_ass.reset_ress()
            if ind_ass.is_less_than(0):
                grade.vbad()
            elif ind_ass.is_equal_to(ind_ass.sector_max_val) or ind_ass.is_equal_to(ind_ass.industry_max_val):
                grade.best()
            else:
                ind_ass.reset_ress()
                ind_ass.is_greater_than(0.05)
                ind_ass.is_greater_than(0.2)
                ind_ass.is_greater_than(ind_ass.sector_avg_val)
                if sum(ind_ass.ress) == 3:
                    grade.vgood()
                elif sum(ind_ass.ress) == 2:
                    grade.good()
                elif sum(ind_ass.ress) == 1:
                    grade.ok()
                else:
                    grade.bad()

    def evaluate_debt_to_equity_ratio():
        # poniżej 1 - dobry
        # powyżej 2,5 ryzykowny
        # bardzo niski poziom wskaźnika jest negatywnym sygnałem - firma nie wykorzystuje dźwigni długu do ekspansji
        # bankowość ma znacznie wyższy poziom wskaźnika
        # dopuszczalny wyższy w sektorach o powolnym i stabilnym wzroscie - np. użyteczność publiczna
        # ujemny wskaźnik oznacza ujemny equity (więcej zobowiązań od aktywów) - zagrożenie upadłością
        if col == 'Debt to Equity Ratio':
            ind_ass.reset_ress()
            if ind_ass.is_less_than(0):
                grade.vbad()
            elif ind_ass.is_less_than(0.2):
                grade.bad()
            elif ind_ass.is_less_than(1):
                grade.vgood()
            elif ind_ass.is_less_than(2.5):
                grade.good()
            else:
                grade.bad()

    def evaluate_total_debt_to_total_assets_ratio():
        # miara aktywów firmy finansowanych z zadłużenia
        # pokazuje jak firma rozwijała się i nabywała swoje aktywa w funkcji czasu
        # mówi czy firma posiada wystarczające fundusze aby sprostać swoim bieżącym zobowiązaniom
        # ponad 1 - firma ma więcej zobowiązań niż aktywów, ryzyko niewypłacalności w przypadku wzrostu stóp procentowych
        # poniżej 0,5 - większa częśc aktywów firmy jest finansowana kapitałem własnym
        # nie dostarcza żadnych wskazówek odnośnie jakości aktywów
        if col == 'Total Debt to Total Assets Ratio':
            ind_ass.reset_ress()
            if ind_ass.is_greater_than(1):
                grade.bad()
            elif ind_ass.is_greater_than(0.5):
                grade.ok()
            elif ind_ass.is_less_than(0.5):
                grade.good()

    def evaluate_beneish_m_score():
        # ponizej -1.78 - przedsiębiorstwo nie jest manipulatorem
        # powyżej -1.78 - jest manipulatorem
        if col == 'Beneish M Score':
            ind_ass.reset_ress()
            if ind_ass.is_less_than(1.78):
                grade.good()
            elif ind_ass.is_greater_than(1.78):
                grade.bad()

    def evaluate_altman_z_score():
        # test wytrzymałości kredytowej
        # powyżej 3 - bezpiecznie
        # poniżej 1.8 - zagrożenie bankructwem
        if col == 'Altman Z Score':
            ind_ass.reset_ress()
            if ind_ass.is_greater_than(3):
                grade.good()
            elif ind_ass.is_greater_than(1.8):
                grade.ok()
            else:
                grade.bad()

    def evaluate_p_s():
        if col == 'P/S':
            ind_ass.reset_ress()
            if ind_ass.is_less_than(0):
                grade.vbad()
            elif ind_ass.is_equal_to(ind_ass.sector_min_val) or ind_ass.is_equal_to(ind_ass.industry_min_val):
                grade.best()
            else:
                ind_ass.reset_ress()
                ind_ass.is_less_than(ind_ass.sector_avg_val)
                ind_ass.is_less_than(ind_ass.industry_avg_val)
                ind_ass.is_less_than(ind_ass.sector_median_val)
                ind_ass.is_less_than(ind_ass.industry_median_val)
                if sum(ind_ass.ress) == 4:
                    grade.vgood()
                elif sum(ind_ass.ress) > 1:
                    grade.good()
                elif sum(ind_ass.ress) > 0:
                    grade.ok()
                else:
                    grade.bad()


    def evaluate_p_e():
        if col == 'P/E':
            ind_ass.reset_ress()
            if ind_ass.is_less_than(0):
                grade.vbad()
            elif ind_ass.is_equal_to(ind_ass.sector_min_val) or ind_ass.is_equal_to(ind_ass.industry_min_val):
                grade.best()
            else:
                ind_ass.reset_ress()
                ind_ass.is_less_than(ind_ass.sector_avg_val)
                ind_ass.is_less_than(ind_ass.industry_avg_val)
                ind_ass.is_less_than(ind_ass.sector_median_val)
                ind_ass.is_less_than(ind_ass.industry_median_val)
                if sum(ind_ass.ress) == 4:
                    grade.good()
                elif sum(ind_ass.ress) > 0:
                    grade.ok()
                else:
                    grade.bad()




    ind_ass = IndicatorAssessment(df)
    grade = Grade(ind_ass.total_df['Ticker'].values.tolist())

    for col in df.columns[:3]:
        for i in df.index:
            grade.nograde()
            grade.add_res()
        grade.add_column(col)


    for col in df.columns[3:]:
        ind_ass.add(col)
        ind_ass.sector_comparative_values()
        ind_ass.industry_comparative_values()

        for t, s, i, v in zip(ind_ass.tickers, ind_ass.sectors, ind_ass.industries, ind_ass.vals):
            grade.nograde()
            grade.tic = t  # necessary for grade.score
            ind_ass.v = v
            ind_ass.prepare_sector_industry_grouped_values(s, i)

            evaluate_roa()
            evaluate_debt_to_equity_ratio()
            evaluate_total_debt_to_total_assets_ratio()
            evaluate_beneish_m_score()
            evaluate_altman_z_score()
            evaluate_p_s()
            evaluate_p_e()

            grade.add_res()  # adds colors to list
            grade.add_score()  # adds score from one indicator to total score of current ticker
        grade.add_column(col)  # joins ress lists

    color_df = grade.get_color_df()
    score_df = grade.get_score_df()

    return color_df, score_df
