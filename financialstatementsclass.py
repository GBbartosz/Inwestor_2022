import pandas as pd

import update
import utilities as u





#class FinancialStatements:
#    def __init__(self):
#        self.isy = IncomeStatementY()
#        self.isq == IncomeStatementQ()


class OneFinancialStatement:
    def __init__(self, fin_st_type, ticker, period_type):
        self.fin_st_type = fin_st_type
        self.ticker = ticker
        self.period_type = period_type
        self.wsj_cursor, self.wsj_conn, self.wsj_engine = u.create_sql_connection('wsj')
        self.table_name = ticker + '_' + fin_st_type + '_' + period_type

        # lista wszystkich okresow
        if self.period_type == 'y':
            all_periods = u.years_generator()
        elif self.period_type == 'q':
            all_periods = u.quarters_generator()
        else:
            print('ivalid period in OneFinancialStatement class')

        # przygotowanie df z okresami kwartalnymi lub rocznymi
        self.df = None
        self.__get_and_prepare_df(all_periods)
        self.__detect_errors()

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

        ind_name_list = self.df.loc[:, 2].tolist()
        for ind_name in ind_name_list:
            ind_name = u.get_rid_of_special_characters(ind_name)
            setattr(self, str(ind_name), self.Indicator(i, years_list, df))

    # od tego zaczac - czy konieczny loop?
    class Indicator(object):
        def __init__(self, i, years_list, df):
            for y in years_list:
                val = df[y][i]
                setattr(self, y, val)

        def __float__(self, year):
            return getattr(self, year)

        def val(self, year):
            return getattr(self, year)

    def __get_and_prepare_df(self, all_periods):
        self.df = self.__select_all_to_df()
        self.df.columns = u.get_transform_dates_to_quarters(self.df.columns)
        self.columns = list(self.df.columns[:2])
        for period in all_periods:
            if period not in self.df.columns:
                self.df[period] = None
            self.columns.append(period)
        self.df = self.df[self.columns]
        self.df = self.df.applymap(u.transform_val2)  # zamiana nieliczbowych znakow z liczb

    def __select_all_to_df(self):
        sql_select_all = 'SELECT * FROM [wsj].[dbo].[{}]'.format(self.table_name)
        df = pd.read_sql(sql_select_all, con=self.wsj_conn)
        return df

    def __repair_column_name(self, old_col_name):
        sql_query = f'''
                    ALTER TABLE [wsj].[dbo].[{self.table_name}]
                    DROP COLUMN [{old_col_name}]
                    '''
        self.wsj_cursor.execute(sql_query)
        ticker_tables = u.create_basic_ticker_table_name(self.ticker)
        update.update(self.ticker, ticker_tables)

    def __detect_errors(self):
        for col in self.columns:
            if '0001' in col:
                print(f'Error column detected for {self.ticker} in {self.table_name}')
                error_detected = True
                self.__repair_column_name(col)
                self.__get_and_prepare_df()


u.pandas_df_display_options()
fin_st_type = 'income_statement'
ticker = 'META'
period_type = 'y'
ofs = OneFinancialStatement(fin_st_type, ticker, period_type)



       # -
       # %
       # ticker_tables = create_basic_ticker_table_name(ticker)