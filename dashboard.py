import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
import warnings

from plotly.validators.scatter.marker import SymbolValidator

from indicatorall import IndicatorAll, get_all_indicators
from tickerclass import Ticker
import utilities as u
import dashboardlinks as dashblinks


class IndcompFilters:
    def __init__(self):
        self.indicator = None
        self.split_type = 'companies'
        self.industry = []
        self.sector = []
        self.b_chosen_period = ButtonChosenPeriod()
        self.highlight_ticker = []


class DDChosen:
    def __init__(self, name):
        self.elements = []
        self.name = name
        self.elements_colors = []
        self.elements_markers = []
        self.marker_symbols = [m for m in SymbolValidator().values if isinstance(m, int)]
        self.marker_symbols_n = 0

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

    def assign_color_to_ticker(self, ticker_name):
        if ticker_name not in self.elements_colors:
            self.elements_colors.append(ticker_name)
            color = random_color()
            setattr(self, ticker_name + '_color', color)

    def assign_marker_to_indicator(self, indicator_name):
        if indicator_name not in self.elements_markers:
            self.elements_markers.append(indicator_name)
            setattr(self, indicator_name + '_marker', self.marker_symbols[self.marker_symbols_n])
            self.marker_symbols_n += 1


class ButtonChosenPeriod:
    def __init__(self, current_period='year'):
        self.val = current_period

    def update(self, click_num, current_period=None):
        if click_num == 1:
            if current_period == 'quarter':
                self.val = 'year'
            else:
                self.val = 'quarter'
        else:
            if self.val == 'year':
                self.val = 'quarter'
            else:
                self.val = 'year'

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
        self.chosen_fin_statement = None

    def update(self, dd_chosen_ticker, b_chosen_period):
        self.b_chosen_period = b_chosen_period
        self.period = b_chosen_period.val
        if len(dd_chosen_ticker.elements) == 1:
            self.ticker_name = dd_chosen_ticker.elements[-1]

    def get_df(self, chosen_statement=None):
        global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine

        self.chosen_fin_statement = chosen_statement
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


def sort_fin_st_df_columns(df):
    date_columns = [c for c in df.columns if c != 'index' and 'All' not in c]
    date_columns.sort()
    indicators_col = [c for c in df.columns if 'All' in c]
    columns = indicators_col + date_columns
    df = df[columns]
    return df


def convert_df_to_datatable(df):
    dt = None
    dtcols = None
    if df.empty is False:
        df.columns = [col + ' ' if 'Fiscal' not in col else col for col in df.columns]  # nazwy kolumn w dash data table nie moga byc liczba bo wowczas dash sortuje je automatycznie wedlug ukrytego wzoru
        dt = df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
        dtcols = list(df.columns)
    return dt, dtcols


def random_color():
    color = 'rgb' + str(tuple(np.random.choice(range(256), size=3)))
    return color


def ticker_indicator_period_update(chosen_val, ddchosen_obj_actual, dd_obj_other, b_chosen_period):

    def create_ticker_obj(main_chart_fig, ddchosen_obj_tic, ddchosen_obj_ind, b_chosen_period,
                          wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):

        def get_indicators_add_trace(main_chart_fig, ddchosen_obj_ind, tic, color):

            for i in ddchosen_obj_ind.elements:
                ddchosen_obj_ind.assign_marker_to_indicator(i)
                marker = getattr(ddchosen_obj_ind, i + '_marker')
                indicator_period = b_chosen_period.condition_return_val('_y', '_q')
                indicator_name = i + indicator_period
                x = getattr(tic, 'dates' + indicator_period).values
                x.sort()
                y = getattr(tic, indicator_name).values
                n = tic.name + '_' + i
                main_chart_fig.add_trace(go.Scatter(x=x,
                                                    y=y,
                                                    name=n,
                                                    line=dict(color=color),
                                                    marker=dict(symbol=marker,
                                                                size=10)))
            main_chart_fig.update_xaxes(type='category')

        n = 0
        for t in ddchosen_obj_tic.elements:
            tic = Ticker(t, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            set_period_type = b_chosen_period.condition_return_val(tic.set_df_year, tic.set_df_quarter)
            set_period_type()
            tic.create_indicators()
            ddchosen_obj_tic.assign_color_to_ticker(t)
            color = getattr(ddchosen_obj_tic, t + '_color')
            get_indicators_add_trace(main_chart_fig, ddchosen_obj_ind, tic, color)

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


def get_marker(special, color):
    if special:
        marker = dict(symbol='cross-open',
                      color=color,
                      size=25,
                      opacity=1,
                      line=dict(width=3))

    else:
        marker = dict(symbol='circle-open',
                      color=color,
                      size=20,
                      opacity=0.7,
                      line=dict(width=3))

    return marker


def create_indcomp_fig(tickers_list, chosen_indicator, split_type, industry, sector, b_chosen_period_value, highlight_ticker,
                       wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine):

    indall = IndicatorAll(tickers_list, chosen_indicator, industry, sector, b_chosen_period_value,
                       wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)

    x = indall.get_x()
    ys = indall.get_y()

    if split_type == 'companies':
        split_vals = indall.filtered_tickers_l
    elif split_type == 'sectors':
        split_vals = indall.get_sectors()
    elif split_type == 'industries':
        split_vals = indall.get_industries()

    colors = indall.assign_colors(split_vals)
    indcomp_fig = go.Figure()
    split_vals_legend = []
    for y, split_val, color, tic in zip(ys, split_vals, colors, indall.filtered_tickers_l):

        if split_val in split_vals_legend:  # show only distinct values in legend
            show_legend = False
        else:
            show_legend = True
            split_vals_legend.append(split_val)

        if tic in highlight_ticker: marker = get_marker(True, color)
        else: marker = get_marker(False, color)

        indcomp_fig.add_trace(go.Scatter(x=x,
                                         y=y,
                                         name=split_val,
                                         hovertext=tic,
                                         marker=marker,
                                         #marker_color=color,
                                         mode='markers',
                                         showlegend=show_legend))

    indcomp_fig.update_xaxes(type='category')

    return indcomp_fig, indall


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
    indicators_dd_l = options_for_dropdown(tic.indicators_names_l)
    return tickers_dropdown_l, indicators_dd_l

#def navigation_panel(current_page):
#
#    def create_button(txt, page, disabled):
#        button = dash.dcc.Link(dash.html.Button(txt), href='/' + page, disabled=disabled)
#        return button
#
#    pages = {'Main': '', 'Financial statements': 'fin_st'}
#    buttons = []
#    for page_name in pages.keys():
#        if pages[page_name] != current_page:
#            buttons.append(create_button(page_name, pages[page_name]))
#    buttons_layout = dash.html.Div(children=buttons)
#    return buttons_layout


def dashboard():

    def main_page():
        global tickers_l, dd_chosen_ticker, dd_chosen_indicator
        tickers_dropdown_l, indicators_dd_l = all_options_for_dropdowns(tickers_list)
        b_chosen_period = ButtonChosenPeriod()

        layout_main_page = dash.html.Div([
            dash.html.Div(
                dash.html.H1(id='h1_ticker_name',
                             children='None ticker selected',
                             style={'width': '1200px',
                                    'height': '40px'})
            ),
            dash.html.Div(children=[
                dash.dcc.Dropdown(id='ticker_dd',
                                  options=tickers_dropdown_l,
                                  placeholder='Select ticker',
                                  multi=True,
                                  style={'width': '600px',
                                         'height': '80px',
                                         'display': 'inline-block'}),
                dash.dcc.Dropdown(id='indicator_dd',
                                  options=indicators_dd_l,
                                  placeholder='Select indicator',
                                  multi=True,
                                  style={'width': '600px',
                                         'height': '80px',
                                         'display': 'inline-block'}),
                dash.html.Button(children='year',
                                 id='year_quarter_button',
                                 n_clicks=0,
                                 style={'width': '80px',
                                        'height': '80px',
                                        'display': 'inline-block',
                                        'vertical-align': 'top'})],
                          style={'display': 'inline-block'}
            ),
            dash.dcc.Graph(id='main_chart', figure=go.Figure(), style={'width': '1800px',
                                                                       'height': '800px'}),
            #dash.dcc.Link(dash.html.Button('Financial statement', id='button_link_to_finst', disabled=True), id='link_to_finst', href='/finst')
            dashblinks.link_finst(),
            dashblinks.link_indicator_comparison()
        ])
        dash.register_page('Main', path='/', layout=layout_main_page)

        @app.callback(
            dash.Output(component_id='h1_ticker_name', component_property='children'),
            dash.Output(component_id='main_chart', component_property='figure', allow_duplicate=True),
            dash.Output(component_id='button_link_to_finst', component_property='disabled'),
            dash.Input(component_id='ticker_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_ticker(chosen_ticker):
            global dd_chosen_ticker, dd_chosen_indicator, curr_choice_for_fin_st, fin_st_tickers_dropdown_l, \
                wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal b_chosen_period

            finst_link_disabled = True
            main_chart_fig = ticker_indicator_period_update(chosen_ticker, dd_chosen_ticker, dd_chosen_indicator,
                                                            b_chosen_period)
            if dd_chosen_ticker.not_empty() is False:
                title_h1_ticker = 'None ticker selected'
            else:
                title_h1_ticker = dd_chosen_ticker.elements
                fin_st_tickers_dropdown_l_update, indicators_dd_l = all_options_for_dropdowns(dd_chosen_ticker.elements)
                fin_st_tickers_dropdown_l = fin_st_tickers_dropdown_l_update
                finst_link_disabled = False
            curr_choice_for_fin_st.update(dd_chosen_ticker, b_chosen_period)
            return title_h1_ticker, main_chart_fig, finst_link_disabled

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
            global dd_chosen_ticker, dd_chosen_indicator, curr_choice_for_fin_st, \
                wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal b_chosen_period

            b_chosen_period.update(click_num)
            main_chart_fig = ticker_indicator_period_update(b_chosen_period.val, dd_chosen_ticker, dd_chosen_indicator,
                                                            b_chosen_period)
            curr_choice_for_fin_st.update(dd_chosen_ticker, b_chosen_period)
            return b_chosen_period.val, main_chart_fig

    def financial_statements_page():
        global dd_chosen_ticker, dd_chosen_indicator, curr_choice_for_fin_st, fin_st_tickers_dropdown_l

        financial_statements_l = ['income_statement', 'balance_assets', 'balance_liabilities', 'cash_flow']
        fin_statement_dd_l = options_for_dropdown(financial_statements_l)
        finst_b_chosen_period = ButtonChosenPeriod(curr_choice_for_fin_st.period)
        data_table, data_columns = convert_df_to_datatable(curr_choice_for_fin_st.get_df())

        layout_financial_statements_page = dash.html.Div([
            dash.html.H1(id='finst_h1_ticker_name',
                         children='None ticker selected',
                         style={'width': '1200px',
                                'height': '40px'}),
            dash.html.Div(children=[
                dash.dcc.Dropdown(id='fin_st_dd',
                                  options=fin_statement_dd_l,
                                  placeholder='Select financial statement',
                                  style={'width': '480px',
                                         'height': '40px',
                                         'display': 'inline-block'}),
                dash.html.Button(id='finst_year_quarter_button',
                                 children=curr_choice_for_fin_st.period,
                                 n_clicks=0,
                                 style={'width': '80px',
                                        'height': '40px',
                                        'display': 'inline-block',
                                        'vertical-align': 'top'})]),
            dash.html.Div(dash.dash_table.DataTable(id='fin_st_table',
                                                    data=data_table)),
            dash.dcc.Link(dash.html.Button('Main'), id='link_to_main', href='/')])

        dash.register_page('finst', path='/finst', layout=layout_financial_statements_page)

        @app.callback(
            dash.Output(component_id='finst_year_quarter_button', component_property='children'),
            dash.Output(component_id='fin_st_table', component_property='data'),
            dash.Output(component_id='finst_h1_ticker_name', component_property='children'),
            dash.Input(component_id='fin_st_dd', component_property='value'),
        )
        def update_fin_st_data_table(chosen_fin_st):
            global curr_choice_for_fin_st
            if chosen_fin_st:
                df = curr_choice_for_fin_st.get_df(chosen_fin_st)
                df = sort_fin_st_df_columns(df)
                dt, data_columns = convert_df_to_datatable(df)
                h1_val = curr_choice_for_fin_st.ticker_name + ' ' + chosen_fin_st
            else:
                df = curr_choice_for_fin_st.get_df()
                df = sort_fin_st_df_columns(df)
                dt, data_columns = convert_df_to_datatable(df)
                h1_val = curr_choice_for_fin_st.ticker_name + ' income statement'
            dt = dt[0]  # konieczne [0] nie moze byc w funkcji
            return curr_choice_for_fin_st.period, dt, h1_val

        @app.callback(
            dash.Output(component_id='finst_year_quarter_button', component_property='children', allow_duplicate=True),
            dash.Output(component_id='fin_st_table', component_property='data', allow_duplicate=True),
            dash.Input(component_id='finst_year_quarter_button', component_property='n_clicks'),
            prevent_initial_call=True
        )
        def finst_year_quarter_button_action(click_num):
            global curr_choice_for_fin_st, dd_chosen_ticker
            nonlocal finst_b_chosen_period
            finst_b_chosen_period.update(click_num, curr_choice_for_fin_st.period)
            curr_choice_for_fin_st.update(dd_chosen_ticker, finst_b_chosen_period)
            df = curr_choice_for_fin_st.get_df(curr_choice_for_fin_st.chosen_fin_statement)
            df = sort_fin_st_df_columns(df)
            dt, data_columns = convert_df_to_datatable(df)
            dt = dt[0]
            return finst_b_chosen_period.val, dt

    def indicator_comparison():
        global wsja_cursor, tickers_list

        def initial_options_for_dropdowns():
            global tickers_list, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            indicators_dd_l = options_for_dropdown(get_all_indicators(wsja_cursor))
            tickers_highlight_dd_l = options_for_dropdown(tickers_list)
            indall = IndicatorAll(tickers_list, 'p/s', [], [], 'year',
                                  wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            sectors_dd_l = options_for_dropdown(indall.filtered_sectors)
            industries_dd_l = options_for_dropdown(indall.filtered_industries)
            split_dd_l = options_for_dropdown(['companies', 'sectors', 'industries'])
            return indicators_dd_l, tickers_highlight_dd_l, sectors_dd_l, industries_dd_l, split_dd_l

        indicators_dd_l, tickers_highlight_dd_l, sectors_dd_l, industries_dd_l, split_dd_l = initial_options_for_dropdowns()
        indcomp_filters = IndcompFilters()

        layout_indicator_comparison_page = dash.html.Div([
            dash.html.Div(
                dash.html.H1(id='h1_indicator',
                             children='Please select indicator',
                             style={'width': '1200px',
                                    'height': '40px'})
            ),
            dash.html.Div(children=[
                dash.dcc.Dropdown(id='indcomp_ind_dd',
                                  options=indicators_dd_l,
                                  placeholder='Select indicator',
                                  multi=False,
                                  style={'width': '600px',
                                         'height': '80px',
                                         'display': 'inline-block'}),
                dash.dcc.Dropdown(id='indcomp_split_dd',
                                  options=split_dd_l,
                                  placeholder='Select split option',
                                  multi=False,
                                  style={'width': '200px',
                                         'height': '40px',
                                         'display': 'inline-block'}),
                dash.dcc.Dropdown(id='indcomp_sector_dd',
                                  options=sectors_dd_l,
                                  placeholder='Select sector',
                                  multi=True,
                                  style={'width': '600px',
                                         'height': '80px',
                                         'display': 'inline-block'}),
                dash.dcc.Dropdown(id='indcomp_industry_dd',
                                  options=industries_dd_l,
                                  placeholder='Select industry',
                                  multi=True,
                                  style={'width': '600px',
                                         'height': '80px',
                                         'display': 'inline-block'}),
                dash.dcc.Dropdown(id='indcomp_ticker_highlight_dd',
                                  options=tickers_highlight_dd_l,
                                  placeholder='Select ticker',
                                  multi=True,
                                  style={'width': '600px',
                                         'height': '80px',
                                         'display': 'inline-block'}),
                dash.html.Button(children='year',
                                 id='indcomp_year_quarter_button',
                                 n_clicks=0,
                                 style={'width': '80px',
                                        'height': '80px',
                                        'display': 'inline-block',
                                        'vertical-align': 'top'}),
            ]),
            dash.dcc.Graph(id='indcomp_chart', figure=go.Figure(), style={'width': '1800px',
                                                                          'height': '800px'}),
            dashblinks.link_main()
        ])

        dash.register_page('indcomp', path='/indcomp', layout=layout_indicator_comparison_page)

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_ind_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_indicator(chosen_indicator):
            global tickers_list, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal indcomp_filters

            indcomp_filters.indicator = chosen_indicator
            indcomp_fig, indall = create_indcomp_fig(tickers_list,
                                                     indcomp_filters.indicator,
                                                     indcomp_filters.split_type,
                                                     indcomp_filters.industry,
                                                     indcomp_filters.sector,
                                                     indcomp_filters.b_chosen_period.val,
                                                     indcomp_filters.highlight_ticker,
                                                     wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            return indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_split_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_split_selection(chosen_split_type):
            global tickers_list, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal indcomp_filters

            indcomp_filters.split_type = chosen_split_type
            indcomp_fig, indall = create_indcomp_fig(tickers_list,
                                                     indcomp_filters.indicator,
                                                     indcomp_filters.split_type,
                                                     indcomp_filters.industry,
                                                     indcomp_filters.sector,
                                                     indcomp_filters.b_chosen_period.val,
                                                     indcomp_filters.highlight_ticker,
                                                     wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            return indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_industry_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='indcomp_ticker_highlight_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_sector_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_sector_selection(chosen_sector):
            global tickers_list, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal indcomp_filters

            indcomp_filters.sector = chosen_sector
            indcomp_fig, indall = create_indcomp_fig(tickers_list,
                                                     indcomp_filters.indicator,
                                                     indcomp_filters.split_type,
                                                     indcomp_filters.industry,
                                                     indcomp_filters.sector,
                                                     indcomp_filters.b_chosen_period.val,
                                                     indcomp_filters.highlight_ticker,
                                                     wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn,
                                                     wsja_engine)
            industries_dd_l = options_for_dropdown(indall.filtered_industries)
            tickers_highlight_dd_l = options_for_dropdown(indall.filtered_tickers_l)
            return industries_dd_l, tickers_highlight_dd_l, indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_sector_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='indcomp_ticker_highlight_dd', component_property='options'),
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_industry_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_industry_selection(chosen_industry):
            global tickers_list, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal indcomp_filters

            indcomp_filters.industry = chosen_industry
            indcomp_fig, indall = create_indcomp_fig(tickers_list,
                                                     indcomp_filters.indicator,
                                                     indcomp_filters.split_type,
                                                     indcomp_filters.industry,
                                                     indcomp_filters.sector,
                                                     indcomp_filters.b_chosen_period.val,
                                                     indcomp_filters.highlight_ticker,
                                                     wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            sectors_dd_l = options_for_dropdown(indall.filtered_sectors)
            tickers_highlight_dd_l = options_for_dropdown(indall.filtered_tickers_l)
            return sectors_dd_l, tickers_highlight_dd_l, indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_sector_dd', component_property='options'),
            dash.Output(component_id='indcomp_industry_dd', component_property='options'),
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_ticker_highlight_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_highlighted_ticker_selection(chosen_ticker):
            global tickers_list, wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal indcomp_filters

            indcomp_filters.highlight_ticker = chosen_ticker
            indcomp_fig, indall = create_indcomp_fig(tickers_list,
                                                     indcomp_filters.indicator,
                                                     indcomp_filters.split_type,
                                                     indcomp_filters.industry,
                                                     indcomp_filters.sector,
                                                     indcomp_filters.b_chosen_period.val,
                                                     indcomp_filters.highlight_ticker,
                                                     wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            sectors_dd_l = options_for_dropdown(indall.filtered_sectors)
            industries_dd_l = options_for_dropdown(indall.filtered_industries)
            return sectors_dd_l, industries_dd_l, indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_year_quarter_button', component_property='children'),
            dash.Output(component_id='indcomp_chart', component_property='figure'),
            dash.Input(component_id='indcomp_year_quarter_button', component_property='n_clicks'),
            prevent_initial_call=True
        )
        def year_quarter_button_action(click_num):
            global wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine
            nonlocal indcomp_filters

            indcomp_filters.b_chosen_period.update(click_num)
            indcomp_fig, indall = create_indcomp_fig(tickers_list,
                                                     indcomp_filters.indicator,
                                                     indcomp_filters.split_type,
                                                     indcomp_filters.industry,
                                                     indcomp_filters.sector,
                                                     indcomp_filters.b_chosen_period.val,
                                                     indcomp_filters.highlight_ticker,
                                                     wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
            return indcomp_filters.b_chosen_period.val, indcomp_fig

    app = dash.Dash(__name__, pages_folder="", use_pages=True)
    financial_statements_page()
    main_page()
    indicator_comparison()
    app.run_server(debug=True)


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
end_time = time.time()
print(end_time - start_time)


