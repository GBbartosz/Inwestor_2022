import pandas as pd
import utilities as u
import warnings

import time
import dash
import plotly as plt
import plotly.graph_objects as go

from tickerclass import Ticker
from plotlyfig import PlotlyFig


def ticker_indicator_dd_update(chosen_val, ddchosen_obj_actual, dd_obj_other):

    def create_ticker_obj(main_chart_fig, ddchosen_obj_tic, ddchosen_obj_ind, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):

        def get_indicators_add_trace(main_chart_fig, ddchosen_obj_ind, tic):
            for i in ddchosen_obj_ind.elements:
                indicator_name = i + '_y'
                x = tic.dates_y
                y = getattr(tic, indicator_name).values
                n = tic.name + '_' + i
                xs.append(x)
                ys.append(y)
                names.append(n)
                main_chart_fig.add_trace(go.Scatter(x=x, y=y, name=n))

        for t in ddchosen_obj_tic.elements:
            tic = Ticker(t, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            tic.set_df_year()
            tic.create_indicators()
            get_indicators_add_trace(main_chart_fig, ddchosen_obj_ind, tic)

    main_chart_fig = go.Figure()
    ddchosen_obj_actual.update(chosen_val)
    if chosen_val:
        if dd_obj_other.not_empty():
            xs = []
            ys = []
            names = []
            if ddchosen_obj_actual.name == 'ticker':
                create_ticker_obj(main_chart_fig, ddchosen_obj_actual, dd_obj_other, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor,
                                  wsja_conn, wsja_engine)
            else:
                create_ticker_obj(main_chart_fig, dd_obj_other, ddchosen_obj_actual, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor,
                                  wsja_conn, wsja_engine)
    return main_chart_fig


def all_options_for_dropdowns(tickers_list):
    global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine

    def options_for_dropdown(mylist):
        newlist = []
        for i in mylist:
            tmp = {'label': i, 'value': i}
            newlist.append(tmp)
        return newlist

    tic = Ticker(tickers_list[1], wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
    tic.set_df_year()
    tic.create_indicators()
    tickers_dropdown_l = options_for_dropdown(tickers_list)
    indicators_dropdown_l = options_for_dropdown(tic.indicators_names_l)
    return tickers_dropdown_l, indicators_dropdown_l


class DDChosen:
    def __init__(self, name):
        self.elements = []
        self.name = name

    def update(self, new_element):
        if new_element in self.elements:
            self.elements.remove(new_element)
        else:
            self.elements = new_element

    def not_empty(self):
        if len(self.elements) > 0:
            res = True
        else:
            res = False
        return res


def dashboard():

    def main_page(tickers_list):
        dd_chosen_ticker = DDChosen('ticker')
        dd_chosen_indicator = DDChosen('indicator')
        tickers_dropdown_l, indicators_dropdown_l = all_options_for_dropdowns(tickers_list)

        layout_main_page = dash.html.Div([
            dash.html.Div(
                dash.html.H1(id='h1_ticker_name',
                             children='None ticker selected',
                             style={'width': '1200px', 'height': '40px'})
            ),
            dash.html.Div(children=[
                dash.dcc.Dropdown(id='ticker_dd',
                                  options=tickers_dropdown_l,
                                  placeholder='Select ticker',
                                  multi=True,
                                  style={'width': '480px', 'height': '40px'}),
                dash.dcc.Dropdown(id='indicator_dd',
                                  options=indicators_dropdown_l,
                                  placeholder='Select indicator',
                                  multi=True,
                                  style={'width': '480px', 'height': '40px'})],
                style={'display': 'inline-block'}
            ),
            dash.dcc.Graph(id='main_chart', figure=go.Figure())
        ])
        dash.register_page('main_page', path='/', layout=layout_main_page)

        @app.callback(
            dash.Output(component_id='h1_ticker_name', component_property='children'),
            dash.Output(component_id='main_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='ticker_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_ticker(chosen_ticker):
            global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal dd_chosen_ticker, dd_chosen_indicator

            main_chart_fig = ticker_indicator_dd_update(chosen_ticker, dd_chosen_ticker, dd_chosen_indicator)
            if dd_chosen_ticker.not_empty() is False:
                title_h1_ticker = 'None ticker selected'
            else:
                title_h1_ticker = dd_chosen_ticker.elements
            return title_h1_ticker, main_chart_fig

        @app.callback(
            dash.Output(component_id='main_chart', component_property='figure'),
            dash.Input(component_id='indicator_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_indicator(chosen_indicator):
            global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal dd_chosen_ticker, dd_chosen_indicator

            main_chart_fig = ticker_indicator_dd_update(chosen_indicator, dd_chosen_indicator, dd_chosen_ticker)
            return main_chart_fig

    tickers_list = ['GOOGL', 'META', 'NFLX']  # dodac jako argument
    app = dash.Dash(__name__, pages_folder="", use_pages=True)
    main_page(tickers_list)
    app.run_server(debug=True)



    #indicators_dict = get_indicators_dict(wsj_conn)
    #sql_analysis_tables = get_all_analysis_tables(cursor)
    #adb = AnalysisDatabase(tickers_list, indicators_dict, wsj_conn)
    #print(adb.META.tables.year)
    #print(adb.META.get_df(wsj_conn))

start_time = time.time()
u.pandas_df_display_options()
warnings.filterwarnings('ignore')
wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
wsja_cursor, wsja_conn, wsja_engine = u.create_sql_connection('wsja')
dashboard()
#analyse_chart()
end_time = time.time()
print(end_time - start_time)


