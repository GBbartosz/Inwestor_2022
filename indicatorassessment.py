import pandas as pd


class Grade:
    def __init__(self):
        self.color = None
        self.ress = []
        self.color_dict = {}
        self.df = None

    def vgood(self):
        self.color = '#00FFFF'

    def good(self):
        self.color = '#00BFFF'

    def ok(self):
        self.color = '#CAFF70'

    def bad(self):
        self.color = '#FF7F50'

    def vbad(self):
        self.color = '#FF4040'

    def nograde(self):
        self.color = '#FFFFFF'

    def add_column(self, col_name):
        self.color_dict[col_name] = self.ress
        self.ress = []

    def add_res(self):
        self.ress.append(self.color)

    def get_df(self):
        self.df = pd.DataFrame(self.color_dict)
        return self.df


class IndicatorAssessment:
    def __init__(self, df):
        self.total_df = df
        self.base_df = self.total_df[['Sector', 'Industry']]
        self.df = None
        self.name = None
        self.v = None
        self.grade = 0

        self.sectors = None
        self.industries = None
        self.vals = None

        self.sector_avg = None
        self.sector_median = None

        self.sector_avg_val = None
        self.sector_median_val = None

        self.industry_avg = None
        self.industry_median = None

        self.industry_avg_val = None
        self.industry_median_val = None

    def add(self, col_name):
        self.name = col_name
        self.sectors = self.total_df['Sector'].values.tolist()
        self.industries = self.total_df['Industry'].values.tolist()
        self.vals = self.total_df[col_name].values.tolist()
        self.df = self.base_df.copy()
        self.df[col_name] = self.vals

    def sector_comparative_values(self):
        gb = self.df[['Sector', self.name]].groupby('Sector')
        self.sector_avg, self.sector_median = self.__comparative_values(gb)

    def industry_comparative_values(self):
        gb = self.df[['Industry', self.name]].groupby('Industry')
        self.industry_avg, self.industry_median = self.__comparative_values(gb)

    def __comparative_values(self, gb):
        avg = gb.mean()
        median = gb.median()
        return avg, median

    def prepare_sector_industry_grouped_values(self, sector_group, industry_group):

        self.sector_avg_val = self.sector_avg.loc[sector_group][0]
        self.sector_median_val = self.sector_median.loc[sector_group][0]

        self.industry_avg_val = self.industry_avg.loc[industry_group][0]
        self.industry_median_val = self.industry_median.loc[industry_group][0]

    def is_greater_than(self, x):
        if self.v > x:
            res = True
        else:
            res = False
        self.ress.append(res)
        return res

    def is_less_than(self, x):
        if self.v > x:
            res = True
        else:
            res = False
        self.ress.append(res)
        return res




def indicator_assessment(df):

    def evaluate_roa():
        if col == 'ROA':
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

    grade = Grade()
    ind_ass = IndicatorAssessment(df)

    for col in df.columns[:3]:
        for i in df.index:
            grade.nograde()
            grade.add_res()
        grade.add_column(col)


    for col in df.columns[3:]:
        ind_ass.add(col)
        ind_ass.sector_comparative_values()
        ind_ass.industry_comparative_values()

        for s, i, v in zip(ind_ass.sectors, ind_ass.industries, ind_ass.vals):
            grade.nograde()
            ind_ass.v = v
            ind_ass.ress = []
            ind_ass.grade = 0
            ind_ass.prepare_sector_industry_grouped_values(s, i)

            evaluate_roa()

            grade.add_res()
        grade.add_column(col)

    adf = grade.get_df()

    return adf
