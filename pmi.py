import pandas as pd
import requests
import utilities as u

# PMI = (P1 * 1) + (P2 * 0.5) + (P3 * 0)
# Where:
# P1 = percentage of answers reporting an improvement
# P2 = percentage of answers reporting no change
# P3 = percentage of answers reporting a deterioration


def month_name_to_num():
    mnn = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12'
    }
    return mnn


class ISM:
    def __init__(self, name, sql_table_name):
        self.name = name
        self.link = r'https://ycharts.com/indicators/{}'.format(name)
        self.sql_table_name = sql_table_name
        self.sql_table = 'wsj.dbo.{}'.format(sql_table_name)
        self.df = None

    def change_df_date_format(self):
        mnn = month_name_to_num()
        self.df['Date'] = self.df['Date']\
            .apply(lambda x: x[-4:] + '-' + mnn[x[:x.find(' ')]] + '-' + x[x.find(' ')+1:x.find(',')])

    def sort_df(self):
        self.df = self.df.sort_values(['Date'], ascending=True)
        return self.df

    def df_to_sql(self, sql_all_tables, cursor, wsj_conn, engine):
        if self.df is None:
            print('df doesn\'t exists')
        else:
            if self.sql_table_name in sql_all_tables:
                sql_query = pd.read_sql_query('SELECT * FROM {}'.format(self.sql_table), wsj_conn)
                sql_df = pd.DataFrame(sql_query)
                self.df = self.df.merge(sql_df.drop_duplicates(),
                                        on=[self.df.columns[0], self.df.columns[1]], how='left', indicator=True)
                self.df = self.df[self.df['_merge'] == 'left_only'][['Date', 'Value']].reset_index(drop=True)
                if len(self.df.index) > 0:
                    self.df = self.sort_df()
                    for i in self.df.index:
                        sql_update_query = '''INSERT INTO {} 
                                            VALUES ('{}', {})'''\
                                            .format(self.sql_table, self.df.iloc[i, 0], self.df.iloc[i, 1])
                        cursor.execute(sql_update_query)
                    cursor.commit()
            else:
                self.df.to_sql(self.sql_table_name, con=engine, if_exists='replace', index=False)


def pmi_module():

    def download_data(link):
        nonlocal headers
        resp = requests.get(link, headers=headers).text
        resp_l = pd.read_html(resp)
        df = pd.DataFrame()
        for i in range(len(resp_l)):
            if isinstance(resp_l[i], pd.DataFrame):
                if 'Date' in resp_l[i].columns and 'Value' in resp_l[i].columns:
                    if df is None:
                        df = resp_l[i]
                    else:
                        df = pd.concat([df, resp_l[i]], ignore_index=True)
        return df

    u.pandas_df_display_options()
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    cursor, wsj_conn, engine = u.create_sql_connection()
    sql_all_tables = u.get_all_tables(cursor)

    isms = [ISM('us_pmi', 'US_ISM_Manufacturing_PMI'),
            ISM('us_ism_non_manufacturing_index', 'US_ISM_Services_PMI')]

    for ism in isms:
        ism.df = download_data(ism.link)
        ism.change_df_date_format()
        ism.sort_df()
        ism.df_to_sql(sql_all_tables, cursor, wsj_conn, engine)
