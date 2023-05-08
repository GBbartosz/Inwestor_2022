import pandas as pd
import utilities as u
import warnings

import time
import dash
import plotly as plt
import plotly.graph_objects as go

from tickerclass import Ticker


def analyse_chart(tic):

    def get_main_chart_dd_buttons(indicators_names_l):

        def get_indicators_names_d(indicators_names_l):
            mydict = {}
            for i, n in zip(indicators_names_l, list(range(len(indicators_names_l)))):
                mydict[i] = n
            return mydict

        def get_true_false_l(elenum, num):
            l = num * [False]
            l[elenum] = True
            return l

        bl = []
        indicators_names_d = get_indicators_names_d(indicators_names_l)
        number_of_elements = len(indicators_names_d.keys())
        for i in indicators_names_d.keys():
            position_of_element = indicators_names_d[i]
            true_false_l = get_true_false_l(position_of_element, number_of_elements)
            print(true_false_l)
            ele = {'label': i,
                   'method': 'update',
                   'args': [{'visible': true_false_l},
                            {'title': i}]}
            bl.append(ele)
        return bl

    if tic is not None:
        main_chart_dd_buttons = get_main_chart_dd_buttons(tic.indicators_names_l)

        fig = go.Figure()
        x = tic.dates_y
        for i in tic.indicators_names_l:
            ia = i + '_y'
            y = getattr(tic, ia).values
            fig.add_trace(go.Scatter(x=x, y=y))

        fig.update_layout({
            'updatemenus': [{
                'type': 'dropdown',
                'showactive': True,
                'active': 0,
                'buttons': main_chart_dd_buttons}]
        })

        return fig


def tickers_for_dropdown(tickers_l):
    ddl = []
    for tic in tickers_l:
        ddd = {'label': tic, 'value': tic}
        ddl.append(ddd)
    return ddl


def dashboard():
    ticker_name = None

    u.pandas_df_display_options()
    tickers_list = ['GOOGL', 'META', 'NFLX']                                                   #dodac jako argument

    tic = Ticker(tickers_list[1], wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
    tic.set_df_year()
    tic.set_df_quarter()
    tic.set_income_statment_df_year()
    tic.set_income_statment_df_quarter()
    tickers_dropdown_l = tickers_for_dropdown(tickers_list)

    if ticker_name is None:
        ticker_name = ' '

    app = dash.Dash(__name__, pages_folder="", use_pages=True)


    ### main page ###

    # layout_main_page = get_layout_main_page(ticker_name, tickers_dropdown_l, app)
    layout_main_page = dash.html.Div([
                dash.html.Div(
                    dash.html.H1(id='h1_ticker_name',
                                 children=ticker_name,
                                 style={'width': '120px', 'height': '30px'})
                ),
                dash.dcc.Dropdown(id='ticker_dd',
                                  options=tickers_dropdown_l,
                                  style={'width': '120px', 'height': '30px'}),
                dash.dcc.Graph(id='main_chart')
            ])
    dash.register_page('main_page', path='/', layout=layout_main_page)

    #@app.callback(
    #    dash.Output(component_id='h1_ticker_name', component_property='children'),
    #    dash.Input(component_id='ticker_dd', component_property='value')
    #)
    #def update_h1_ticker(ticker_name):
    #    return ticker_name

    @app.callback(
        dash.Output(component_id='main_chart', component_property='figure'),
        dash.Input(component_id='ticker_dd', component_property='value')
    )
    def update_main_chart(chosen_ticker):
        global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
        fig = go.Figure()
        if chosen_ticker:
            tic = Ticker(chosen_ticker, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            tic.set_df_year()
            tic.create_indicators()

            fig = analyse_chart(tic)
        return fig

    app.run_server(debug=True)



    #indicators_dict = get_indicators_dict(wsj_conn)
    #sql_analysis_tables = get_all_analysis_tables(cursor)
    #adb = AnalysisDatabase(tickers_list, indicators_dict, wsj_conn)
    #print(adb.META.tables.year)
    #print(adb.META.get_df(wsj_conn))






start_time = time.time()
warnings.filterwarnings('ignore')
wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
wsja_cursor, wsja_conn, wsja_engine = u.create_sql_connection('wsja')
dashboard()
#analyse_chart()
end_time = time.time()
print(end_time - start_time)


