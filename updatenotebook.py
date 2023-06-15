import utilities as u
import datetime

# select *
# into wsj.dbo.tmp
# from wsj.dbo.update_notebook
# where ticker = null
# drop table wsj.dbo.update_notebook
# select *
# into wsj.dbo.update_notebook
# from wsj.dbo.tmp
# drop table wsj.dbo.tmp


class UpdateNotebook:
    def __init__(self, update_notebook_name):
        self.update_notebook_name = update_notebook_name
        self.today = str(datetime.datetime.today().date())
        cursor, wsj_conn, engine = u.create_sql_connection('wsj')
        self.cursor = cursor

    def confirm_updated(self, ticker):
        # potwierdzenie przeprowadzenia aktualizacji
        # nawet gdy nie udanej
        ticker = ticker.upper()
        sql_query = f'''UPDATE wsj.dbo.{self.update_notebook_name}
                        SET last_update_date = \'{self.today}\' 
                        WHERE ticker = \'{ticker}\'
                        '''
        self.cursor.execute(sql_query)


def update_notebook(tickers_l, update_notebook_name):
    # skrocenie listy pozostalych do aktualizacji
    # eliminuje tickery ktorych aktualizacje juz podjeto tego sameog dnia
    # nalezy recznie utworzyc pusta tablice przy tworzeniu nowego notatnika do skladowania danych
    tickers_l = [x.upper() for x in tickers_l]
    cursor, wsj_conn, engine = u.create_sql_connection('wsj')
    sql_query = f'select ticker, last_update_date from wsj.dbo.{update_notebook_name}'
    cursor.execute(sql_query)
    res = cursor.fetchall()
    update_notebook_dict = {x[0]: x[1] for x in res}
    today = str(datetime.datetime.today().date())
    remaining_tickers = []
    for t in tickers_l:
        if t in update_notebook_dict.keys():
            if today != update_notebook_dict[t]:
                remaining_tickers.append(t)
        else:
            sql_query = f'INSERT INTO wsj.dbo.{update_notebook_name} (ticker) VALUES (\'{t}\')'
            cursor.execute(sql_query)
            remaining_tickers.append(t)
    return remaining_tickers


# create table wsj.dbo.analyse_notebook
# 	(
# 	ticker char(6),
# 	last_update_date date
# 	)

