import dash
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

    tic = Ticker(tickers_list[1], wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
    tic.set_df_year()
    tic.create_indicators()
    tickers_dropdown_l = options_for_dropdown(tickers_list)
    indicators_dropdown_l = options_for_dropdown(tic.indicators_names_l)
    return tickers_dropdown_l, indicators_dropdown_l


def navigation_panel():
    pass


def dashboard():

    def main_page(tickers_list):
        dd_chosen_ticker = DDChosen('ticker')
        dd_chosen_indicator = DDChosen('indicator')
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
            dash.dcc.Link(
                dash.html.Button('Navigate to "page-2"'),
                href='/page2')
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
            nonlocal dd_chosen_ticker, dd_chosen_indicator, b_chosen_period

            main_chart_fig = ticker_indicator_period_update(chosen_ticker, dd_chosen_ticker, dd_chosen_indicator,
                                                            b_chosen_period)
            if dd_chosen_ticker.not_empty() is False:
                title_h1_ticker = 'None ticker selected'
            else:
                title_h1_ticker = dd_chosen_ticker.elements
            return title_h1_ticker, main_chart_fig

        @app.callback(
            dash.Output(component_id='main_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indicator_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_indicator(chosen_indicator):
            global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal dd_chosen_ticker, dd_chosen_indicator

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
            global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal dd_chosen_ticker, dd_chosen_indicator, b_chosen_period

            b_chosen_period.update(click_num)
            main_chart_fig = ticker_indicator_period_update(b_chosen_period.val, dd_chosen_ticker, dd_chosen_indicator,
                                                            b_chosen_period)
            return b_chosen_period.val, main_chart_fig

    def financial_statements_page(tickers_list, ticker_name):
        tickers_dropdown_l, indicators_dropdown_l = all_options_for_dropdowns(tickers_list)
        financial_statements_l = ['income_statement', 'balance_assets', 'balance_liabilities', 'cash_flow']
        fin_statement_dd_l = options_for_dropdown(financial_statements_l)



        #[dbo].[A_income_statement_q]
        #[dbo].[A_balance_assets_q]
        #[dbo].[A_balance_liabilities_q]
        #[dbo].[A_cash_flow_q]


        layout_financial_statements_page = dash.html.Div([
            dash.html.H1(id='h1_ticker_name',
                         children='None ticker selected',
                         style={'width': '1200px', 'height': '40px'}),
            dash.html.Div(children=[
                dash.dcc.Dropdown(id='ticker_dd',
                                  options=tickers_dropdown_l,
                                  placeholder='Select ticker',
                                  multi=True,
                                  style={'width': '480px', 'height': '40px'}),
                dash.dcc.Dropdown(id='fin_statement_dd',
                                  options=fin_statement_dd_l,
                                  placeholder='Select ticker',
                                  multi=True,
                                  style={'width': '480px', 'height': '40px'})]),
            dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
        )




    tickers_list = ['GOOGL', 'META', 'NFLX']  # dodac jako argument
    app = dash.Dash(__name__, pages_folder="", use_pages=True)
    financial_statements_page(tickers_list, None)
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


