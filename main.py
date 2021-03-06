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
import utilities as u

#tickers_list = ['MMM', 'AOS', 'ABT', 'ABBV', 'ABMD', 'ACN', 'ATVI', 'ADM', 'ADBE', 'AAP', 'AMD', 'AES', 'AFL', 'A', 'APD', 'AKAM', 'ALB', 'ALK', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'ADI', 'ANSS', 'ANTM', 'AON', 'APA', 'AAPL', 'AMAT', 'APTV', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'BKR', 'BLL', 'BAC', 'BBWI', 'BAX', 'BDX', 'BRK.B', 'BBY', 'BIO', 'TECH', 'BIIB', 'BLK', 'BK', 'BA', 'BKNG', 'BWA', 'BXP', 'BSX', 'BMY', 'AVGO', 'BR', 'BRO', 'BF.B', 'CHRW', 'CDNS', 'CZR', 'CPB', 'COF', 'CAH', 'KMX', 'CCL', 'CARR', 'CTLT', 'CAT', 'CBOE', 'CBRE', 'CDW', 'CE', 'CNC', 'CNP', 'CDAY', 'CERN', 'CF', 'CRL', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CTXS', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'CL', 'CMCSA', 'CMA', 'CAG', 'COP', 'ED', 'STZ', 'CPRT', 'GLW', 'CTVA', 'COST', 'CTRA', 'CCI', 'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 'DE', 'DAL', 'XRAY', 'DVN', 'DXCM', 'FANG', 'DLR', 'DFS', 'DISCA', 'DISCK', 'DISH', 'DG', 'DLTR', 'D', 'DPZ', 'DOV', 'DOW', 'DTE', 'DUK', 'DRE', 'DD', 'DXC', 'EMN', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'LLY', 'EMR', 'ENPH', 'ETR', 'EOG', 'EFX', 'EQIX', 'EQR', 'ESS', 'EL', 'ETSY', 'RE', 'EVRG', 'ES', 'EXC', 'EXPE', 'EXPD', 'EXR', 'XOM', 'FFIV', 'FB', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FRC', 'FE', 'FISV', 'FLT', 'FMC', 'F', 'FTNT', 'FTV', 'FBHS', 'FOXA', 'FOX', 'BEN', 'FCX', 'GPS', 'GRMN', 'IT', 'GNRC', 'GD', 'GE', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GL', 'GS', 'HAL', 'HBI', 'HAS', 'HCA', 'PEAK', 'HSIC', 'HES', 'HPE', 'HLT', 'HOLX', 'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUM', 'HBAN', 'HII', 'IBM', 'IEX', 'IDXX', 'INFO', 'ITW', 'ILMN', 'INCY', 'IR', 'INTC', 'ICE', 'IFF', 'IP', 'IPG', 'INTU', 'ISRG', 'IVZ', 'IPGP', 'IQV', 'IRM', 'JBHT', 'JKHY', 'J', 'SJM', 'JNJ', 'JCI', 'JPM', 'JNPR', 'KSU', 'K', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 'LW', 'LVS', 'LEG', 'LDOS', 'LEN', 'LNC', 'LIN', 'LYV', 'LKQ', 'LMT', 'L', 'LOW', 'LUMN', 'LYB', 'MTB', 'MRO', 'MPC', 'MKTX', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MTCH', 'MKC', 'MCD', 'MCK', 'MDT', 'MRK', 'MET', 'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MRNA', 'MHK', 'TAP', 'MDLZ', 'MPWR', 'MNST', 'MCO', 'MS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NWL', 'NEM', 'NWSA', 'NWS', 'NEE', 'NLSN', 'NKE', 'NI', 'NSC', 'NTRS', 'NOC', 'NLOK', 'NCLH', 'NRG', 'NUE', 'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'OKE', 'ORCL', 'OGN', 'OTIS', 'PCAR', 'PKG', 'PH', 'PAYX', 'PAYC', 'PYPL', 'PENN', 'PNR', 'PBCT', 'PEP', 'PKI', 'PFE', 'PM', 'PSX', 'PNW', 'PXD', 'PNC', 'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PTC', 'PEG', 'PSA', 'PHM', 'PVH', 'QRVO', 'QCOM', 'PWR', 'DGX', 'RL', 'RJF', 'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RHI', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL', 'SPGI', 'CRM', 'SBAC', 'SLB', 'STX', 'SEE', 'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SNA', 'SO', 'LUV', 'SWK', 'SBUX', 'STT', 'STE', 'SYK', 'SIVB', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO', 'TPR', 'TGT', 'TEL', 'TDY', 'TFX', 'TER', 'TSLA', 'TXN', 'TXT', 'COO', 'HIG', 'HSY', 'MOS', 'TRV', 'DIS', 'TMO', 'TJX', 'TSCO', 'TT', 'TDG', 'TRMB', 'TFC', 'TWTR', 'TYL', 'TSN', 'USB', 'UDR', 'ULTA', 'UAA', 'UA', 'UNP', 'UAL', 'UPS', 'URI', 'UNH', 'UHS', 'VLO', 'VTR', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VFC', 'VIAC', 'VTRS', 'V', 'VNO', 'VMC', 'WRB', 'GWW', 'WAB', 'WBA', 'WMT', 'WM', 'WAT', 'WEC', 'WFC', 'WELL', 'WST', 'WDC', 'WU', 'WRK', 'WY', 'WHR', 'WMB', 'WLTW', 'WYNN', 'XEL', 'XLNX', 'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZION', 'ZTS', 'AAPL', 'MSFT', 'GOOG', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'TSM', 'FB', 'UNH', 'JNJ', 'V', 'JPM', 'WMT', 'PG', 'XOM', 'BAC', 'HD', 'MA', 'CVX', 'PFE', 'KO', 'BABA', 'ABBV', 'DIS', 'LLY', 'AVGO', 'ASML', 'NVO', 'TM', 'CSCO', 'COST', 'VZ', 'NTES', 'PEP', 'TMO', 'ABT', 'CMCSA', 'ADBE', 'NKE', 'ORCL', 'CRM', 'ACN', 'MRK', 'INTC', 'DHR', 'NVS', 'SHEL', 'WFC', 'BHP', 'UPS', 'QCOM', 'AZN', 'AMD', 'MCD', 'T', 'UNP', 'NFLX', 'NEE', 'TXN', 'PM', 'RY', 'TMUS', 'MS', 'BMY', 'LOW', 'SCHW', 'RTX', 'MDT', 'SPGI', 'LIN', 'TD', 'CVS', 'RIO', 'INTU', 'AXP', 'COP', 'AMGN', 'HON', 'TTE', 'HSBC', 'SAP', 'LMT', 'SONY', 'SNY', 'DE', 'UL', 'PYPL', 'ANTM', 'IBM', 'CHTR', 'C', 'PLD', 'GS', 'AMAT', 'NOW', 'AMT', 'EQNR', 'DEO', 'ISRG', 'BLK', 'HDB', 'TGT', 'BA', 'CAT', 'SBUX', 'EL', 'PTR', 'GSK', 'SYK', 'JD', 'GE', 'VALE', 'MO', 'BUD', 'BTI', 'PBR', 'INFY', 'ZTS', 'MU', 'BP', 'ENB', 'CNI', 'MDLZ', 'BNS', 'CME', 'CB', 'ADP', 'ABNB', 'BX', 'BAM', 'MMM', 'CSX', 'ADI', 'USB', 'BKNG', 'DUK', 'HCA', 'MMC', 'DELL', 'BDX', 'TFC', 'GILD', 'CI', 'CCI', 'PNC', 'ICE', 'MUFG', 'SHOP', 'TJX', 'BMO', 'LRCX', 'NOC', 'FCX', 'CP', 'SO', 'EOG', 'CNQ', 'EW', 'NSC', 'GD', 'TEAM', 'F', 'REGN', 'SHW', 'D', 'ITW', 'PSA', 'WM', 'EQIX', 'CL', 'SNOW', 'FISV', 'ATVI', 'AON', 'BSX', 'PGR', 'SQ', 'ABB', 'GM', 'SNP', 'VRTX', 'IBN', 'MCO', 'WDAY', 'AMOV', 'ETN', 'AMX', 'SCCO', 'NEM', 'PXD', 'UBER', 'RELX', 'FDX', 'CM', 'HUM', 'COF', 'EPD', 'TRP', 'FIS', 'KDP', 'SLB', 'MRNA', 'PANW', 'EMR', 'SE', 'UBS', 'NGG', 'FTNT', 'SNAP', 'MRVL', 'MELI', 'MET', 'OXY', 'NTR', 'MAR', 'PDD', 'TRI', 'LHX', 'BIDU', 'E', 'BCE', 'ILMN', 'APD', 'CNC', 'KLAC', 'VMW', 'SAN', 'AIG', 'DG', 'KHC', 'AEP', 'ECL', 'ROP', 'LFC', 'SRE', 'HMC', 'ITUB', 'SNPS', 'TAK', 'SMFG', 'STLA', 'CTSH', 'ADM', 'NXPI', 'ADSK', 'APH', 'IDXX', 'SU', 'SPG', 'BSBR', 'ORLY', 'DDOG', 'PAYX', 'JCI', 'VOD', 'MPC', 'HSY', 'KMB', 'TEL', 'COIN', 'EXC', 'IQV', 'KR', 'DOW', 'BAX', 'SYY', 'GOLD', 'MNST', 'ABEV', 'CDNS', 'RIVN', 'KMI', 'MCK', 'DXCM', 'TRV', 'LULU', 'WBA', 'RSG', 'BK', 'GIS', 'CRWD', 'STZ', 'WMB', 'MSCI', 'CMG', 'A', 'PRU', 'WIT', 'LYG', 'DLR', 'DVN', 'O', 'CTAS', 'AFL', 'PUK', 'WELL', 'XEL', 'HLT', 'CARR', 'MFC', 'HPQ', 'DD', 'AZO', 'MCHP', 'BBD', 'MSI', 'CTVA', 'LCID', 'NUE', 'RMD', 'ALC', 'PSX', 'CPNG', 'TTD', 'ALGN', 'ING', 'ODFL', 'ANET', 'PH', 'RACE', 'APO', 'TU', 'GPN', 'EC', 'SBAC', 'EA', 'LNG', 'ALL', 'TT', 'VLO', 'TDG', 'BCS', 'WCN', 'AVB', 'YUM', 'BBVA', 'STM', 'PEG', 'TSN', 'CHT', 'AJG', 'EQR', 'OTIS', 'BNTX', 'KKR', 'NU', 'MPLX', 'MFG', 'GLW', 'NET', 'EBAY', 'ZM', 'GFS', 'DLTR', 'ET', 'CVE', 'SIVB', 'FERG', 'LYB', 'ED', 'BBDO', 'MTD', 'BKR', 'TROW', 'ROST', 'ZS', 'IFF', 'DFS', 'HES', 'DASH', 'ROK', 'AMP', 'LVS', 'ARE', 'NIO', 'FAST', 'IMO', 'ABC', 'BIIB', 'HAL', 'PCAR', 'FITB', 'OKE', 'SLF', 'CRH', 'NWG', 'AME', 'VRSK', 'DHI', 'FNV', 'ORAN', 'TLK', 'WEC', 'CBRE', 'FRC', 'ES', 'STT', 'WY', 'AWK', 'PPG', 'BLL', 'VEEV', 'CMI', 'WST', 'APTV', 'CQP', 'NDAQ', 'LI', 'CPRT', 'HRL', 'EFX', 'MKC', 'KEYS', 'MTCH', 'EXPE', 'CERN', 'FMX', 'ANSS', 'NOK', 'RCI', 'TWLO', 'ERIC', 'EXR', 'TWTR', 'MT', 'PHG', 'SWK', 'LEN', 'U', 'WTW', 'SPOT', 'LYV', 'AEM', 'BBY', 'XPEV', 'ON', 'ZBH', 'LH', 'TSCO', 'EIX', 'GWW', 'RBLX', 'DTE', 'MAA', 'TEF', 'OKTA', 'STE', 'FE', 'FANG', 'CHD', 'SIRI', 'PARAA', 'SGEN', 'LUV', 'FOXA', 'VRSN', 'CAJ', 'INVH', 'VMC', 'MLM', 'CDW', 'AEE', 'URI', 'IX', 'CSGP', 'UMC', 'LBRDK', 'ETR', 'HZNP', 'MTB', 'STX', 'FTS', 'ZTO', 'HIG', 'VTR', 'NTRS', 'SQM', 'SWKS', 'PKI', 'CLR', 'PLTR', 'PCG', 'IT', 'ESS', 'K', 'TECK', 'LBRDA', 'PARA', 'DAL', 'MOS', 'FOX', 'HUBS', 'FTV', 'DOV', 'KEY', 'YUMC', 'ZI', 'JBHT']
tickers_list = ['REGN', 'JNJ', 'F', 'INTC', 'AMD', 'DIS', 'T', 'BMW', 'SAP', 'ORCL', 'LIN', 'AAPL',
                'MSFT', 'GOOG', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'FB', 'JNJ', 'V', 'WMT', 'PG', 'XOM', 'HD', 'WMT',
               'MCD', 'KO', 'PEP', 'ADBE', 'BA', 'COST', 'ORCL', 'NFLX', 'PG']
tickers_list = ['A', 'AAPL', 'ABBV', 'ABC', 'ABT', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADSK', 'AEE', 'AEP', 'AFL', 'AIG', 'AJG', 'ALGN', 'ALL', 'AMAT', 'AMD', 'AME', 'AMGN', 'AMP', 'AMT', 'AMZN', 'ANET', 'ANSS', 'ANTM', 'AON', 'APD', 'APH', 'APTV', 'ARE', 'ATVI', 'AVB', 'AVGO', 'AWK', 'AXP', 'AZO', 'BA', 'BAC', 'BAX', 'BBY', 'BDX', 'BIIB', 'BK', 'BKNG', 'BKR', 'BLK', 'BLL', 'BMY', 'BSX', 'C', 'CARR', 'CAT', 'CB', 'CBRE', 'CCI', 'CDNS', 'CDW', 'CERN', 'CHD', 'CHTR', 'CI', 'CL', 'CMCSA', 'CME', 'CMG', 'CMI', 'CNC', 'COF', 'COP', 'COST', 'CPRT', 'CRM', 'CSCO', 'CSX', 'CTAS', 'CTSH', 'CTVA', 'CVS', 'CVX', 'D', 'DAL', 'DD', 'DE', 'DFS', 'DG', 'DHI', 'DHR', 'DIS', 'DLR', 'DLTR', 'DOV', 'DOW', 'DTE', 'DUK', 'DVN', 'DXCM', 'EA', 'EBAY', 'ECL', 'ED', 'EFX', 'EIX', 'EL', 'EMR', 'EOG', 'EQIX', 'EQR', 'ES', 'ESS', 'ETN', 'ETR', 'EW', 'EXC', 'EXPE', 'EXR', 'F', 'FANG', 'FAST', 'FB', 'FCX', 'FDX', 'FE', 'FIS', 'FISV', 'FITB', 'FOX', 'FOXA', 'FRC', 'FTNT', 'FTV', 'GD', 'GE', 'GILD', 'GIS', 'GLW', 'GM', 'GOOG', 'GOOGL', 'GPN', 'GS', 'GWW', 'HAL', 'HCA', 'HD', 'HES', 'HIG', 'HLT', 'HON', 'HPQ', 'HRL', 'HSY', 'HUM', 'IBM', 'ICE', 'IDXX', 'IFF', 'ILMN', 'INTC', 'INTU', 'IQV', 'ISRG', 'IT', 'ITW', 'JBHT', 'JCI', 'JNJ', 'JPM', 'K', 'KEY', 'KEYS', 'KHC', 'KLAC', 'KMB', 'KMI', 'KO', 'KR', 'LEN', 'LH', 'LHX', 'LIN', 'LLY', 'LMT', 'LOW', 'LRCX', 'LUV', 'LVS', 'LYB', 'LYV', 'MA', 'MAA', 'MAR', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDLZ', 'MDT', 'MET', 'MKC', 'MLM', 'MMC', 'MNST', 'MO', 'MOS', 'MPC', 'MRK', 'MRNA', 'MS', 'MSCI', 'MSFT', 'MSI', 'MTB', 'MTCH', 'MTD', 'MU', 'NDAQ', 'NEE', 'NEM', 'NFLX', 'NKE', 'NOC', 'NOW', 'NSC', 'NTRS', 'NUE', 'NVDA', 'NXPI', 'O', 'ODFL', 'OKE', 'ORCL', 'ORLY', 'OTIS', 'OXY', 'PAYX', 'PCAR', 'PEG', 'PEP', 'PFE', 'PG', 'PGR', 'PH', 'PKI', 'PLD', 'PM', 'PNC', 'PPG', 'PRU', 'PSA', 'PSX', 'PXD', 'PYPL', 'QCOM', 'REGN', 'RMD', 'ROK', 'ROP', 'ROST', 'RSG', 'RTX', 'SBAC', 'SBUX', 'SCHW', 'SHW', 'SIVB', 'SLB', 'SNPS', 'SO', 'SPG', 'SPGI', 'SRE', 'STE', 'STT', 'STX', 'STZ', 'SWK', 'SWKS', 'SYK', 'SYY', 'T', 'TDG', 'TEL', 'TFC', 'TGT', 'TJX', 'TMO', 'TMUS', 'TROW', 'TRV', 'TSCO', 'TSLA', 'TSN', 'TT', 'TWTR', 'TXN', 'UNH', 'UNP', 'UPS', 'URI', 'USB', 'V', 'VLO', 'VMC', 'VRSK', 'VRSN', 'VRTX', 'VTR', 'VZ', 'WBA', 'WEC', 'WELL', 'WFC', 'WM', 'WMB', 'WMT', 'WST', 'WY', 'XEL', 'XOM', 'YUM', 'ZBH', 'ZTS', 'AAL', 'AAP', 'ABB', 'ABEV', 'ABMD', 'ABNB', 'AEM', 'AES', 'AIZ', 'AKAM', 'ALB', 'ALC', 'ALK', 'ALLE', 'AMCR', 'AMOV', 'AMX', 'AOS', 'APA', 'APO', 'ASML', 'ATO', 'AVY', 'AZN', 'BABA', 'BAM', 'BBD', 'BBDO', 'BBVA', 'BBWI', 'BCE', 'BCS', 'BEN', 'BF.B', 'BHP', 'BIDU', 'BIO', 'BMO', 'BNS', 'BNTX', 'BP', 'BR', 'BRK.B', 'BRO', 'BSBR', 'BTI', 'BUD', 'BWA', 'BX', 'BXP', 'CAG', 'CAH', 'CAJ', 'CBOE', 'CCL', 'CDAY', 'CE', 'CF', 'CFG', 'CHRW', 'CHT', 'CINF', 'CLR', 'CLX', 'CM', 'CMA', 'CMS', 'CNI', 'CNP', 'CNQ', 'COIN', 'COO', 'CP', 'CPB', 'CPNG', 'CQP', 'CRH', 'CRL', 'CRWD', 'CSGP', 'CTLT', 'CTRA', 'CTXS', 'CVE', 'CZR', 'DASH', 'DDOG', 'DELL', 'DEO', 'DGX', 'DISCA', 'DISCK', 'DISH', 'DPZ', 'DRE', 'DRI', 'DVA', 'DXC', 'E', 'EC', 'EMN', 'ENB', 'ENPH', 'EPD', 'EQNR', 'ERIC', 'ET', 'ETSY', 'EVRG', 'EXPD', 'FBHS', 'FERG', 'FFIV', 'FLT', 'FMC', 'FMX', 'FNV', 'FRT', 'FTS', 'GFS', 'GL', 'GNRC', 'GOLD', 'GPC', 'GPS', 'GRMN', 'GSK', 'HAS', 'HBAN', 'HBI', 'HDB', 'HII', 'HMC', 'HOLX', 'HPE', 'HSBC', 'HSIC', 'HST', 'HUBS', 'HWM', 'HZNP', 'IBN', 'IEX', 'IMO', 'INCY', 'INFO', 'INFY', 'ING', 'INVH', 'IP', 'IPG', 'IPGP', 'IR', 'IRM', 'ITUB', 'IVZ', 'IX', 'J', 'JD', 'JKHY', 'JNPR', 'KDP', 'KIM', 'KKR', 'KMX', 'KSU', 'L', 'LBRDA', 'LBRDK', 'LCID', 'LDOS', 'LEG', 'LFC', 'LI', 'LKQ', 'LNC', 'LNG', 'LNT', 'LULU', 'LUMN', 'LW', 'LYG', 'MAS', 'MELI', 'MFC', 'MFG', 'MGM', 'MHK', 'MKTX', 'MMM', 'MPLX', 'MPWR', 'MRO', 'MRVL', 'MT', 'MUFG', 'NCLH', 'NET', 'NGG', 'NI', 'NIO', 'NLOK', 'NLSN', 'NOK', 'NRG', 'NTAP', 'NTES', 'NTR', 'NU', 'NVO', 'NVR', 'NVS', 'NWG', 'NWL', 'NWS', 'NWSA', 'OGN', 'OKTA', 'OMC', 'ON', 'ORAN', 'PANW', 'PARA', 'PARAA', 'PAYC', 'PBCT', 'PBR', 'PCG', 'PDD', 'PEAK', 'PENN', 'PFG', 'PHG', 'PHM', 'PKG', 'PLTR', 'PNR', 'PNW', 'POOL', 'PPL', 'PTC', 'PTR', 'PUK', 'PVH', 'PWR', 'QRVO', 'RACE', 'RBLX', 'RCI', 'RCL', 'RE', 'REG', 'RELX', 'RF', 'RHI', 'RIO', 'RIVN', 'RJF', 'RL', 'ROL', 'RY', 'SAN', 'SAP', 'SCCO', 'SE', 'SEE', 'SGEN', 'SHEL', 'SHOP', 'SIRI', 'SJM', 'SLF', 'SMFG', 'SNA', 'SNAP', 'SNOW', 'SNP', 'SNY', 'SONY', 'SPOT', 'SQ', 'SQM', 'STLA', 'STM', 'SU', 'SYF', 'TAK', 'TAP', 'TD', 'TDY', 'TEAM', 'TECH', 'TECK', 'TEF', 'TER', 'TFX', 'TLK', 'TM', 'TPR', 'TRI', 'TRMB', 'TRP', 'TSM', 'TTD', 'TTE', 'TTWO', 'TU', 'TWLO', 'TXT', 'TYL', 'U', 'UA', 'UAA', 'UAL', 'UBER', 'UBS', 'UDR', 'UHS', 'UL', 'ULTA', 'UMC', 'VALE', 'VEEV', 'VFC', 'VIAC', 'VMW', 'VNO', 'VOD', 'VTRS', 'WAB', 'WAT', 'WCN', 'WDAY', 'WDC', 'WHR', 'WIT', 'WLTW', 'WRB', 'WRK', 'WTW', 'WU', 'WYNN', 'XLNX', 'XPEV', 'XRAY', 'XYL', 'YUMC', 'ZBRA', 'ZI', 'ZION', 'ZM', 'ZS', 'ZTO', 'MMM']
tickers_list = ['CPNG', 'CQP', 'CRH', 'CRL', 'CRWD', 'CSGP', 'CTLT', 'CTRA', 'CTXS', 'CVE', 'CZR', 'DASH', 'DDOG', 'DELL', 'DEO', 'DGX', 'DISCA', 'DISCK', 'DISH', 'DPZ', 'DRE', 'DRI', 'DVA', 'DXC', 'E', 'EC', 'EMN', 'ENB', 'ENPH', 'EPD', 'EQNR', 'ERIC', 'ET', 'ETSY', 'EVRG', 'EXPD', 'FBHS', 'FERG', 'FFIV', 'FLT', 'FMC', 'FMX', 'FNV', 'FRT', 'FTS', 'GFS', 'GL', 'GNRC', 'GOLD', 'GPC', 'GPS', 'GRMN', 'GSK', 'HAS', 'HBAN', 'HBI', 'HDB', 'HII', 'HMC', 'HOLX', 'HPE', 'HSBC', 'HSIC', 'HST', 'HUBS', 'HWM', 'HZNP', 'IBN', 'IEX', 'IMO', 'INCY', 'INFO', 'INFY', 'ING', 'INVH', 'IP', 'IPG', 'IPGP', 'IR', 'IRM', 'ITUB', 'IVZ', 'IX', 'J', 'JD', 'JKHY', 'JNPR', 'KDP', 'KIM', 'KKR', 'KMX', 'KSU', 'L', 'LBRDA', 'LBRDK', 'LCID', 'LDOS', 'LEG', 'LFC', 'LI', 'LKQ', 'LNC', 'LNG', 'LNT', 'LULU', 'LUMN', 'LW', 'LYG', 'MAS', 'MELI', 'MFC', 'MFG', 'MGM', 'MHK', 'MKTX', 'MMM', 'MPLX', 'MPWR', 'MRO', 'MRVL', 'MT', 'MUFG', 'NCLH', 'NET', 'NGG', 'NI', 'NIO', 'NLOK', 'NLSN', 'NOK', 'NRG', 'NTAP', 'NTES', 'NTR', 'NU', 'NVO', 'NVR', 'NVS', 'NWG', 'NWL', 'NWS', 'NWSA', 'OGN', 'OKTA', 'OMC', 'ON', 'ORAN', 'PANW', 'PARA', 'PARAA', 'PAYC', 'PBCT', 'PBR', 'PCG', 'PDD', 'PEAK', 'PENN', 'PFG', 'PHG', 'PHM', 'PKG', 'PLTR', 'PNR', 'PNW', 'POOL', 'PPL', 'PTC', 'PTR', 'PUK', 'PVH', 'PWR', 'QRVO', 'RACE', 'RBLX', 'RCI', 'RCL', 'RE', 'REG', 'RELX', 'RF', 'RHI', 'RIO', 'RIVN', 'RJF', 'RL', 'ROL', 'RY', 'SAN', 'SAP', 'SCCO', 'SE', 'SEE', 'SGEN', 'SHEL', 'SHOP', 'SIRI', 'SJM', 'SLF', 'SMFG', 'SNA', 'SNAP', 'SNOW', 'SNP', 'SNY', 'SONY', 'SPOT', 'SQ', 'SQM', 'STLA', 'STM', 'SU', 'SYF', 'TAK', 'TAP', 'TD', 'TDY', 'TEAM', 'TECH', 'TECK', 'TEF', 'TER', 'TFX', 'TLK', 'TM', 'TPR', 'TRI', 'TRMB', 'TRP', 'TSM', 'TTD', 'TTE', 'TTWO', 'TU', 'TWLO', 'TXT', 'TYL', 'U', 'UA', 'UAA', 'UAL', 'UBER', 'UBS', 'UDR', 'UHS', 'UL', 'ULTA', 'UMC', 'VALE', 'VEEV', 'VFC', 'VIAC', 'VMW', 'VNO', 'VOD', 'VTRS', 'WAB', 'WAT', 'WCN', 'WDAY', 'WDC', 'WHR', 'WIT', 'WLTW', 'WRB', 'WRK', 'WTW', 'WU', 'WYNN', 'XLNX', 'XPEV', 'XRAY', 'XYL', 'YUMC', 'ZBRA', 'ZI', 'ZION', 'ZM', 'ZS', 'ZTO', 'MMM', 'A', 'AAPL', 'ABBV', 'ABC', 'ABT', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADSK', 'AEE', 'AEP', 'AFL', 'AIG', 'AJG', 'ALGN', 'ALL', 'AMAT', 'AMD', 'AME', 'AMGN', 'AMP', 'AMT', 'AMZN', 'ANET', 'ANSS', 'ANTM', 'AON', 'APD', 'APH', 'APTV', 'ARE', 'ATVI', 'AVB', 'AVGO', 'AWK', 'AXP', 'AZO', 'BA', 'BAC', 'BAX', 'BBY', 'BDX', 'BIIB', 'BK', 'BKNG', 'BKR', 'BLK', 'BLL', 'BMY', 'BSX', 'C', 'CARR', 'CAT', 'CB', 'CBRE', 'CCI', 'CDNS', 'CDW', 'CERN', 'CHD', 'CHTR', 'CI', 'CL', 'CMCSA', 'CME', 'CMG', 'CMI', 'CNC', 'COF', 'COP', 'COST', 'CPRT', 'CRM', 'CSCO', 'CSX', 'CTAS', 'CTSH', 'CTVA', 'CVS', 'CVX', 'D', 'DAL', 'DD', 'DE', 'DFS', 'DG', 'DHI', 'DHR', 'DIS', 'DLR', 'DLTR', 'DOV', 'DOW', 'DTE', 'DUK', 'DVN', 'DXCM', 'EA', 'EBAY', 'ECL', 'ED', 'EFX', 'EIX', 'EL', 'EMR', 'EOG', 'EQIX', 'EQR', 'ES', 'ESS', 'ETN', 'ETR', 'EW', 'EXC', 'EXPE', 'EXR', 'F', 'FANG', 'FAST', 'FB', 'FCX', 'FDX', 'FE', 'FIS', 'FISV', 'FITB', 'FOX', 'FOXA', 'FRC', 'FTNT', 'FTV', 'GD', 'GE', 'GILD', 'GIS', 'GLW', 'GM', 'GOOG', 'GOOGL', 'GPN', 'GS', 'GWW', 'HAL', 'HCA', 'HD', 'HES', 'HIG', 'HLT', 'HON', 'HPQ', 'HRL', 'HSY', 'HUM', 'IBM', 'ICE', 'IDXX', 'IFF', 'ILMN', 'INTC', 'INTU', 'IQV', 'ISRG', 'IT', 'ITW', 'JBHT', 'JCI', 'JNJ', 'JPM', 'K', 'KEY', 'KEYS', 'KHC', 'KLAC', 'KMB', 'KMI', 'KO', 'KR', 'LEN', 'LH', 'LHX', 'LIN', 'LLY', 'LMT', 'LOW', 'LRCX', 'LUV', 'LVS', 'LYB', 'LYV', 'MA', 'MAA', 'MAR', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDLZ', 'MDT', 'MET', 'MKC', 'MLM', 'MMC', 'MNST', 'MO', 'MOS', 'MPC', 'MRK', 'MRNA', 'MS', 'MSCI', 'MSFT', 'MSI', 'MTB', 'MTCH', 'MTD', 'MU', 'NDAQ', 'NEE', 'NEM', 'NFLX', 'NKE', 'NOC', 'NOW', 'NSC', 'NTRS', 'NUE', 'NVDA', 'NXPI', 'O', 'ODFL', 'OKE', 'ORCL', 'ORLY', 'OTIS', 'OXY', 'PAYX', 'PCAR', 'PEG', 'PEP', 'PFE', 'PG', 'PGR', 'PH', 'PKI', 'PLD', 'PM', 'PNC', 'PPG', 'PRU', 'PSA', 'PSX', 'PXD', 'PYPL', 'QCOM', 'REGN', 'RMD', 'ROK', 'ROP', 'ROST', 'RSG', 'RTX', 'SBAC', 'SBUX', 'SCHW', 'SHW', 'SIVB', 'SLB', 'SNPS', 'SO', 'SPG', 'SPGI', 'SRE', 'STE', 'STT', 'STX', 'STZ', 'SWK', 'SWKS', 'SYK', 'SYY', 'T', 'TDG', 'TEL', 'TFC', 'TGT', 'TJX', 'TMO', 'TMUS', 'TROW', 'TRV', 'TSCO', 'TSLA', 'TSN', 'TT', 'TWTR', 'TXN', 'UNH', 'UNP', 'UPS', 'URI', 'USB', 'V', 'VLO', 'VMC', 'VRSK', 'VRSN', 'VRTX', 'VTR', 'VZ', 'WBA', 'WEC', 'WELL', 'WFC', 'WM', 'WMB', 'WMT', 'WST', 'WY', 'XEL', 'XOM', 'YUM', 'ZBH', 'ZTS', 'AAL', 'AAP', 'ABB', 'ABEV', 'ABMD', 'ABNB', 'AEM', 'AES', 'AIZ', 'AKAM', 'ALB', 'ALC', 'ALK', 'ALLE', 'AMCR', 'AMOV', 'AMX', 'AOS', 'APA', 'APO', 'ASML', 'ATO', 'AVY', 'AZN', 'BABA', 'BAM', 'BBD', 'BBDO', 'BBVA', 'BBWI', 'BCE', 'BCS', 'BEN', 'BF.B', 'BHP', 'BIDU', 'BIO', 'BMO', 'BNS', 'BNTX', 'BP', 'BR', 'BRK.B', 'BRO', 'BSBR', 'BTI', 'BUD', 'BWA', 'BX', 'BXP', 'CAG', 'CAH', 'CAJ', 'CBOE', 'CCL', 'CDAY', 'CE', 'CF', 'CFG', 'CHRW', 'CHT', 'CINF', 'CLR', 'CLX', 'CM', 'CMA', 'CMS', 'CNI', 'CNP', 'CNQ', 'COIN', 'COO', 'CP', 'CPB', ]
tickers_list = ['INTL', 'DOV']
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


def analyse_one(ticker):
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 20)
    pd.set_option('display.width', 400)
    ticker = ticker.upper()
    if u.all_tables_available(ticker) is False:
        print(ticker + ' - nie zosta?? sprawdzony. Brak tabel.')
        df, df2 = pd.DataFrame(), pd.DataFrame()
    else:
        isy, isq, bay, baq, bly, blq, cfy, cfq, price, all_years, all_quarters = u.classes_from_sql(ticker)
        df, df2 = analyse.calculate(ticker, isy, isq, bay, baq, bly, blq, cfy, cfq, price, all_years, all_quarters, False)
    return df, df2


def analyse_all():
    print(len(tickers_list))
    start_time = time.time()
    frame_df = []
    frame_df2 = []
    total_number = len(tickers_list)
    total_number_range = range(len(tickers_list))
    for tic, num in zip(tickers_list, total_number_range):
        print(tic)
        print('{0} out of {1}'.format(num, total_number))
        df, df2 = analyse_one(tic)
        frame_df.append(df)
        frame_df2.append(df2)


    total_df = pd.concat(frame_df, ignore_index=True, sort=False)
    total_df2 = pd.concat(frame_df2, ignore_index=True, sort=False)
    print(total_df)
    print(total_df2)
    # to excel
    #excel_path = 'C:\\Users\\Bartek\\Desktop\\myfile.xlsx'
    #wb = openpyxl.load_workbook(excel_path)
    #writer = pd.ExcelWriter(excel_path, engine='openpyxl')
    #writer.wb = wb
    #writer.sheets = dict((ws.title, ws) for ws in wb.worksheets)
    #sheets_list = wb.sheetnames
    #print(sheets_list)
    #total_df.to_excel(excel_writer=writer, sheet_name=sheets_list[0])
    #total_df2.to_excel(excel_writer=writer, sheet_name=sheets_list[1])
    #writer.save()

    excel_path = 'C:\\Users\\Bartek\\Desktop\\myfile.xlsx'
    wb = xlwt.Workbook(excel_path)
    ws1 = wb.add_sheet('Main indicators')
    ws2 = wb.add_sheet('Advanced indicators')
    wb = openpyxl.Workbook()
    ws = wb.active
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        writer.book = wb
        writer.sheets = dict((ws.title, ws) for ws in wb.worksheets)
        total_df.to_excel(excel_writer=writer, sheet_name='Main indicators')
        total_df2.to_excel(excel_writer=writer, sheet_name='Advanced indicators')
        writer.save()
    end_time = time.time()
    print(end_time - start_time)


def update_one(ticker):
    ticker = ticker.upper()
    ticker_tables = u.create_basic_ticker_table_name(ticker)
    update.update(ticker, ticker_tables)


def update_all():
    unsuccessfuls = []
    total_number = len(tickers_list)
    print(total_number)
    total_number_range = range(len(tickers_list))
    for tic, num in zip(tickers_list, total_number_range):
        print(tic)
        print('{0} out of {1}'.format(num, total_number))
        ticker_tables = u.create_basic_ticker_table_name(tic)
        update.update(tic, ticker_tables)
        if update.unsuccessful is not None:
            unsuccessfuls.append(update.unsuccessful)
    print(unsuccessfuls)


def update_global():
    updateglobal.calculateglobal(tickers_list)


def update_indeks():
    updateindeks.update_indeks()


root = Tk()
root.title = 'Panel inwestora'
root.geometry('600x600')

information = tk.StringVar()
information.set('Wprowad?? ticker')
entry_txt = tk.StringVar()
entry_txt.set('')

label1 = Label(root, text='Wpisz ticker sp????ki').pack()
ticker = Entry(root, textvariable=entry_txt, width=60, borderwidth=10, justify=CENTER).pack()
entry_txt.trace('w', find_ticker)
label2 = Label(root, textvariable=information).pack()
frame1 = Frame(root).pack()

button1 = Button(root, text='Analizuj', height=2, width=15, bg='SkyBlue2', activebackground='red3',
                 command=lambda: analyse_one(entry_txt.get()), state=DISABLED)
button2 = Button(root, text='Aktualizuj', height=2, width=15, bg='SkyBlue2', activebackground='red3',
                 command=lambda: update_one(entry_txt.get()), state=DISABLED)
button3 = Button(frame1, text='Analizuj wszystkie', height=2, width=20, bg='SkyBlue2', activebackground='red3',
                 command=lambda: analyse_all())
button4 = Button(frame1, text='Aktualizuj wszystkie', height=2, width=20, bg='SkyBlue2', activebackground='red3',
                 command=lambda: update_all())
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

button5 = Button(root, text='Wyj??cie', height=2, width=10, bg='SkyBlue2', activebackground='red3', command=root.quit)\
    .pack(side=BOTTOM)


mainloop()
