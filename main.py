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

    # przez notatnik moze nie byc wrzucane do excela wyniki gdy byly wczesniej aktualizowane
    analyse_notebook_name = 'analyse_notebook'
    analyse_notebook = upnot.UpdateNotebook(analyse_notebook_name)
    remaining_tickers = upnot.update_notebook(tickers_list, analyse_notebook_name)

    frame_df_y = []
    frame_df_q = []
    #frame_df2 = []
    total_number, total_number_range = u.get_total_number_and_range_of_all_tickers(remaining_tickers)
    for tic, num in zip(remaining_tickers, total_number_range):
        print(f'{tic} - {num} out of {total_number}')
        #df_y, df_q, df2 = analyse_one(tic, False)
        df_y, df_q = analyse_one(tic, False)
        frame_df_y.append(df_y)
        frame_df_q.append(df_q)
        #frame_df2.append(df2)
        analyse_notebook.confirm_updated(tic)

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
    update_notebook_name = 'update_notebook'
    update_notebook = upnot.UpdateNotebook(update_notebook_name)
    remaining_tickers = upnot.update_notebook(tickers_list, update_notebook_name)
    #remaining_tickers = tickers_list

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

    def investigate_table(cursor, tabl):
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
        invalid_cols = investigate_table(cursor, tabl)
        if invalid_cols:
            tic_name = get_ticker_name_from_table_name(tabl)
            invalid_tickers.add(tic_name)
            drop_invalid_column(cursor, tabl, invalid_cols)
    cursor.commit()

    export_invalid_columns_report_to_csv(invalid_tickers)

if __name__ == '__main__':
    warnings.filterwarnings('ignore')

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
