import dash
import pandas as pd
import plotly.graph_objects as go
import time
import warnings

from tickerclass import Ticker
import utilities as u


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


class ButtonChosenPeriod:
    def __init__(self):
        self.val = 'year'

    def update(self, click_num):
        if (click_num / 2).is_integer():
            self.val = 'year'
        else:
            self.val = 'quarter'

    def condition_return_val(self, val_y, val_q):
        if self.val == 'year':
            res = val_y
        else:
            res = val_q
        return res


class CurrentChooiceForFinStatement:
    def __init__(self):
        self.ticker_name = None
        self.period = 'year'
        self.b_chosen_period = None

    def update(self, dd_chosen_ticker, b_chosen_period):
        self.b_chosen_period = b_chosen_period
        if len(dd_chosen_ticker.elements) == 1:
            self.ticker_name = dd_chosen_ticker.elements[-1]

    def get_df(self, chosen_statement=None):
        global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine

        # single albo multi wybor w dropdown
        if chosen_statement is not None and isinstance(chosen_statement, str) is False:
            chosen_statement = chosen_statement[0]

        if self.ticker_name is None:
            df = pd.DataFrame()
        else:
            tic = Ticker(self.ticker_name, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            if chosen_statement is None:
                self.b_chosen_period.condition_return_val(tic.set_is_df_y, tic.set_is_df_q)()
                df = self.b_chosen_period.condition_return_val(tic.is_df_y, tic.is_df_q)
            else:
                get_chosen_fin_st(chosen_statement,
                                  self.b_chosen_period.condition_return_val(tic.set_is_df_y, tic.set_is_df_q),
                                  self.b_chosen_period.condition_return_val(tic.set_ba_df_y, tic.set_ba_df_q),
                                  self.b_chosen_period.condition_return_val(tic.set_bl_df_y, tic.set_bl_df_q),
                                  self.b_chosen_period.condition_return_val(tic.set_cf_df_y, tic.set_cf_df_q))()
                df = get_chosen_fin_st(chosen_statement,
                                       self.b_chosen_period.condition_return_val(tic.is_df_y, tic.is_df_q),
                                       self.b_chosen_period.condition_return_val(tic.ba_df_y, tic.ba_df_q),
                                       self.b_chosen_period.condition_return_val(tic.bl_df_y, tic.bl_df_q),
                                       self.b_chosen_period.condition_return_val(tic.cf_df_y, tic.cf_df_q))
        return df


def get_chosen_fin_st(fin_st, x1, x2, x3, x4):
    res = None
    if fin_st == 'income_statement':
        res = x1
    elif fin_st == 'balance_assets':
        res = x2
    elif fin_st == 'balance_liabilities':
        res = x3
    elif fin_st == 'cash_flow':
        res = x4
    return res


def convert_df_to_datatable(df):
    dt = None
    if df.empty is False:
        dt = df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
    return dt


def ticker_indicator_period_update(chosen_val, ddchosen_obj_actual, dd_obj_other, b_chosen_period):

    def create_ticker_obj(main_chart_fig, ddchosen_obj_tic, ddchosen_obj_ind, b_chosen_period,
                          wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):

        def get_indicators_add_trace(main_chart_fig, ddchosen_obj_ind, tic):
            for i in ddchosen_obj_ind.elements:
                indicator_period = b_chosen_period.condition_return_val('_y', '_q')
                indicator_name = i + indicator_period
                x = tic.dates_y
                y = getattr(tic, indicator_name).values
                n = tic.name + '_' + i
                xs.append(x)
                ys.append(y)
                names.append(n)
                main_chart_fig.add_trace(go.Scatter(x=x, y=y, name=n))

        for t in ddchosen_obj_tic.elements:
            tic = Ticker(t, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            set_period_type = b_chosen_period.condition_return_val(tic.set_df_year, tic.set_df_quarter)
            set_period_type()
            tic.create_indicators()
            get_indicators_add_trace(main_chart_fig, ddchosen_obj_ind, tic)

    main_chart_fig = go.Figure()

    # gdy aktywowano przycisk
    if chosen_val in ['year', 'quarter']:
        ddchosen_obj_actual.name = 'ticker'
    else:
        ddchosen_obj_actual.update(chosen_val)

    if chosen_val:
        if dd_obj_other.not_empty():
            xs = []
            ys = []
            names = []
            if ddchosen_obj_actual.name == 'ticker':
                create_ticker_obj(main_chart_fig, ddchosen_obj_actual, dd_obj_other, b_chosen_period, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor,
                                  wsja_conn, wsja_engine)
            else:
                create_ticker_obj(main_chart_fig, dd_obj_other, ddchosen_obj_actual, b_chosen_period, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor,
                                  wsja_conn, wsja_engine)
    return main_chart_fig


def options_for_dropdown(mylist):
    newlist = []
    for i in mylist:
        tmp = {'label': i, 'value': i}
        newlist.append(tmp)
    return newlist


def all_options_for_dropdowns(tickers_list):
    global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine

    tic = Ticker(tickers_list[0], wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
    tic.set_df_year()
    tic.create_indicators()
    tickers_dropdown_l = options_for_dropdown(tickers_list)
    indicators_dropdown_l = options_for_dropdown(tic.indicators_names_l)
    return tickers_dropdown_l, indicators_dropdown_l


def navigation_panel(current_page):

    def create_button(txt, page):
        button = dash.dcc.Link(dash.html.Button(txt), href='/' + page)
        return button

    pages = {'Main': '', 'Financial statements': 'fin_st'}
    buttons = []
    for page_name in pages.keys():
        if pages[page_name] != current_page:
            buttons.append(create_button(page_name, pages[page_name]))
    buttons_layout = dash.html.Div(children=buttons)
    return buttons_layout


def dashboard():

    def main_page():
        global tickers_l, dd_chosen_ticker, dd_chosen_indicator
        page_id = ''
        b_chosen_period = ButtonChosenPeriod()
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
                                  style={'width': '480px', 'height': '40px'}),
                dash.html.Button(children='year',
                                 id='year_quarter_button',
                                 n_clicks=0)],
                style={'display': 'inline-block'}
            ),
            dash.dcc.Graph(id='main_chart', figure=go.Figure()),
            navigation_panel(page_id)
            #dash.dcc.Link(
            #    dash.html.Button('Navigate to "page-2"'),
            #    href='/page2')
        ])
        dash.register_page(page_id, path='/', layout=layout_main_page)

        @app.callback(
            dash.Output(component_id='h1_ticker_name', component_property='children'),
            dash.Output(component_id='main_chart', component_property='figure', allow_duplicate=True),
            #dash.Output(component_id='fin_st_ticker_dd', component_property='options'),
            dash.Input(component_id='ticker_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_ticker(chosen_ticker):
            global dd_chosen_ticker, dd_chosen_indicator, curr_choice_for_fin_st, fin_st_tickers_dropdown_l, \
                wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal b_chosen_period

            main_chart_fig = ticker_indicator_period_update(chosen_ticker, dd_chosen_ticker, dd_chosen_indicator,
                                                            b_chosen_period)
            if dd_chosen_ticker.not_empty() is False:
                title_h1_ticker = 'None ticker selected'
            else:
                title_h1_ticker = dd_chosen_ticker.elements
                fin_st_tickers_dropdown_l_update, indicators_dropdown_l = all_options_for_dropdowns(dd_chosen_ticker.elements)
                fin_st_tickers_dropdown_l = fin_st_tickers_dropdown_l_update
            curr_choice_for_fin_st.update(dd_chosen_ticker, b_chosen_period)
            return title_h1_ticker, main_chart_fig

        @app.callback(
            dash.Output(component_id='main_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indicator_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_indicator(chosen_indicator):
            global dd_chosen_ticker, dd_chosen_indicator, \
                wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine

            main_chart_fig = ticker_indicator_period_update(chosen_indicator, dd_chosen_indicator, dd_chosen_ticker,
                                                            b_chosen_period)
            return main_chart_fig

        @app.callback(
            dash.Output(component_id='year_quarter_button', component_property='children'),
            dash.Output(component_id='main_chart', component_property='figure'),
            dash.Input(component_id='year_quarter_button', component_property='n_clicks'),
            prevent_initial_call=True
        )
        def year_quarter_button_action(click_num):
            global dd_chosen_ticker, dd_chosen_indicator, curr_choice_for_fin_st, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal b_chosen_period

            b_chosen_period.update(click_num)
            main_chart_fig = ticker_indicator_period_update(b_chosen_period.val, dd_chosen_ticker, dd_chosen_indicator,
                                                            b_chosen_period)
            curr_choice_for_fin_st.update(dd_chosen_ticker, b_chosen_period)
            return b_chosen_period.val, main_chart_fig

    def financial_statements_page():
        global tickers_l, dd_chosen_ticker, dd_chosen_indicator, curr_choice_for_fin_st, fin_st_tickers_dropdown_l
        page_id = 'fin_st'
        financial_statements_l = ['income_statement', 'balance_assets', 'balance_liabilities', 'cash_flow']
        fin_statement_dd_l = options_for_dropdown(financial_statements_l)
        data_table = convert_df_to_datatable(curr_choice_for_fin_st.get_df())



        layout_financial_statements_page = dash.html.Div([
            #dash.dcc.Location(id='url', refresh=True),
            dash.html.H1(id='h1_ticker_name',
                         children='None ticker selected',
                         style={'width': '1200px', 'height': '40px'}),
            dash.html.Div(children=[
                dash.dcc.Dropdown(id='fin_st_dd',
                                  options=fin_statement_dd_l,
                                  placeholder='Select financial statement',
                                  style={'width': '480px', 'height': '40px'})]),
            dash.dash_table.DataTable(id='fin_st_table', data=data_table),
            navigation_panel(page_id)])

        dash.register_page(page_id, path='/fin_st', layout=layout_financial_statements_page)

        @app.callback(
            dash.Output(component_id='fin_st_table', component_property='data'),
            dash.Input(component_id='fin_st_dd', component_property='value')
        )
        def update_fin_st_data_table(chosen_fin_st):
            global curr_choice_for_fin_st
            if chosen_fin_st:
                df = curr_choice_for_fin_st.get_df(chosen_fin_st)
                dt = convert_df_to_datatable(df)
            else:
                df = curr_choice_for_fin_st.get_df()
                dt = convert_df_to_datatable(df)
            dt = dt[0]  # konieczne [0] nie moze byc w funkcji
            return dt


    app = dash.Dash(__name__, pages_folder="", use_pages=True)
    financial_statements_page()
    main_page()
    app.run_server(debug=True)



    #indicators_dict = get_indicators_dict(wsj_conn)
    #sql_analysis_tables = get_all_analysis_tables(cursor)
    #adb = AnalysisDatabase(tickers_list, indicators_dict, wsj_conn)
    #print(adb.META.tables.year)
    #print(adb.META.get_df(wsj_conn))

start_time = time.time()
u.pandas_df_display_options()
warnings.filterwarnings('ignore')

tickers_list = ['GOOGL', 'META', 'NFLX']  # dodac jako argument
fin_st_tickers_dropdown_l = []
dd_chosen_ticker = DDChosen('ticker')
dd_chosen_indicator = DDChosen('indicator')
curr_choice_for_fin_st = CurrentChooiceForFinStatement()
wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
wsja_cursor, wsja_conn, wsja_engine = u.create_sql_connection('wsja')
dashboard()
#analyse_chart()
end_time = time.time()
print(end_time - start_time)

