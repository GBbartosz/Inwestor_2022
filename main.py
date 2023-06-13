import datetime
import openpyxl
import pandas as pd
import pyodbc
import time
from tkinter import *
import tkinter as tk
import xlwt

import analyse
import update
import updateglobal
import updateindeks
import updatenotebook as upnot
import utilities as u
import warnings


def create_or_replace_indicators_sql_table(ticker, dfs):
    cursor, wsj_conn, engine = u.create_sql_connection('wsja')
    analysed_tables = ['year', 'quarter', 'global']
    analysed_tables = [f'analysis_{ticker}_{p}' for p in analysed_tables]
    for analysed_table, df in zip(analysed_tables, dfs):
        if df.empty is False:
            df.to_sql(analysed_table, con=engine, if_exists='replace', index=False)


#def create_excel_file(total_df_y, total_df_q, total_df2, file_name):
def create_excel_file(total_df_y, total_df_q, file_name):
    excel_path = r'C:\Users\barto\Desktop\Inwestor_2023\{}.xlsx'.format(file_name)
    wb = xlwt.Workbook(excel_path)
    ws1 = wb.add_sheet('Main indicators y')
    ws2 = wb.add_sheet('Main indicators q')
    ws3 = wb.add_sheet('Advanced indicators y')
    wb = openpyxl.Workbook()
    ws = wb.active
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        writer.book = wb
        writer.sheets.update(dict((ws.title, ws) for ws in wb.worksheets))
        total_df_y.to_excel(excel_writer=writer, sheet_name='Main indicators y')
        total_df_q.to_excel(excel_writer=writer, sheet_name='Main indicators q')
        #total_df2.to_excel(excel_writer=writer, sheet_name='Advanced indicators y')
        writer.save()


def find_ticker(*args):
    information.set(entry_txt.get())
    if entry_txt.get().upper() in tickers_list:
        information.set('Ticker found')
        button1.config(state='normal')
        button2.config(state='normal')
    else:
        information.set('Ticker not found')
        button1.config(state=DISABLED)
        button2.config(state=DISABLED)


def analyse_one(ticker, only_one):
    u.pandas_df_display_options()
    ticker = ticker.upper()
    if u.all_tables_available(ticker) is False:
        print(ticker + ' - nie został sprawdzony. Brak tabel.')
        df_y, df_q, df2 = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    else:
        isy, isq, bay, baq, bly, blq, cfy, cfq, price_y, price_q, all_years, all_quarters = u.classes_from_sql(ticker)
        #df_y, df_q, df2 = analyse.calculate(ticker, isy, isq, bay, baq, bly, blq, cfy, cfq, price_y, price_q, all_years, all_quarters, False)
        df_y, df_q = analyse.calculate(ticker, isy, isq, bay, baq, bly, blq, cfy, cfq, price_y, price_q, all_years, all_quarters, False)
        #create_or_replace_indicators_sql_table(ticker, [df_y, df_q, df2])
        create_or_replace_indicators_sql_table(ticker, [df_y, df_q])

    # czy analiza tylko 1 spolki
    if only_one is True:
        print(df_y)
        print(df_q)
        #print(df2)
        f_name = 'analiza_{}'.format(ticker)
        #create_excel_file(df_y, df_q, df2, f_name)
        create_excel_file(df_y, df_q, f_name)
    #return df_y, df_q, df2
    return df_y, df_q


def analyse_all(tickers_list):
    start_time = time.time()
    frame_df_y = []
    frame_df_q = []
    #frame_df2 = []
    total_number, total_number_range = u.get_total_number_and_range_of_all_tickers(tickers_list)
    for tic, num in zip(tickers_list, total_number_range):
        print(f'{tic} - {num} out of {total_number}')
        #df_y, df_q, df2 = analyse_one(tic, False)
        df_y, df_q = analyse_one(tic, False)
        frame_df_y.append(df_y)
        frame_df_q.append(df_q)
        #frame_df2.append(df2)

    total_df_y = pd.concat(frame_df_y, ignore_index=True, sort=False)
    total_df_q = pd.concat(frame_df_q, ignore_index=True, sort=False)
    #total_df2 = pd.concat(frame_df2, ignore_index=True, sort=False)
    print(total_df_y)
    print(total_df_q)
    #print(total_df2)

    #create_excel_file(total_df_y, total_df_q, total_df2, 'analiza_all')
    create_excel_file(total_df_y, total_df_q, 'analiza_all')
    end_time = time.time()
    print(end_time - start_time)


def update_one(ticker):
    ticker = ticker.upper()
    ticker_tables = u.create_basic_ticker_table_name(ticker)
    update.update(ticker, ticker_tables)


def update_all(tickers_list):
    unsuccessfuls = []
    update_notebook = upnot.UpdateNotebook()

    #remaining_tickers = upnot.update_notebook(tickers_list)
    remaining_tickers = tickers_list

    total_number, total_number_range = u.get_total_number_and_range_of_all_tickers(remaining_tickers)
    for tic, num in zip(remaining_tickers, total_number_range):
        print(tic)
        print('{0} out of {1}'.format(num, total_number))
        ticker_tables = u.create_basic_ticker_table_name(tic)
        update.update(tic, ticker_tables)
        if update.unsuccessful is not None:
            unsuccessfuls.append(update.unsuccessful)
        update_notebook.confirm_updated(tic)
    print(unsuccessfuls)


def update_global():
    updateglobal.calculateglobal(tickers_list)


def update_indeks():
    updateindeks.update_indeks()


def find_and_delete_invalid_column_names_in_all_tables():
    # wyszukuje '1-Jan-0001', Unnamed: 5

    def get_ticker_name_from_table_name(table_name):
        floorpos = table_name.find('_')
        ticker_name = table_name[:floorpos]
        return ticker_name

    def investigate_table(cursor):
        query = f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = \'{tabl}\' AND TABLE_SCHEMA=\'dbo\'
                """
        cursor.execute(query)
        invalid_columns = [x[0] for x in cursor.fetchall() if x[0] in ['1-Jan-0001', 'Unnamed: 5']]
        return invalid_columns

    def drop_invalid_column(cursor, tabl, invalid_columns):
        for invalid_column in invalid_columns:
            query = f'ALTER TABLE wsj.dbo.{tabl} DROP COLUMN [{invalid_column}]'
            cursor.execute(query)

    def export_invalid_columns_report_to_csv(invalid_tickers):
        if invalid_tickers:
            df = pd.DataFrame({'invalid_tickers': list(invalid_tickers)})
            today = str(datetime.datetime.today()).replace('-', '_').replace(' ', '_').replace(':', '_').replace('.', '_')
            f_name = f'invalid_columns_in_tables_{today}'
            df.to_csv(f'C:\\Users\\barto\\Desktop\\Inwestor_2023\\invalid_columns_in_tables\\{f_name}.csv')

    cursor, wsj_conn, engine = u.create_sql_connection('wsj')
    sql_table_list = u.get_all_tables(cursor)
    invalid_tickers = set()
    for tabl in sql_table_list:
        invalid_cols = investigate_table(cursor)
        if invalid_cols:
            tic_name = get_ticker_name_from_table_name(tabl)
            invalid_tickers.add(tic_name)
            drop_invalid_column(cursor, tabl, invalid_cols)
    cursor.commit()

    export_invalid_columns_report_to_csv(invalid_tickers)

if __name__ == '__main__':
    warnings.filterwarnings('ignore')
        #tickers_list = ['REGN', 'JNJ', 'F', 'INTC', 'AMD', 'DIS', 'T', 'BMW', 'SAP', 'ORCL', 'LIN', 'AAPL',
    #                'MSFT', 'GOOG', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'FB', 'JNJ', 'V', 'WMT', 'PG', 'XOM', 'HD', 'WMT',
    #               'MCD', 'KO', 'PEP', 'ADBE', 'BA', 'COST', 'ORCL', 'NFLX', 'PG']
    #tickers_list = ['CDR', 'GT', 'CON', 'A', 'AAPL', 'ABBV', 'ABC', 'ABT', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADSK', 'AEE', 'AEP', 'AFL', 'AIG', 'AJG', 'ALGN', 'ALL', 'AMAT', 'AMD', 'AME', 'AMGN', 'AMP', 'AMT', 'AMZN', 'ANET', 'ANSS', 'ANTM', 'AON', 'APD', 'APH', 'APTV', 'ARE', 'ATVI', 'AVB', 'AVGO', 'AWK', 'AXP', 'AZO', 'BA', 'BAC', 'BAX', 'BBY', 'BDX', 'BIIB', 'BK', 'BKNG', 'BKR', 'BLK', 'BLL', 'BMY', 'BSX', 'C', 'CARR', 'CAT', 'CB', 'CBRE', 'CCI', 'CDNS', 'CDW', 'CERN', 'CHD', 'CHTR', 'CI', 'CL', 'CMCSA', 'CME', 'CMG', 'CMI', 'CNC', 'COF', 'COP', 'COST', 'CPRT', 'CRM', 'CSCO', 'CSX', 'CTAS', 'CTSH', 'CTVA', 'CVS', 'CVX', 'D', 'DAL', 'DD', 'DE', 'DFS', 'DG', 'DHI', 'DHR', 'DIS', 'DLR', 'DLTR', 'DOV', 'DOW', 'DTE', 'DUK', 'DVN', 'DXCM', 'EA', 'EBAY', 'ECL', 'ED', 'EFX', 'EIX', 'EL', 'EMR', 'EOG', 'EQIX', 'EQR', 'ES', 'ESS', 'ETN', 'ETR', 'EW', 'EXC', 'EXPE', 'EXR', 'F', 'FANG', 'FAST', 'FB', 'FCX', 'FDX', 'FE', 'FIS', 'FISV', 'FITB', 'FOX', 'FOXA', 'FRC', 'FTNT', 'FTV', 'GD', 'GE', 'GILD', 'GIS', 'GLW', 'GM', 'GOOG', 'GOOGL', 'GPN', 'GS', 'GWW', 'HAL', 'HCA', 'HD', 'HES', 'HIG', 'HLT', 'HON', 'HPQ', 'HRL', 'HSY', 'HUM', 'IBM', 'ICE', 'IDXX', 'IFF', 'ILMN', 'INTC', 'INTU', 'IQV', 'ISRG', 'IT', 'ITW', 'JBHT', 'JCI', 'JNJ', 'JPM', 'K', 'KEY', 'KEYS', 'KHC', 'KLAC', 'KMB', 'KMI', 'KO', 'KR', 'LEN', 'LH', 'LHX', 'LIN', 'LLY', 'LMT', 'LOW', 'LRCX', 'LUV', 'LVS', 'LYB', 'LYV', 'MA', 'MAA', 'MAR', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDLZ', 'MDT', 'MET', 'MKC', 'MLM', 'MMC', 'MNST', 'MO', 'MOS', 'MPC', 'MRK', 'MRNA', 'MS', 'MSCI', 'MSFT', 'MSI', 'MTB', 'MTCH', 'MTD', 'MU', 'NDAQ', 'NEE', 'NEM', 'NFLX', 'NKE', 'NOC', 'NOW', 'NSC', 'NTRS', 'NUE', 'NVDA', 'NXPI', 'O', 'ODFL', 'OKE', 'ORCL', 'ORLY', 'OTIS', 'OXY', 'PAYX', 'PCAR', 'PEG', 'PEP', 'PFE', 'PG', 'PGR', 'PH', 'PKI', 'PLD', 'PM', 'PNC', 'PPG', 'PRU', 'PSA', 'PSX', 'PXD', 'PYPL', 'QCOM', 'REGN', 'RMD', 'ROK', 'ROP', 'ROST', 'RSG', 'RTX', 'SBAC', 'SBUX', 'SCHW', 'SHW', 'SIVB', 'SLB', 'SNPS', 'SO', 'SPG', 'SPGI', 'SRE', 'STE', 'STT', 'STX', 'STZ', 'SWK', 'SWKS', 'SYK', 'SYY', 'T', 'TDG', 'TEL', 'TFC', 'TGT', 'TJX', 'TMO', 'TMUS', 'TROW', 'TRV', 'TSCO', 'TSLA', 'TSN', 'TT', 'TWTR', 'TXN', 'UNH', 'UNP', 'UPS', 'URI', 'USB', 'V', 'VLO', 'VMC', 'VRSK', 'VRSN', 'VRTX', 'VTR', 'VZ', 'WBA', 'WEC', 'WELL', 'WFC', 'WM', 'WMB', 'WMT', 'WST', 'WY', 'XEL', 'XOM', 'YUM', 'ZBH', 'ZTS', 'AAL', 'AAP', 'ABB', 'ABEV', 'ABMD', 'ABNB', 'AEM', 'AES', 'AIZ', 'AKAM', 'ALB', 'ALC', 'ALK', 'ALLE', 'AMCR', 'AMOV', 'AMX', 'AOS', 'APA', 'APO', 'ASML', 'ATO', 'AVY', 'AZN', 'BABA', 'BAM', 'BBD', 'BBDO', 'BBVA', 'BBWI', 'BCE', 'BCS', 'BEN', 'BF.B', 'BHP', 'BIDU', 'BIO', 'BMO', 'BNS', 'BNTX', 'BP', 'BR', 'BRK.B', 'BRO', 'BSBR', 'BTI', 'BUD', 'BWA', 'BX', 'BXP', 'CAG', 'CAH', 'CAJ', 'CBOE', 'CCL', 'CDAY', 'CE', 'CF', 'CFG', 'CHRW', 'CHT', 'CINF', 'CLR', 'CLX', 'CM', 'CMA', 'CMS', 'CNI', 'CNP', 'CNQ', 'COIN', 'COO', 'CP', 'CPB', 'CPNG', 'CQP', 'CRH', 'CRL', 'CRWD', 'CSGP', 'CTLT', 'CTRA', 'CTXS', 'CVE', 'CZR', 'DASH', 'DDOG', 'DELL', 'DEO', 'DGX', 'DISCA', 'DISCK', 'DISH', 'DPZ', 'DRE', 'DRI', 'DVA', 'DXC', 'E', 'EC', 'EMN', 'ENB', 'ENPH', 'EPD', 'EQNR', 'ERIC', 'ET', 'ETSY', 'EVRG', 'EXPD', 'FBHS', 'FERG', 'FFIV', 'FLT', 'FMC', 'FMX', 'FNV', 'FRT', 'FTS', 'GFS', 'GL', 'GNRC', 'GOLD', 'GPC', 'GPS', 'GRMN', 'GSK', 'HAS', 'HBAN', 'HBI', 'HDB', 'HII', 'HMC', 'HOLX', 'HPE', 'HSBC', 'HSIC', 'HST', 'HUBS', 'HWM', 'HZNP', 'IBN', 'IEX', 'IMO', 'INCY', 'INFO', 'INFY', 'ING', 'INVH', 'IP', 'IPG', 'IPGP', 'IR', 'IRM', 'ITUB', 'IVZ', 'IX', 'J', 'JD', 'JKHY', 'JNPR', 'KDP', 'KIM', 'KKR', 'KMX', 'KSU', 'L', 'LBRDA', 'LBRDK', 'LCID', 'LDOS', 'LEG', 'LFC', 'LI', 'LKQ', 'LNC', 'LNG', 'LNT', 'LULU', 'LUMN', 'LW', 'LYG', 'MAS', 'MELI', 'MFC', 'MFG', 'MGM', 'MHK', 'MKTX', 'MMM', 'MPLX', 'MPWR', 'MRO', 'MRVL', 'MT', 'MUFG', 'NCLH', 'NET', 'NGG', 'NI', 'NIO', 'NLOK', 'NLSN', 'NOK', 'NRG', 'NTAP', 'NTES', 'NTR', 'NU', 'NVO', 'NVR', 'NVS', 'NWG', 'NWL', 'NWS', 'NWSA', 'OGN', 'OKTA', 'OMC', 'ON', 'ORAN', 'PANW', 'PARA', 'PARAA', 'PAYC', 'PBCT', 'PBR', 'PCG', 'PDD', 'PEAK', 'PENN', 'PFG', 'PHG', 'PHM', 'PKG', 'PLTR', 'PNR', 'PNW', 'POOL', 'PPL', 'PTC', 'PTR', 'PUK', 'PVH', 'PWR', 'QRVO', 'RACE', 'RBLX', 'RCI', 'RCL', 'RE', 'REG', 'RELX', 'RF', 'RHI', 'RIO', 'RIVN', 'RJF', 'RL', 'ROL', 'RY', 'SAN', 'SAP', 'SCCO', 'SE', 'SEE', 'SGEN', 'SHEL', 'SHOP', 'SIRI', 'SJM', 'SLF', 'SMFG', 'SNA', 'SNAP', 'SNOW', 'SNP', 'SNY', 'SONY', 'SPOT', 'SQ', 'SQM', 'STLA', 'STM', 'SU', 'SYF', 'TAK', 'TAP', 'TD', 'TDY', 'TEAM', 'TECH', 'TECK', 'TEF', 'TER', 'TFX', 'TLK', 'TM', 'TPR', 'TRI', 'TRMB', 'TRP', 'TSM', 'TTD', 'TTE', 'TTWO', 'TU', 'TWLO', 'TXT', 'TYL', 'U', 'UA', 'UAA', 'UAL', 'UBER', 'UBS', 'UDR', 'UHS', 'UL', 'ULTA', 'UMC', 'VALE', 'VEEV', 'VFC', 'VIAC', 'VMW', 'VNO', 'VOD', 'VTRS', 'WAB', 'WAT', 'WCN', 'WDAY', 'WDC', 'WHR', 'WIT', 'WLTW', 'WRB', 'WRK', 'WTW', 'WU', 'WYNN', 'XLNX', 'XPEV', 'XRAY', 'XYL', 'YUMC', 'ZBRA', 'ZI', 'ZION', 'ZM', 'ZS', 'ZTO', 'MMM']
    #tickers_list = ['CPNG', 'CQP', 'CRH', 'CRL', 'CRWD', 'CSGP', 'CTLT', 'CTRA', 'CTXS', 'CVE', 'CZR', 'DASH', 'DDOG', 'DELL', 'DEO', 'DGX', 'DISCA', 'DISCK', 'DISH', 'DPZ', 'DRE', 'DRI', 'DVA', 'DXC', 'E', 'EC', 'EMN', 'ENB', 'ENPH', 'EPD', 'EQNR', 'ERIC', 'ET', 'ETSY', 'EVRG', 'EXPD', 'FBHS', 'FERG', 'FFIV', 'FLT', 'FMC', 'FMX', 'FNV', 'FRT', 'FTS', 'GFS', 'GL', 'GNRC', 'GOLD', 'GPC', 'GPS', 'GRMN', 'GSK', 'HAS', 'HBAN', 'HBI', 'HDB', 'HII', 'HMC', 'HOLX', 'HPE', 'HSBC', 'HSIC', 'HST', 'HUBS', 'HWM', 'HZNP', 'IBN', 'IEX', 'IMO', 'INCY', 'INFO', 'INFY', 'ING', 'INVH', 'IP', 'IPG', 'IPGP', 'IR', 'IRM', 'ITUB', 'IVZ', 'IX', 'J', 'JD', 'JKHY', 'JNPR', 'KDP', 'KIM', 'KKR', 'KMX', 'KSU', 'L', 'LBRDA', 'LBRDK', 'LCID', 'LDOS', 'LEG', 'LFC', 'LI', 'LKQ', 'LNC', 'LNG', 'LNT', 'LULU', 'LUMN', 'LW', 'LYG', 'MAS', 'MELI', 'MFC', 'MFG', 'MGM', 'MHK', 'MKTX', 'MMM', 'MPLX', 'MPWR', 'MRO', 'MRVL', 'MT', 'MUFG', 'NCLH', 'NET', 'NGG', 'NI', 'NIO', 'NLOK', 'NLSN', 'NOK', 'NRG', 'NTAP', 'NTES', 'NTR', 'NU', 'NVO', 'NVR', 'NVS', 'NWG', 'NWL', 'NWS', 'NWSA', 'OGN', 'OKTA', 'OMC', 'ON', 'ORAN', 'PANW', 'PARA', 'PARAA', 'PAYC', 'PBCT', 'PBR', 'PCG', 'PDD', 'PEAK', 'PENN', 'PFG', 'PHG', 'PHM', 'PKG', 'PLTR', 'PNR', 'PNW', 'POOL', 'PPL', 'PTC', 'PTR', 'PUK', 'PVH', 'PWR', 'QRVO', 'RACE', 'RBLX', 'RCI', 'RCL', 'RE', 'REG', 'RELX', 'RF', 'RHI', 'RIO', 'RIVN', 'RJF', 'RL', 'ROL', 'RY', 'SAN', 'SAP', 'SCCO', 'SE', 'SEE', 'SGEN', 'SHEL', 'SHOP', 'SIRI', 'SJM', 'SLF', 'SMFG', 'SNA', 'SNAP', 'SNOW', 'SNP', 'SNY', 'SONY', 'SPOT', 'SQ', 'SQM', 'STLA', 'STM', 'SU', 'SYF', 'TAK', 'TAP', 'TD', 'TDY', 'TEAM', 'TECH', 'TECK', 'TEF', 'TER', 'TFX', 'TLK', 'TM', 'TPR', 'TRI', 'TRMB', 'TRP', 'TSM', 'TTD', 'TTE', 'TTWO', 'TU', 'TWLO', 'TXT', 'TYL', 'U', 'UA', 'UAA', 'UAL', 'UBER', 'UBS', 'UDR', 'UHS', 'UL', 'ULTA', 'UMC', 'VALE', 'VEEV', 'VFC', 'VIAC', 'VMW', 'VNO', 'VOD', 'VTRS', 'WAB', 'WAT', 'WCN', 'WDAY', 'WDC', 'WHR', 'WIT', 'WLTW', 'WRB', 'WRK', 'WTW', 'WU', 'WYNN', 'XLNX', 'XPEV', 'XRAY', 'XYL', 'YUMC', 'ZBRA', 'ZI', 'ZION', 'ZM', 'ZS', 'ZTO', 'MMM', 'A', 'AAPL', 'ABBV', 'ABC', 'ABT', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADSK', 'AEE', 'AEP', 'AFL', 'AIG', 'AJG', 'ALGN', 'ALL', 'AMAT', 'AMD', 'AME', 'AMGN', 'AMP', 'AMT', 'AMZN', 'ANET', 'ANSS', 'ANTM', 'AON', 'APD', 'APH', 'APTV', 'ARE', 'ATVI', 'AVB', 'AVGO', 'AWK', 'AXP', 'AZO', 'BA', 'BAC', 'BAX', 'BBY', 'BDX', 'BIIB', 'BK', 'BKNG', 'BKR', 'BLK', 'BLL', 'BMY', 'BSX', 'C', 'CARR', 'CAT', 'CB', 'CBRE', 'CCI', 'CDNS', 'CDW', 'CERN', 'CHD', 'CHTR', 'CI', 'CL', 'CMCSA', 'CME', 'CMG', 'CMI', 'CNC', 'COF', 'COP', 'COST', 'CPRT', 'CRM', 'CSCO', 'CSX', 'CTAS', 'CTSH', 'CTVA', 'CVS', 'CVX', 'D', 'DAL', 'DD', 'DE', 'DFS', 'DG', 'DHI', 'DHR', 'DIS', 'DLR', 'DLTR', 'DOV', 'DOW', 'DTE', 'DUK', 'DVN', 'DXCM', 'EA', 'EBAY', 'ECL', 'ED', 'EFX', 'EIX', 'EL', 'EMR', 'EOG', 'EQIX', 'EQR', 'ES', 'ESS', 'ETN', 'ETR', 'EW', 'EXC', 'EXPE', 'EXR', 'F', 'FANG', 'FAST', 'FB', 'FCX', 'FDX', 'FE', 'FIS', 'FISV', 'FITB', 'FOX', 'FOXA', 'FRC', 'FTNT', 'FTV', 'GD', 'GE', 'GILD', 'GIS', 'GLW', 'GM', 'GOOG', 'GOOGL', 'GPN', 'GS', 'GWW', 'HAL', 'HCA', 'HD', 'HES', 'HIG', 'HLT', 'HON', 'HPQ', 'HRL', 'HSY', 'HUM', 'IBM', 'ICE', 'IDXX', 'IFF', 'ILMN', 'INTC', 'INTU', 'IQV', 'ISRG', 'IT', 'ITW', 'JBHT', 'JCI', 'JNJ', 'JPM', 'K', 'KEY', 'KEYS', 'KHC', 'KLAC', 'KMB', 'KMI', 'KO', 'KR', 'LEN', 'LH', 'LHX', 'LIN', 'LLY', 'LMT', 'LOW', 'LRCX', 'LUV', 'LVS', 'LYB', 'LYV', 'MA', 'MAA', 'MAR', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDLZ', 'MDT', 'MET', 'MKC', 'MLM', 'MMC', 'MNST', 'MO', 'MOS', 'MPC', 'MRK', 'MRNA', 'MS', 'MSCI', 'MSFT', 'MSI', 'MTB', 'MTCH', 'MTD', 'MU', 'NDAQ', 'NEE', 'NEM', 'NFLX', 'NKE', 'NOC', 'NOW', 'NSC', 'NTRS', 'NUE', 'NVDA', 'NXPI', 'O', 'ODFL', 'OKE', 'ORCL', 'ORLY', 'OTIS', 'OXY', 'PAYX', 'PCAR', 'PEG', 'PEP', 'PFE', 'PG', 'PGR', 'PH', 'PKI', 'PLD', 'PM', 'PNC', 'PPG', 'PRU', 'PSA', 'PSX', 'PXD', 'PYPL', 'QCOM', 'REGN', 'RMD', 'ROK', 'ROP', 'ROST', 'RSG', 'RTX', 'SBAC', 'SBUX', 'SCHW', 'SHW', 'SIVB', 'SLB', 'SNPS', 'SO', 'SPG', 'SPGI', 'SRE', 'STE', 'STT', 'STX', 'STZ', 'SWK', 'SWKS', 'SYK', 'SYY', 'T', 'TDG', 'TEL', 'TFC', 'TGT', 'TJX', 'TMO', 'TMUS', 'TROW', 'TRV', 'TSCO', 'TSLA', 'TSN', 'TT', 'TWTR', 'TXN', 'UNH', 'UNP', 'UPS', 'URI', 'USB', 'V', 'VLO', 'VMC', 'VRSK', 'VRSN', 'VRTX', 'VTR', 'VZ', 'WBA', 'WEC', 'WELL', 'WFC', 'WM', 'WMB', 'WMT', 'WST', 'WY', 'XEL', 'XOM', 'YUM', 'ZBH', 'ZTS', 'AAL', 'AAP', 'ABB', 'ABEV', 'ABMD', 'ABNB', 'AEM', 'AES', 'AIZ', 'AKAM', 'ALB', 'ALC', 'ALK', 'ALLE', 'AMCR', 'AMOV', 'AMX', 'AOS', 'APA', 'APO', 'ASML', 'ATO', 'AVY', 'AZN', 'BABA', 'BAM', 'BBD', 'BBDO', 'BBVA', 'BBWI', 'BCE', 'BCS', 'BEN', 'BF.B', 'BHP', 'BIDU', 'BIO', 'BMO', 'BNS', 'BNTX', 'BP', 'BR', 'BRK.B', 'BRO', 'BSBR', 'BTI', 'BUD', 'BWA', 'BX', 'BXP', 'CAG', 'CAH', 'CAJ', 'CBOE', 'CCL', 'CDAY', 'CE', 'CF', 'CFG', 'CHRW', 'CHT', 'CINF', 'CLR', 'CLX', 'CM', 'CMA', 'CMS', 'CNI', 'CNP', 'CNQ', 'COIN', 'COO', 'CP', 'CPB', ]
    #tickers_list = ['GOOGL', 'META', 'NFLX']

    tickers_df = pd.read_csv(r'C:\Users\barto\Desktop\Inwestor_2023\source_data\tickers_list.csv')
    valid_tickers_df = tickers_df[tickers_df['valid'] == 1]
    tickers_list = valid_tickers_df['ticker'].tolist()
    print(tickers_list)
    find_and_delete_invalid_column_names_in_all_tables()

    root = Tk()
    root.title = 'Panel inwestora'
    root.geometry('600x600')

    information = tk.StringVar()
    information.set('Wprowadź ticker')
    entry_txt = tk.StringVar()
    entry_txt.set('')

    label1 = Label(root, text='Wpisz ticker spółki').pack()
    ticker = Entry(root, textvariable=entry_txt, width=60, borderwidth=10, justify=CENTER).pack()
    entry_txt.trace('w', find_ticker)
    label2 = Label(root, textvariable=information).pack()
    frame1 = Frame(root).pack()

    button1 = Button(root, text='Analizuj', height=2, width=15, bg='SkyBlue2', activebackground='red3',
                     command=lambda: analyse_one(entry_txt.get(), True), state=DISABLED)
    button2 = Button(root, text='Aktualizuj', height=2, width=15, bg='SkyBlue2', activebackground='red3',
                     command=lambda: update_one(entry_txt.get()), state=DISABLED)
    button3 = Button(frame1, text='Analizuj wszystkie', height=2, width=20, bg='SkyBlue2', activebackground='red3',
                     command=lambda: analyse_all(tickers_list))
    button4 = Button(frame1, text='Aktualizuj wszystkie', height=2, width=20, bg='SkyBlue2', activebackground='red3',
                     command=lambda: update_all(tickers_list))
    button6 = Button(frame1, text='Aktualizuj Global', height=2, width=20, bg='SkyBlue2', activebackground='red3',
                     command=lambda: update_global())
    button7 = Button(frame1, text='Aktualizuj Indeksy', height=2, width=20, bg='SkyBlue2', activebackground='red3',
                     command=lambda: update_indeks())

    button1.pack()
    button2.pack()
    button3.pack()
    button4.pack()
    button6.pack()
    button7.pack()

    button5 = Button(root, text='Wyjście', height=2, width=10, bg='SkyBlue2', activebackground='red3', command=root.quit)\
        .pack(side=BOTTOM)


    mainloop()
