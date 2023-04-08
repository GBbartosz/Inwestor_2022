import pandas as pd
import requests
from bs4 import BeautifulSoup
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
        self.sql_table = sql_table_name
        self.df = None

    def change_df_date_format(self):
        mnn = month_name_to_num()
        self.df['Date'] = self.df['Date'].apply(lambda x: x[-4:] + '-' + mnn[x[:x.find(' ')]] + '-' + x[x.find(' ')+1:x.find(',')])


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

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    cursor, wsj_conn, engine = u.create_sql_connection()
    sql_all_tables = u.get_all_tables(cursor)

    isms = [ISM('us_pmi', 'US_ISM_Manufacturing_PMI'),
            ISM('us_ism_non_manufacturing_index', 'US_ISM_Services_PMI')]
    for ism in isms:
        ism.df = download_data(ism.link)
        ism.change_df_date_format()
        ism.df = ism.df.sort_values(['Date'], ascending=True)
        ism.df = ism.df.reset_index(drop=True)
        print(ism.df)
        if ism.name in sql_all_tables:
            pass
        else:
            #ism.df.to_sql(ism.sql_table, con=engine, if_exists='replace', index=False)
            pass


pmi_module()



