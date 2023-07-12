import pandas as pd
import update
import utilities as u


class FinancialStatements:
    def __init__(self, ticker):
        self.wsj_cursor, self.wsj_conn, self.wsj_engine = u.create_sql_connection('wsj')
        self.ticker_name = ticker

        self.faulty_column_detected = self.FaultyColumnDetected()
        self.__create_all_one_financial_statement()

        if self.faulty_column_detected.status:  # case when faulty column detected and try to update
            print(f'Error column detected for {self.ticker_name} (update ticker)')
            for table, col in zip(self.faulty_column_detected.tables, self.faulty_column_detected.columns):
                self.__drop_faulty_column(table, col)
            self.__repair_column_name_by_updating_ticker()

            self.faulty_column_detected = self.FaultyColumnDetected()
            self.__create_all_one_financial_statement()

        if self.faulty_column_detected.status:  # case when faulty column detected again and delete faulty columns without update
            print(f'Error 2 column detected for {self.ticker_name}, (delete column without update)')
            for table, col in zip(self.faulty_column_detected.tables, self.faulty_column_detected.columns):
                self.__drop_faulty_column(table, col)
            self.__create_all_one_financial_statement()

    class FaultyColumnDetected:
        def __init__(self):
            self.status = False
            self.tables = []
            self.columns = []

    def __drop_faulty_column(self, table, col):
        sql_query = f'''
                    ALTER TABLE [wsj].[dbo].[{table}]
                    DROP COLUMN [{col}]
                    '''
        self.wsj_cursor.execute(sql_query)

    def __repair_column_name_by_updating_ticker(self):
        ticker_tables = u.create_basic_ticker_table_name(self.ticker_name)
        update.update(self.ticker_name, ticker_tables)

    def __create_all_one_financial_statement(self):
        self.isq = OneFinancialStatement('income_statement', self.ticker_name, 'q', self.faulty_column_detected)
        self.baq = OneFinancialStatement('balance_assets', self.ticker_name, 'q', self.faulty_column_detected)
        self.blq = OneFinancialStatement('balance_liabilities', self.ticker_name, 'q', self.faulty_column_detected)
        self.cfq = OneFinancialStatement('cash_flow', self.ticker_name, 'q', self.faulty_column_detected)

class OneFinancialStatement:
    def __init__(self, fin_st_type, ticker, period_type, faulty_column_detected):
        self.fin_st_type = fin_st_type
        self.ticker = ticker
        self.faulty_column_detected = faulty_column_detected
        self.period_type = period_type
        self.wsj_cursor, self.wsj_conn, self.wsj_engine = u.create_sql_connection('wsj')
        self.table_name = ticker + '_' + fin_st_type + '_' + period_type

        # list of all periods
        if self.period_type == 'y':
            self.all_periods = u.years_generator()
        elif self.period_type == 'q':
            self.all_periods = u.quarters_generator()
        else:
            print('invalid period in OneFinancialStatement class')

        # preparing df with quarter or year periods
        self.df = None
        self.all_periods_month_name = None
        self.all_periods_real = None
        self.__get_and_prepare_df()
        self.__detect_errors()  # deletes invalid column (0001) and updates
        self.indicators = self.df.iloc[:, 1].to_list()

        if self.fin_st_type == 'income_statement':
            self.Sales_Revenue = None
            self.Sales_Growth = None
            self.Cost_of_Goods_Sold_COGS_incl_D_A = None
            self.COGS_excluding_D_A = None
            self.Depreciation_Amortization_Expense = None
            self.Depreciation = None
            self.Amortization_of_Intangibles = None
            self.Amortization_of_Deferred_Charges = None
            self.COGS_Growth = None
            self.Gross_Income = None
            self.Gross_Income_Growth = None
            self.Gross_Profit_Margin = None
            self.SG_A_Expense = None
            self.Research_Development = None
            self.Other_SG_A = None
            self.SGA_Growth = None
            self.Other_Operating_Expense = None
            self.EBIT = None
            self.Unusual_Expense = None
            self.Non_Operating_Income_Expense = None
            self.Non_Operating_Interest_Income = None
            self.Equity_in_Affiliates_Preta = None
            self.Interest_Expense = None
            self.Interest_Expense_Growth = None
            self.Gross_Interest_Expense = None
            self.Interest_Capitalized = None
            self.Pretax_Income = None
            self.Pretax_Income_Growth = None
            self.Pretax_Margin = None
            self.Income_Tax = None
            self.Income_Tax_Current_Domestic = None
            self.Income_Tax_Current_Foreign = None
            self.Income_Tax_Deferred_Domestic = None
            self.Income_Tax_Deferred_Foreign = None
            self.Income_Tax_Credits = None
            self.Equity_in_Affiliates = None
            self.Other_After_Tax_Income_Expens = None
            self.Consolidated_Net_Income = None
            self.Minority_Interest_Expense = None
            self.Net_Income = None
            self.Net_Income_Growth = None
            self.Net_Margin = None
            self.Extraordinaries_Discontinued_Operations = None
            self.Extra_Items_Gain_Loss_Sale_Of_Assets = None
            self.Cumulative_Effect_Accounting_Chg = None
            self.Discontinued_Operations = None
            self.Net_Income_After_Extraordinaries = None
            self.Preferred_Dividends = None
            self.Net_Income_Available_to_Common = None
            self.EPS_Basic = None
            self.EPS_Basic_Growth = None
            self.Basic_Shares_Outstanding = None
            self.EPS_Diluted = None
            self.EPS_Diluted_Growth = None
            self.Diluted_Shares_Outstanding = None
            self.EBITDA = None
            self.EBITDA_Growth = None
            self.EBITDA_Margin = None
            self.EBIT = None
        elif self.fin_st_type == 'balance_assets':
            self.Net_Income_before_Extraordinaries = None
            self.Cash_Short_Term_Investments = None
            self.Cash_Only = None
            self.Short_Term_Investments = None
            self.Cash_Short_Term_Investments_Growth = None
            self.Cash_ST_Investments_Total_Assets = None
            self.Total_Accounts_Receivable = None
            self.Accounts_Receivables_Net = None
            self.Accounts_Receivables_Gross = None
            self.Bad_Debt_Doubtful_Accounts = None
            self.Other_Receivables = None
            self.Accounts_Receivable_Growth = None
            self.Accounts_Receivable_Turnover = None
            self.Inventories = None
            self.Finished_Goods = None
            self.Work_in_Progress = None
            self.Raw_Materials = None
            self.Progress_Payments_Other = None
            self.Other_Current_Assets = None
            self.Prepaid_Expenses = None
            self.Miscellaneous_Current_Assets = None
            self.Total_Current_Assets = None
            self.Net_Property_Plant_Equipment = None
            self.Property_Plant_Equipment_Gross = None
            self.Buildings = None
            self.Land_Improvements = None
            self.Machinery_Equipment = None
            self.Construction_in_Progress = None
            self.Leases = None
            self.Computer_Software_and_Equipment = None
            self.Leased_Property = None
            self.Transportation_Equipment = None
            self.Other_Property_Plant_Equipment = None
            self.Accumulated_Depreciation = None
            self.Buildings = None
            self.Land_Improvements = None
            self.Machinery_Equipment = None
            self.Construction_in_Progress = None
            self.Leases = None
            self.Computer_Software_and_Equipment = None
            self.Leased_Property = None
            self.Transportation_Equipment = None
            self.Other_Property_Plant_Equipment = None
            self.Total_Investments_and_Advances = None
            self.LT_Investment_Affiliate_Companies = None
            self.Other_Long_Term_Investments = None
            self.Long_Term_Note_Receivable = None
            self.Intangible_Assets = None
            self.Net_Goodwill = None
            self.Net_Other_Intangibles = None
            self.Other_Assets = None
            self.Deferred_Charges = None
            self.Tangible_Other_Assets = None
            self.Total_Assets = None
            self.Assets_Total_Growth = None
            self.Asset_Turnover = None
            self.Return_On_Average_Assets = None
        elif self.fin_st_type == 'balance_liabilities':
            self.ST_Debt_Current_Portion_LT_Debt = None
            self.Short_Term_Debt = None
            self.Current_Portion_of_Long_Term_Debt = None
            self.Accounts_Payable = None
            self.Accounts_Payable_Growth = None
            self.Income_Tax_Payable = None
            self.Other_Current_Liabilities = None
            self.Dividends_Payable = None
            self.Accrued_Payroll = None
            self.Miscellaneous_Current_Liabilities = None
            self.Total_Current_Liabilities = None
            self.Total_Current_Assets_FOR_CALCULATION_PURPOSES_ONLY = None
            self.Total_Assets_FOR_CALCULATION_PURPOSES_ONLY = None
            self.Inventories_FOR_CALCULATION_PURPOSES_ONLY = None
            self.Cash_Short_Term_Investments_FOR_CALCULATION_PURPOSES_ONLY = None
            self.Current_Ratio = None
            self.Quick_Ratio = None
            self.Cash_Ratio = None
            self.Long_Term_Debt = None
            self.Long_Term_Debt_excl_Capitalized_Leases = None
            self.Non_Convertible_Debt = None
            self.Convertible_Debt = None
            self.Capitalized_Lease_Obligations = None
            self.Provision_for_Risks_Charges = None
            self.Deferred_Taxes = None
            self.Deferred_Taxes_Credit = None
            self.Deferred_Taxes_Debit = None
            self.Other_Liabilities = None
            self.Deferred_Tax_Liability_Untaxed_Reserves = None
            self.Other_Liabilities_excl_Deferred_Incom = None
            self.Deferred_Income = None
            self.Total_Liabilities = None
            self.Non_Equity_Reserves = None
            self.Total_Liabilities_Total_Assets = None
            self.Preferred_Stock_Carrying_Valu = None
            self.Redeemable_Preferred_Stock = None
            self.Non_Redeemable_Preferred_Stock = None
            self.Preferred_Stock_issues_for_ESOP = None
            self.ESOP_Guarantees_Preferred_Stock = None
            self.Common_Equity_Tota = None
            self.Common_Stock_Par_Carry_Value = None
            self.Additional_Paid_In_Capital_Capital_Surplus = None
            self.Retained_Earnings = None
            self.ESOP_Debt_Guarantee = None
            self.Cumulative_Translation_Adjustment_Unrealized_For_Exch_Gain = None
            self.Unrealized_Gain_Loss_Marketable_Securities = None
            self.Revaluation_Reserves = None
            self.Other_Appropriated_Reserves = None
            self.Unappropriated_Reserves = None
            self.Treasury_Stock = None
            self.Common_Equity_Total_Assets = None
            self.Total_Shareholders_Equity = None
            self.Total_Shareholders_Equity_Total_Assets = None
            self.Accumulated_Minority_Interest = None
            self.Total_Equity = None
            self.Liabilities_Shareholders_Equity = None
        elif self.fin_st_type == 'cash_flow':
            self.Net_Income_before_Extraordinaries = None
            self.Net_Income_Growth = None
            self.Depreciation_Depletion_Amortization = None
            self.Depreciation_and_Depletion = None
            self.Amortization_of_Intangible_Assets = None
            self.Deferred_Taxes_Investment_Tax_Credit = None
            self.Deferred_Taxes = None
            self.Investment_Tax_Credit = None
            self.Other_Funds = None
            self.Funds_from_Operations = None
            self.Extraordinaries = None
            self.Changes_in_Working_Capital = None
            self.Receivables = None
            self.Inventories = None
            self.Accounts_Payable = None
            self.Income_Taxes_Payable = None
            self.Other_Accruals = None
            self.Other_Assets_Liabilities = None
            self.Net_Operating_Cash_Flow = None
            self.Net_Operating_Cash_Flow_Growth = None
            self.Net_Operating_Cash_Flow_Sales = None

        ind_name_list = self.indicators
        for ind_name, index_num in zip(ind_name_list, self.df.index):
            ind_name = u.get_rid_of_special_characters(ind_name)
            setattr(self, str(ind_name), Indicator(index_num, self.all_periods_real, self.df))

    def __add_empty_columns_to_df_to_equalize_periods_in_all_dataframes_and_update_all_periods_real(self):
        self.columns = list(self.df.columns[:2]) # kolumny index i wskazniki
        all_periods_real = []
        i = 0
        for period in self.all_periods_real:
            if period not in self.df.columns:  # nie wykorzystywany przypadek po zamianie self.all_periods na self.all_periods_real
                self.df[period] = None
                all_periods_real.append(None)
            else:
                all_periods_real.append(self.all_periods_real[i])
                i += 1
            self.columns.append(period)
        self.df = self.df[self.columns]
        self.all_periods_real = all_periods_real

    def __get_and_prepare_df(self):
        self.df = self.__select_all_to_df()
        self.all_periods_month_name = self.df.columns[2:]
        self.sql_columns = self.df.columns
        self.all_periods_real = list([u.convert_date_with_month_name_to_number(c) for c in self.df.columns[2:]])  # conversion month names to numbers
        #self.df.columns = u.get_transform_dates_to_quarters(self.df.columns)
        self.df.columns = list(self.df.columns[:2]) + self.all_periods_real
        self.__add_empty_columns_to_df_to_equalize_periods_in_all_dataframes_and_update_all_periods_real()
        indicators_column = self.df.columns[1]  # aby wykluczyc kolumne ze stringami - powodowala blad w kolejnym wierszu
        self.df.loc[:, self.df.columns != indicators_column] = self.df.loc[:, self.df.columns != indicators_column].applymap(u.transform_val) # zamiana nieliczbowych znakow z liczb
        self.__convert_thousands_to_millions()

    def __select_all_to_df(self):
        sql_select_all = 'SELECT * FROM [wsj].[dbo].[{}]'.format(self.table_name)
        df = pd.read_sql(sql_select_all, con=self.wsj_conn)
        return df

    def __detect_errors(self):
        for col in self.sql_columns:
            if '0001' in col:
                self.faulty_column_detected.status = True
                self.faulty_column_detected.tables.append(self.table_name)
                self.faulty_column_detected.columns.append(col)

    def __convert_thousands_to_millions(self):
        ind_col = self.columns[1]
        print(ind_col)
        if 'Thousands' in ind_col:
            if 'income_statement' in self.table_name:
                specwords = ['margin', 'Margin', 'growth', 'Growth', 'EPS']
                #correct_positions = [Sales Growth, COGS Growth, Gross Income Growth, Gross Profit Margin, SGA Growth, Interest Expense Growth, Pretax Income Growth, Pretax Margin, Net Income Growth, Net Margin, 'EPS (Basic)', 'EPS (Basic) Growth', 'EPS (Diluted)', 'EPS (Diluted) Growth']
            if 'balance_assets' in self.table_name:
                specwords = ['growth', 'Growth', 'Cash & ST Investments / Total Assets', 'Accounts Receivable Turnover', 'Asset Turnover', 'Return On Average Assets']
                # Bad Debt/Doubtful Accounts -- sprawdzic
            if 'balance_liabilities' in self.table_name:

            if 'cash_flow' in self.table_name:

            ind_in_thousands = [x for x in self.df[ind_col] if all(specword not in x for specword in specwords)]
            print(ind_in_thousands)








class Indicator(object):
    def __init__(self, i, periods_list, df):
        self.periods_list = periods_list
        for p in self.periods_list:
            val = df[p][i]
            val = u.transform_val(val)
            setattr(self, p, val)

    def __float__(self, period):
        return getattr(self, period)

    def __get_previous_quarter(self, period):
        period_pos = self.periods_list.index(period)
        prev_period = self.periods_list[period_pos - 1]
        return prev_period

    def val(self, period):
        return getattr(self, period)

    def val_prev(self, period):
        period_pos = self.periods_list.index(period)
        if period_pos >= 1:
            prev_period = self.__get_previous_quarter(self, period)
            res = getattr(self, prev_period)
        else:
            res = None
        return res

    def val_prev_year(self, period):
        period_pos = self.periods_list.index(period)
        if period_pos >= 4:  # checks if 4 periods including present period are available
            prev_year_period = self.periods_list[period_pos - 4]
            res = getattr(self, prev_year_period)
        else:
            res = None
        return res

    def quarter_year_val(self, period):
        # returns sum of last four quarters
        period_pos = self.periods_list.index(period)
        if period_pos >= 3:  # checks if 4 periods including present period are available
            i = 0
            year_sum = 0
            while i < 4:
                year_sum += getattr(self, period)  # add value from period
                period = self.__get_previous_quarter(period)  # get previous period
                i += 1
        else:
            year_sum = None
        return year_sum

    def previous_year_quarter_year_val(self, period):
        # returns sum from four quarters, 4 quarters ago
        period_pos = self.periods_list.index(period)
        if period_pos >= 7:  # checks if 8 periods including present period are available
            i = 0
            prev_year_sum = 0
            while i < 8:
                if i >= 4:
                    prev_year_sum += getattr(self, period)  # add value from period
                    period = self.__get_previous_quarter(period)  # get previous period
                i += 1
        else:
            prev_year_sum = None
        return prev_year_sum


#import time
#import warnings
#def calculate_time(function, loops):
#    start_time = time.time()
#    n = 0
#    while n < loops:
#        function()
#        n += 1
#    end_time = time.time()
#    print(end_time - start_time)
#
#
#def func():
#    u.pandas_df_display_options()
#    warnings.filterwarnings('ignore')
#    fin_st_type = 'income_statement'
#    ticker = 'META'
#    period_type = 'q'
#    ofs = OneFinancialStatement(fin_st_type, ticker, period_type)
#    print(ofs.df)
#    x = ofs.Sales_Revenue.val('2022-03-31')
#    x = ofs.Sales_Revenue.quarter_year_val('2022-03-31')
#    print(x)


#calculate_time(func, 1)

#4.21647047996521


       # -
       # %
       # ticker_tables = create_basic_ticker_table_name(ticker)