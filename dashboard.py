import dash

from dash.dash_table.Format import Format, Scheme

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import subprocess
import time
import warnings

from plotly.validators.scatter.marker import SymbolValidator

import dashboardlinks as dashblinks
import dashboardelements as dashele
import indicatorassessment
import utilities as u

from indicatorall import IndicatorAll, get_all_indicators
from tickerclass import Ticker


class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.action_name = None

    def start(self, action_name):
        self.action_name = action_name
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()
        res = self.end_time - self.start_time
        print(f'{self.action_name}: {res}')


class DataTableUnfiltering:
    def __init__(self, color_df):
        self.initial_color_df = color_df
        self.initial_shape = color_df.shape
        self.current_shape = self.initial_shape
        self.table_filtered = False

    def __shape1_less_than_shape2(self, shape1, shape2):
        if shape1[0] < shape2[0] or shape1[1] < shape2[1]:
            res = True
        else:
            res = False
        return res

    def sort_action(self, derived_virtual_indices):
        color_df = self.initial_color_df.reindex(derived_virtual_indices).reset_index(drop=True)
        return color_df

    def filter_action(self, color_df):
        self.current_shape = color_df.shape
        if self.__shape1_less_than_shape2(self.current_shape, self.initial_shape):
            self.table_filtered = True

    def unfilter_action(self, color_df, derived_virtual_indices):
        if self.table_filtered and self.__shape1_less_than_shape2(self.current_shape, color_df.shape):
            color_df = self.initial_color_df.reindex(derived_virtual_indices).reset_index(drop=True)
            self.table_filtered = False
            self.current_shape = color_df.shape
        return color_df


class IndcompFilters:
    def __init__(self, dd_chosen_price):
        self.indicator = None
        self.split_type = 'companies'
        self.industry = []
        self.sector = []
        self.chosen_tickers = []
        self.price_period_type = dd_chosen_price.period_type
        self.price_val_type = dd_chosen_price.val_type
        self.price_summarization = dd_chosen_price.summarization
        self.highlight_ticker = []
        self.fs_currencies = ['USD', 'EUR', 'HKD', 'JPY']
        self.p_currencies = ['USD', 'EUR', 'HKD', 'JPY']


class IiFilters:
    def __init__(self):
        global tickers_list
        self.x_indicator = None
        self.y_indicator = None
        self.tickers = tickers_list
        self.industry = []
        self.sector = []
        self.split_type = 'companies'
        self.dd_chosen_price = ChoiceForPrice()
        self.fs_currencies = ['USD', 'EUR', 'HKD', 'JPY']
        self.p_currencies = ['USD', 'EUR', 'HKD', 'JPY']


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
            fixed_colors = u.fixed_tickers_colors()
            if ticker_name in fixed_colors.keys():
                color = fixed_colors[ticker_name]
            else:
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
        global wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine, dd_chosen_price

        self.chosen_fin_statement = chosen_statement
        # single albo multi wybor w dropdown
        if chosen_statement is not None and isinstance(chosen_statement, str) is False:
            chosen_statement = chosen_statement[0]

        if self.ticker_name is None:
            df = pd.DataFrame()
        else:
            tic = Ticker(self.ticker_name, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine, dd_chosen_price)
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


# musi wpływać na wybór tablic przez klasę Ticker
class ChoiceForPrice:
    def __init__(self):
        self.period_type = 'day'
        self.val_type = 'Close'
        self.summarization = 'close'

        self.table_name_type = self.__get_table_name_type()

    def __get_table_name_type(self):
        return f'{self.period_type}_{self.val_type}_{self.summarization}'

    def update(self, period_type=None, val_type=None, summarization=None):
        if period_type:
            self.period_type = period_type
        elif val_type:
            self.val_type = val_type
        elif summarization:
            self.summarization = summarization


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


def dropdown_selection_of_price_property(price_type_property, chosen_val):
    global dd_chosen_ticker, dd_chosen_indicator, dd_chosen_price, \
        wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

    if price_type_property == 'period_type':
        dd_chosen_price.period_type = chosen_val
    if price_type_property == 'val_type':
        dd_chosen_price.val_type = chosen_val
    if price_type_property == 'summarization':
        dd_chosen_price.summarization = chosen_val

    main_chart_fig = ticker_indicator_period_update(dd_chosen_ticker, dd_chosen_indicator, dd_chosen_price)

    return main_chart_fig


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


def ticker_indicator_period_update(dd_chosen_ticker, dd_chosen_indicator, dd_chosen_price):

    def create_ticker_obj(main_chart_fig, ddchosen_obj_tic, ddchosen_obj_ind, dd_chosen_price,
                          wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine):

        def get_indicators_add_trace(main_chart_fig, ddchosen_obj_ind, tic, color, fs_currency, price_currency):

            for indicator_name in ddchosen_obj_ind.elements:
                ddchosen_obj_ind.assign_marker_to_indicator(indicator_name)
                marker = getattr(ddchosen_obj_ind, indicator_name + '_marker')
                x = getattr(tic, indicator_name).dates
                x.sort()
                y = getattr(tic, indicator_name).values
                n = tic.name + '_' + indicator_name
                hovertext = f'{tic.name}<br>{indicator_name}<br>FS: {fs_currency}, P: {price_currency}'
                main_chart_fig.add_trace(go.Scatter(x=x,
                                                    y=y,
                                                    name=n,
                                                    hovertext=hovertext,
                                                    line=dict(color=color),
                                                    marker=dict(symbol=marker,
                                                                size=10)))
            # main_chart_fig.update_xaxes(type='category')

        for t in ddchosen_obj_tic.elements:
            tic = Ticker(t, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine, dd_chosen_price)
            tic.set_analysis_df()
            tic.create_indicators()
            ddchosen_obj_tic.assign_color_to_ticker(t)
            color = getattr(ddchosen_obj_tic, t + '_color')
            get_indicators_add_trace(main_chart_fig, ddchosen_obj_ind, tic, color, tic.fs_currency, tic.p_currency)

    layout = go.Layout(
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0  # top margin
        )
    )
    main_chart_fig = go.Figure(layout=layout)

    if dd_chosen_ticker.not_empty() and dd_chosen_indicator.not_empty():
        create_ticker_obj(main_chart_fig, dd_chosen_ticker, dd_chosen_indicator, dd_chosen_price,
                              wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine)

    return main_chart_fig


def get_marker(special, color):
    if special:
        marker = dict(symbol='x-thin',
                      color=color,
                      size=15,
                      opacity=1,
                      line=dict(width=1))

    else:
        marker = dict(symbol='circle',
                      color=color,
                      size=10,
                      opacity=0.5,
                      line=dict(width=1))

    return marker


def create_indcomp_fig():
    global tickers_list, dd_chosen_price, indcomp_filters, \
        wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

    chosen_indicator = indcomp_filters.indicator
    split_type = indcomp_filters.split_type
    industry = indcomp_filters.industry
    sector = indcomp_filters.sector
    chosen_tickers = indcomp_filters.chosen_tickers
    highlight_ticker = indcomp_filters.highlight_ticker
    fs_currencies = indcomp_filters.fs_currencies
    p_currencies = indcomp_filters.p_currencies

    indall = IndicatorAll(tickers_list, chosen_tickers, chosen_indicator, industry, sector, dd_chosen_price,
                          wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine)

    if indcomp_filters.indicator is None:
        indcomp_fig = go.Figure()
    else:
        xs = indall.get_xs()
        ys = indall.get_ys()

        if split_type == 'companies':
            split_vals = indall.filtered_tickers_l
        elif split_type == 'sectors':
            split_vals = indall.get_sectors()
        elif split_type == 'industries':
            split_vals = indall.get_industries()

        colors = indall.assign_colors(split_vals)
        indcomp_fig = go.Figure()
        split_vals_legend = []
        for x, y, split_val, color, tic, sector, industry, fs_currency, price_currency in zip(xs, ys, split_vals, colors, indall.filtered_tickers_l, indall.get_sectors(), indall.get_industries(), indall.get_fs_currencies(), indall.get_p_currencies()):

            if fs_currency not in fs_currencies or price_currency not in p_currencies:  # skip if currency omitted in currency checklists
                continue

            if split_val in split_vals_legend:  # show only distinct values in legend
                show_legend = False
            else:
                show_legend = True
                split_vals_legend.append(split_val)

            if tic in highlight_ticker:
                marker = get_marker(True, color)
            else:
                marker = get_marker(False, color)

            hovertext = f'{tic}<br>{sector}<br>{industry}<br>FS: {fs_currency}, P: {price_currency}'

            indcomp_fig.add_trace(go.Scatter(x=x,
                                             y=y,
                                             name=split_val,
                                             hovertext=hovertext,
                                             line=dict(color=color, width=1),
                                             marker=marker,
                                             mode='lines+markers',
                                             showlegend=show_legend))

        # indcomp_fig.update_xaxes(type='category')
        indcomp_fig.update_layout(margin=dict(l=20, r=0, t=0, b=20))

    return indcomp_fig, indall


def options_for_dropdown(mylist):
    mylist = list(mylist)
    mylist.sort()
    newlist = []
    for i in mylist:
        tmp = {'label': i, 'value': i}
        newlist.append(tmp)
    return newlist


def all_options_for_dropdowns(tickers_list):
    global wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine, dd_chosen_price

    tic = Ticker(tickers_list[0], wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine, dd_chosen_price)
    tic.set_analysis_df()
    tic.create_indicators()
    tickers_dropdown_l = options_for_dropdown(tickers_list)
    indicators_dd_l = options_for_dropdown(tic.indicators_names_l)
    price_period_type_dd_l = options_for_dropdown(['day', 'week', 'month', 'quarter'])
    price_val_type_dd_l = options_for_dropdown(['High', 'Low', 'Open', 'Close'])
    price_summarization_dd_l = options_for_dropdown(['max', 'min', 'open', 'close'])
    return tickers_dropdown_l, indicators_dd_l, price_period_type_dd_l, price_val_type_dd_l, price_summarization_dd_l


def get_total_df():
    global tickers_list, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine
    dt_chosen_price = ChoiceForPrice()
    dt_indcomp_filters = IndcompFilters(dt_chosen_price)
    dt_indcomp_filters.chosen_tickers = tickers_list  # to display all tickers
    all_indicators = get_all_indicators(wsja2_cursor)
    total_df = None
    for indicator in all_indicators:
        this_ind = IndicatorAll(tickers_list,
                                dt_indcomp_filters.chosen_tickers,
                                indicator,
                                dt_indcomp_filters.industry,
                                dt_indcomp_filters.sector,
                                dt_chosen_price,
                                wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine)

        if total_df is None:  # first loop
            total_df = pd.DataFrame({'Ticker': this_ind.filtered_tickers_l,
                                     'Sector': this_ind.get_sectors(),
                                     'Industry': this_ind.get_industries()})

        vals = [inner_list[-1] for inner_list in this_ind.get_ys()]
        total_df[indicator] = vals
        total_df.iloc[:, 3:] = total_df.iloc[:, 3:].apply(lambda x: round(x, 2))
    return total_df


def dashboard():
    global timer

    def main_page():
        global tickers_list, dd_chosen_ticker, dd_chosen_indicator, dd_chosen_price
        tickers_dropdown_l, indicators_dd_l, price_period_type_dd_l, price_val_type_dd_l, price_summarization_dd_l = all_options_for_dropdowns(tickers_list)
        b_chosen_period = ButtonChosenPeriod()

        layout_main_page = dash.html.Div([
            dash.html.Div([
                dash.html.Div([dashele.main_h1()], style={'display': 'inline-block', 'textAlign': 'left', 'margin': '0', 'padding': '0'}),
                dash.html.Div([
                    dash.html.Div([dashblinks.link_finst()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_indicator_comparison()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_indicators_intersection()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_data_table()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div(dashblinks.link_score(), style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'})
                ], style={'display': 'inline-block', 'textAlign': 'right'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'height': '4vh', 'margin': '0', 'padding': '0hv'}),
            dash.html.Div(children=[
                dash.html.Div([
                    dash.dcc.Dropdown(id='ticker_dd',
                                      options=tickers_dropdown_l,
                                      placeholder='Select ticker',
                                      multi=True,
                                      style=dashele.main_multi_dropdown_style(),
                                      className = 'main_dropdown',
                                      clearable=False),
                    dash.dcc.Dropdown(id='indicator_dd',
                                      options=indicators_dd_l,
                                      placeholder='Select indicator',
                                      multi=True,
                                      style=dashele.main_multi_dropdown_style())
                ], style={'textAlign': 'left'}),
                dash.html.Div([
                    dash.dcc.Dropdown(id='price_period_type_dd',
                                      options=price_period_type_dd_l,
                                      placeholder='Period',
                                      multi=False,
                                      style=dashele.main_single_dropdown_style()),
                    dash.dcc.Dropdown(id='price_val_type_dd',
                                      options=price_val_type_dd_l,
                                      placeholder='Value',
                                      multi=False,
                                      style=dashele.main_single_dropdown_style()),
                    dash.dcc.Dropdown(id='price_summarization_dd',
                                      options=price_summarization_dd_l,
                                      placeholder='Summarization',
                                      multi=False,
                                      style=dashele.main_single_dropdown_style())
                ])
            ], style={'margin': '0', 'padding': '0'}),
            dash.html.Div([
                dash.dcc.Graph(id='main_chart',
                               figure=go.Figure(),
                               style={'height': '80vh',
                                      'width': '204vh',
                                      'borderWidth': '0',
                                      'margin': '0',
                                      'padding': '0'},
                               config={'displayModeBar': True})
                           ], style={'margin': '0', 'padding': '0'})
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
                wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine
            nonlocal b_chosen_period

            finst_link_disabled = True
            dd_chosen_ticker.update(chosen_ticker)
            curr_choice_for_fin_st.update(dd_chosen_ticker, b_chosen_period)
            main_chart_fig = ticker_indicator_period_update(dd_chosen_ticker, dd_chosen_indicator, dd_chosen_price)
            if dd_chosen_ticker.not_empty() is False:
                title_h1_ticker = 'None ticker selected'
            else:
                title_h1_ticker = dd_chosen_ticker.elements
                fin_st_tickers_dropdown_l_update, indicators_dd_l, price_period_type_dd_l, price_val_type_dd_l, price_summarization_dd_l = all_options_for_dropdowns(dd_chosen_ticker.elements)
                fin_st_tickers_dropdown_l = fin_st_tickers_dropdown_l_update
                finst_link_disabled = False
            return title_h1_ticker, main_chart_fig, finst_link_disabled

        @app.callback(
            dash.Output(component_id='main_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indicator_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_indicator(chosen_indicator):
            global dd_chosen_ticker, dd_chosen_indicator, dd_chosen_price, \
                wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

            dd_chosen_indicator.update(chosen_indicator)
            main_chart_fig = ticker_indicator_period_update(dd_chosen_ticker, dd_chosen_indicator, dd_chosen_price)
            return main_chart_fig

        @app.callback(
            dash.Output(component_id='main_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='price_period_type_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_price_period_type(chosen_val):
            main_chart_fig = dropdown_selection_of_price_property('period_type', chosen_val)
            return main_chart_fig

        @app.callback(
            dash.Output(component_id='main_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='price_val_type_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_price_period_type(chosen_val):
            main_chart_fig = dropdown_selection_of_price_property('val_type', chosen_val)
            return main_chart_fig

        @app.callback(
            dash.Output(component_id='main_chart', component_property='figure'),
            dash.Input(component_id='price_summarization_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_price_period_type(chosen_val):
            main_chart_fig = dropdown_selection_of_price_property('summarization', chosen_val)
            return main_chart_fig

    def financial_statements_page():
        global dd_chosen_ticker, dd_chosen_indicator, curr_choice_for_fin_st, fin_st_tickers_dropdown_l

        financial_statements_l = ['income_statement', 'balance_assets', 'balance_liabilities', 'cash_flow']
        fin_statement_dd_l = options_for_dropdown(financial_statements_l)
        finst_b_chosen_period = ButtonChosenPeriod(curr_choice_for_fin_st.period)
        data_table, data_columns = convert_df_to_datatable(curr_choice_for_fin_st.get_df())

        layout_financial_statements_page = dash.html.Div([
            dash.html.Div([
                dash.html.Div([dashele.finst_h1()], style={'display': 'inline-block', 'textAlign': 'left', 'margin': '0', 'padding': '0'}),
                dash.html.Div([
                    dash.html.Div([dashblinks.link_main()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_indicator_comparison()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_indicators_intersection()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_data_table()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div(dashblinks.link_score(), style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'})
                ], style={'display': 'inline-block', 'textAlign': 'right'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'height': '4vh', 'margin': '0', 'padding': '0hv'}),
            dash.html.Div([
                dash.html.Div([dash.dcc.Dropdown(id='fin_st_dd',
                                                 options=fin_statement_dd_l,
                                                 placeholder='Select financial statement',
                                                 style=dashele.finst_dropdown_style())
                               ], style={'display': 'inline-block', 'vertical-align': 'top'}),
                dash.html.Div([dash.html.Button(id='finst_year_quarter_button',
                                                children=curr_choice_for_fin_st.period,
                                                n_clicks=0,
                                                style=dashele.finst_button_style())
                               ], style={'display': 'inline-block', 'vertical-align': 'top'})
            ]),
            dash.html.Div(dash.dash_table.DataTable(id='fin_st_table',
                                                    data=data_table))
        ])

        dash.register_page('finst', path='/finst', layout=layout_financial_statements_page)

        @app.callback(
            dash.Output(component_id='finst_year_quarter_button', component_property='children'),
            dash.Output(component_id='fin_st_table', component_property='data'),
            dash.Output(component_id='finst_h1_ticker_name', component_property='children'),
            dash.Input(component_id='fin_st_dd', component_property='value'),
            prevent_initial_call=True
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
        global wsja2_cursor, tickers_list

        def initial_options_for_dropdowns():
            global tickers_list, dd_chosen_price, indcomp_filters, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine
            indicators_dd_l = options_for_dropdown(get_all_indicators(wsja2_cursor))
            tickers_highlight_dd_l = options_for_dropdown(tickers_list)
            indcomp_chosen_tickers_dd_l = options_for_dropdown(tickers_list)
            indall = IndicatorAll(tickers_list, [], 'P/S', [], [], dd_chosen_price,
                                  wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine)
            sectors_dd_l = options_for_dropdown(indall.filtered_sectors)
            industries_dd_l = options_for_dropdown(indall.filtered_industries)
            split_dd_l = options_for_dropdown(['companies', 'sectors', 'industries'])
            price_period_type_dd_l = options_for_dropdown(['day', 'week', 'month', 'quarter'])
            price_val_type_dd_l = options_for_dropdown(['High', 'Low', 'Open', 'Close'])
            price_summarization_dd_l = options_for_dropdown(['max', 'min', 'open', 'close'])
            return indicators_dd_l, indcomp_chosen_tickers_dd_l, tickers_highlight_dd_l, sectors_dd_l, industries_dd_l, split_dd_l, \
                price_period_type_dd_l, price_val_type_dd_l, price_summarization_dd_l

        indicators_dd_l, indcomp_chosen_tickers_dd_l, tickers_highlight_dd_l, sectors_dd_l, industries_dd_l, split_dd_l, price_period_type_dd_l, price_val_type_dd_l, price_summarization_dd_l = initial_options_for_dropdowns()
        indcomp_ind_dd = dashele.dropdown_ele('indcomp_ind_dd', indicators_dd_l, 'Select indicator', False, '20vh', '4vh')
        indcomp_split_dd = dashele.dropdown_ele('indcomp_split_dd', split_dd_l, 'Select split option', False, '20vh', '4vh')
        indcomp_sector_dd = dashele.dropdown_ele('indcomp_sector_dd', sectors_dd_l, 'Select sector', True, '20vh', '20vh')
        indcomp_industry_dd = dashele.dropdown_ele('indcomp_industry_dd', industries_dd_l, 'Select industry', True, '20vh', '20vh')
        indcomp_chosen_tickers_dd = dashele.dropdown_ele('indcomp_chosen_tickers_dd', indcomp_chosen_tickers_dd_l, 'Select ticker', True, '20vh', '20vh')
        indcomp_ticker_highlight_dd = dashele.dropdown_ele('indcomp_ticker_highlight_dd', tickers_highlight_dd_l, 'Select highlighted ticker', True, '20vh', '9vh')
        indcomp_price_period_type_dd = dashele.dropdown_ele('indcomp_price_period_type_dd', price_period_type_dd_l, dd_chosen_price.period_type, False, '20vh', '4vh')
        indcomp_price_val_type_dd = dashele.dropdown_ele('indcomp_price_val_type_dd', price_val_type_dd_l, dd_chosen_price.val_type, False, '20vh', '4vh')
        indcomp_price_summarization_dd = dashele.dropdown_ele('indcomp_price_summarization_dd', price_summarization_dd_l, dd_chosen_price.summarization, False, '20vh', '4vh')
        indcomp_fs_checkbox_title = dashele.fs_checkbox_title()
        indcomp_p_checkbox_title = dashele.p_checkbox_title()
        indcomp_fs_checkbox = dashele.fs_currency_checklist()
        indcomp_p_checkbox = dashele.p_currency_checklist()

        indcomp_title = dash.html.H1(id='h1_indicator',
                                     children='Indicators',
                                     style={'font-size': '20px',
                                            'text-align': 'center',
                                            'line-height': '2px'})

        indcomp_chart = dash.dcc.Graph(id='indcomp_chart',
                                       figure=go.Figure(),
                                       style={'height': '90vh', 'width': '175vh'})

        layout_indicator_comparison_page = dash.html.Div([
            dash.html.Div([
                dash.html.Div([dash.html.Div([indcomp_title], style={'display': 'inline-block', 'margin-left': '50px', 'margin-right': '140px', 'margin-top': '0px'}),
                               dash.html.Div([dash.html.Div([indcomp_fs_checkbox_title], style={'display': 'inline-block', 'margin-left': '10px', 'margin-right': '6px', 'margin-top': '0px'}),
                                              dash.html.Div([indcomp_fs_checkbox], style={'display': 'inline-block', 'margin-right': '20px', 'margin-top': '0px'}),
                                              dash.html.Div([indcomp_p_checkbox_title], style={'display': 'inline-block', 'margin-right': '6px', 'margin-top': '0px'}),
                                              dash.html.Div([indcomp_p_checkbox], style={'display': 'inline-block', 'margin-right': '6px', 'margin-top': '0px'})],
                                             style={'display': 'inline-block', 'padding': '3px 3px', 'border': '2px blue solid', 'border-radius': '10px'})
                               ], style={'display': 'inline-block',
                                         'textAlign': 'left',
                                         'margin-top': '0px'}),
                dash.html.Div([
                    dash.html.Div([dashblinks.link_main()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_indicators_intersection()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_data_table()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div(dashblinks.link_score(), style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'})
                    ], style={'display': 'inline-block', 'textAlign': 'right'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'height': '4vh', 'margin-top': '0px', 'padding': '0hv'}),
            dash.html.Div([
                dash.html.Div([dash.html.Div(indcomp_ind_dd),
                               dash.html.Div(indcomp_split_dd),
                               dash.html.Div(indcomp_sector_dd),
                               dash.html.Div(indcomp_industry_dd),
                               dash.html.Div(indcomp_chosen_tickers_dd),
                               dash.html.Div(indcomp_ticker_highlight_dd),
                               dash.html.Div(indcomp_price_period_type_dd),
                               dash.html.Div(indcomp_price_val_type_dd),
                               dash.html.Div(indcomp_price_summarization_dd)
                               ], style={'display': 'inline-block'}),
                dash.html.Div([indcomp_chart], style={'display': 'inline-block', 'margin': '0vh 2vh'}),
            ], style={'marginBottom': 0, 'marginTop': 0})
        ])

        dash.register_page('indcomp', path='/indcomp', layout=layout_indicator_comparison_page)

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            [dash.Input('fs_currency_checklist', 'value')],
            prevent_initial_call=True
        )
        def checklist_selection_of_fs_currency(fs_currencies):
            indcomp_filters.fs_currencies = fs_currencies
            indcomp_fig, indall = create_indcomp_fig()
            return indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            [dash.Input('p_currency_checklist', 'value')],
            prevent_initial_call=True
        )
        def checklist_selection_of_p_currency(p_currencies):
            indcomp_filters.p_currencies = p_currencies
            indcomp_fig, indall = create_indcomp_fig()
            return indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_ind_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_indicator(chosen_indicator):
            global tickers_list, indcomp_filters, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

            indcomp_filters.indicator = chosen_indicator
            if indcomp_filters.indicator is None:
                indcomp_fig = go.Figure()
            else:
                indcomp_fig, indall = create_indcomp_fig()
            return indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_split_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_split_selection(chosen_split_type):
            global tickers_list, indcomp_filters, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

            indcomp_filters.split_type = chosen_split_type
            indcomp_fig, indall = create_indcomp_fig()
            return indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_industry_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='indcomp_ticker_highlight_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_sector_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_sector_selection(chosen_sector):
            global tickers_list, indcomp_filters, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

            indcomp_filters.sector = chosen_sector
            indcomp_fig, indall = create_indcomp_fig()
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
            global tickers_list, indcomp_filters, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

            indcomp_filters.industry = chosen_industry
            indcomp_fig, indall = create_indcomp_fig()
            sectors_dd_l = options_for_dropdown(indall.filtered_sectors)
            tickers_highlight_dd_l = options_for_dropdown(indall.filtered_tickers_l)
            return sectors_dd_l, tickers_highlight_dd_l, indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_chosen_tickers_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_chosen_tickers_selection(chosen_tickers):
            global tickers_list, indcomp_filters, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

            indcomp_filters.chosen_tickers = chosen_tickers
            indcomp_fig, indall = create_indcomp_fig()
            return indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_sector_dd', component_property='options'),
            dash.Output(component_id='indcomp_industry_dd', component_property='options'),
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_ticker_highlight_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_highlighted_ticker_selection(chosen_ticker):
            global tickers_list, indcomp_filters, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

            indcomp_filters.highlight_ticker = chosen_ticker
            indcomp_fig, indall = create_indcomp_fig()
            sectors_dd_l = options_for_dropdown(indall.filtered_sectors)
            industries_dd_l = options_for_dropdown(indall.filtered_industries)
            return sectors_dd_l, industries_dd_l, indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_price_period_type_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_highlighted_ticker_selection(chosen_price_period_type):
            global indcomp_filters, dd_chosen_price

            dd_chosen_price.period_type = chosen_price_period_type
            indcomp_filters.price_period_type = chosen_price_period_type
            indcomp_fig, indall = create_indcomp_fig()
            return indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_price_val_type_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_highlighted_ticker_selection(chosen_price_val_type):
            global indcomp_filters, dd_chosen_price

            dd_chosen_price.val_type = chosen_price_val_type
            indcomp_filters.price_val_type = chosen_price_val_type
            indcomp_fig, indall = create_indcomp_fig()
            return indcomp_fig

        @app.callback(
            dash.Output(component_id='indcomp_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='indcomp_price_summarization_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_highlighted_ticker_selection(chosen_price_summarization):
            global indcomp_filters, dd_chosen_price

            dd_chosen_price.summarization = chosen_price_summarization
            indcomp_filters.price_summarization = chosen_price_summarization
            indcomp_fig, indall = create_indcomp_fig()
            return indcomp_fig

    def dash_table():
        global total_df, color_df, score_df

        def color_conditional():
            global color_df
            timer.start('new ifs')
            color_dict = {}
            for c in color_df:
                color_dict[c] = {}
                unique_colors = color_df[c].unique()
                for u in unique_colors:
                    color_dict[c][u] = []
                for i in color_df.index:
                    color = color_df[c][i]
                    color_dict[c][color].append(i)
            conditional = [{'if': {'column_id': c, 'row_index': color_dict[c][color]}, 'background-color': color} for c in color_dict.keys() for color in color_dict[c].keys()]
            timer.end()
            return conditional

        def custom_format(col_name):
            # applying format 123 or 123.00 for selected columns
            myformat = Format()
            if col_name in ['Revenue', 'Gross Income', 'EBIT', 'EBITDA', 'NOPAT', 'Net Income', 'Research and Development', 'Total Debt']:
                myformat = Format(precision=0, scheme=Scheme.fixed)
            elif col_name in ['Price', 'P/S', 'Altman Z Score', 'P/E', 'PEG', 'ROE', 'Retained Earnings', 'Stopa wzrostu', 'ROA', 'ROC', 'ROCE', 'ROIC', 'Gross Margins', 'EBITDA Margins', 'EBIT Margins', 'Net Margins', 'Debt to Equity Ratio', 'Total Debt to Total Assets Ratio', 'CAPEX to Revenue Ratio', 'Beneish M Score', 'Current Ratio', 'EPS', 'Debt Service Coverage Ratio', 'Cash Ratio', 'Operationg Cash Flow Debt Ratio']:
                myformat = Format(precision=2, scheme=Scheme.fixed)
            return myformat

        print(total_df[total_df['Ticker'] == 'STLA']['Industry'])
        total_df_dict = total_df.to_dict('records')

        total_table_layout = dash.html.Div([
            dash.html.Div([
                dash.html.Div(dash.html.A(dash.html.Button('Refresh Data', style=dashele.data_table_button_style()), href='/data_table'), style={'display': 'inline-block', 'textAlign': 'left'}),
                dash.html.Div([
                    dash.html.Div(dashblinks.link_main(), style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div(dashblinks.link_indicator_comparison(), style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_indicators_intersection()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div(dashblinks.link_score(), style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'})
                ], style={'display': 'inline-block', 'textAlign': 'right'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'height': '4vh', 'margin': '0', 'padding': '0hv'}),
            dash.dash_table.DataTable(
                id='total_table',
                data=total_df_dict,
                style_data_conditional=color_conditional(),
                columns=[{'id': c, 'name': c, 'hideable': True, 'type': 'numeric', 'format': custom_format(c)} for c in total_df.columns],
                editable=False,
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                row_selectable='multi',
                row_deletable=True,
                style_cell={'minWidth': 85, 'maxWidth': 175, 'width': 95},
                style_header={'whiteSpace': 'normal', 'height': 'auto'},
                style_data={'whiteSpace': 'normal', 'height': 'auto'},
                page_size=500
            )
        ])

        @app.callback(
            dash.dependencies.Output('total_table', 'style_data_conditional'),
            dash.dependencies.Input('total_table', 'derived_virtual_indices')
        )
        def update_colors(derived_virtual_indices):
            global color_df, data_table_unfiltering
            color_df = data_table_unfiltering.sort_action(derived_virtual_indices)
            color_df = data_table_unfiltering.unfilter_action(color_df, derived_virtual_indices)
            data_table_unfiltering.filter_action(color_df)
            conditional = color_conditional()

            return conditional

        dash.register_page('data_table', path='/data_table', layout=total_table_layout)

    def indicators_intersection():

        def initial_options_for_dropdowns_ii():
            indicators_dd_l = options_for_dropdown(get_all_indicators(wsja2_cursor))
            tickers_dd_l = options_for_dropdown(tickers_list)
            indall = IndicatorAll(tickers_list, [], 'P/S', [], [], dd_chosen_price,
                                  wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine)
            sectors_dd_l = options_for_dropdown(indall.filtered_sectors)
            industries_dd_l = options_for_dropdown(indall.filtered_industries)
            split_dd_l = options_for_dropdown(['companies', 'sectors', 'industries'])
            return indicators_dd_l, tickers_dd_l, sectors_dd_l, industries_dd_l, split_dd_l

        def create_ii_fig():
            global ii_filters, wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine

            # selecting both indicators is necessary to proceed
            if ii_filters.x_indicator is None or ii_filters.y_indicator is None or (len(ii_filters.industry) == 0 and len(ii_filters.sector) == 0):
                ii_fig = go.Figure()
                return ii_fig, None, None

            x_ind = IndicatorAll(ii_filters.tickers, [], ii_filters.x_indicator, ii_filters.industry, ii_filters.sector,
                                 ii_filters.dd_chosen_price,
                                 wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine)
            xs = [x[-1] for x in x_ind.get_ys()]
            y_ind = IndicatorAll(ii_filters.tickers, [], ii_filters.y_indicator, ii_filters.industry, ii_filters.sector,
                                 ii_filters.dd_chosen_price,
                                 wsj_cursor, wsj_conn, wsj_engine, wsja2_cursor, wsja2_conn, wsja2_engine)
            ys = [y[-1] for y in y_ind.get_ys()]

            if ii_filters.split_type == 'companies':
                split_vals = x_ind.filtered_tickers_l
            elif ii_filters.split_type == 'sectors':
                split_vals = x_ind.get_sectors()
            elif ii_filters.split_type == 'industries':
                split_vals = x_ind.get_industries()

            fs_currencies = ii_filters.fs_currencies
            p_currencies = ii_filters.p_currencies

            colors = x_ind.assign_colors(split_vals)
            ii_fig = go.Figure()
            split_vals_legend = []
            for x, y, split_val, color, tic, sector, industry, fs_currency, p_currency in zip(xs, ys, split_vals, colors, x_ind.filtered_tickers_l,
                                                                                              x_ind.get_sectors(), x_ind.get_industries(),
                                                                                              x_ind.get_fs_currencies(), x_ind.get_p_currencies()):

                if fs_currency not in fs_currencies or p_currency not in p_currencies:  # skip if currency omitted in currency checklists
                    continue

                if split_val in split_vals_legend:  # show only distinct values in legend
                    show_legend = False
                else:
                    show_legend = True
                    split_vals_legend.append(split_val)

                marker = get_marker(False, color)
                hovertext = f'{tic}<br>{sector}<br>{industry}<br>FS: {fs_currency}, P: {p_currency}'

                ii_fig.add_trace(go.Scatter(x=[x],
                                            y=[y],
                                            name=split_val,
                                            hovertext=hovertext,
                                            marker=marker,
                                            mode='markers',
                                            showlegend=show_legend))

            median_x = np.median(xs)
            min_x = np.min(xs)
            max_x = np.max(xs)
            median_y = np.median(ys)
            min_y = np.min(ys)
            max_y = np.max(ys)
            indicators_ratio = np.mean(ys) / np.mean(xs)
            max_y_indicators_ratio = max_x * indicators_ratio

            ii_fig.add_trace(go.Scatter(x=[min_x, max_x],
                                        y=[median_y, median_y],
                                        mode='lines',
                                        line=dict(color='blue', width=1),
                                        showlegend=False))  # horizontal

            ii_fig.add_trace(go.Scatter(x=[median_x, median_x],
                                        y=[min_y, max_y],
                                        mode='lines',
                                        line=dict(color='blue', width=1),
                                        showlegend=False))  # vertical

            ii_fig.add_trace(go.Scatter(x=[0, max_x],
                                        y=[0, max_y_indicators_ratio],
                                        mode='lines',
                                        line=dict(color='blue', width=1),
                                        showlegend=False))  # inclined

            ii_fig.update_layout(margin=dict(l=20, r=0, t=0, b=20),
                                 xaxis_title=ii_filters.x_indicator,
                                 yaxis_title=ii_filters.y_indicator)

            return ii_fig, x_ind, y_ind

        indicators_dd_l, tickers_dd_l, sectors_dd_l, industries_dd_l, split_dd_l = initial_options_for_dropdowns_ii()
        ii_ind_dd_x = dashele.dropdown_ele('ii_ind_dd_x', indicators_dd_l, 'Select first indicator', False, '20vh', '4vh')
        ii_ind_dd_y = dashele.dropdown_ele('ii_ind_dd_y', indicators_dd_l, 'Select second indicator', False, '20vh', '4vh')
        ii_ticker_dd = dashele.dropdown_ele('ii_ticker_dd', tickers_dd_l, 'Select ticker', True, '20vh', '23vh')
        ii_sector_dd = dashele.dropdown_ele('ii_sector_dd', sectors_dd_l, 'Select sector', True, '20vh', '23vh')
        ii_industry_dd = dashele.dropdown_ele('ii_industry_dd', industries_dd_l, 'Select industry', True, '20vh', '23vh')
        ii_split_dd = dashele.dropdown_ele('ii_split_dd', split_dd_l, 'Select split option', False, '20vh', '4vh')
        ii_fs_checkbox_title = dashele.fs_checkbox_title()
        ii_p_checkbox_title = dashele.p_checkbox_title()
        ii_fs_checkbox = dashele.fs_currency_checklist()
        ii_p_checkbox = dashele.p_currency_checklist()

        ii_title = dash.html.H1(id='h1_ii',
                                children='Indicators intersection',
                                style={'font-size': '20px',
                                       'text-align': 'center',
                                       'line-height': '2px'})

        ii_chart = dash.dcc.Graph(id='ii_chart',
                                  figure=go.Figure(),
                                  style={'height': '90vh', 'width': '175vh'})

        layout_ii_page = dash.html.Div([
            dash.html.Div([
                dash.html.Div([dash.html.Div([ii_title], style={'display': 'inline-block', 'margin-left': '5px', 'margin-right': '50px', 'margin-top': '0px'}),
                               dash.html.Div([dash.html.Div([ii_fs_checkbox_title], style={'display': 'inline-block', 'margin-left': '10px', 'margin-right': '6px', 'margin-top': '0px'}),
                                              dash.html.Div([ii_fs_checkbox], style={'display': 'inline-block', 'margin-right': '20px', 'margin-top': '0px'}),
                                              dash.html.Div([ii_p_checkbox_title], style={'display': 'inline-block', 'margin-right': '6px', 'margin-top': '0px'}),
                                              dash.html.Div([ii_p_checkbox], style={'display': 'inline-block', 'margin-right': '6px', 'margin-top': '0px'})],
                                             style={'display': 'inline-block', 'padding': '3px 3px', 'border': '2px blue solid', 'border-radius': '10px'})
                               ], style={'display': 'inline-block',
                                         'textAlign': 'left',
                                         'margin-top': '0px'
                                         }),
                dash.html.Div([
                    dash.html.Div([dashblinks.link_main()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div([dashblinks.link_data_table()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                    dash.html.Div(dashblinks.link_score(), style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'})
                    ], style={'display': 'inline-block', 'textAlign': 'right'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'height': '4vh', 'margin-top': '0px', 'padding': '0hv'}),
            dash.html.Div([
                dash.html.Div([dash.html.Div(ii_ind_dd_x),
                               dash.html.Div(ii_ind_dd_y),
                               dash.html.Div(ii_ticker_dd),
                               dash.html.Div(ii_sector_dd),
                               dash.html.Div(ii_industry_dd),
                               dash.html.Div(ii_split_dd)
                               ], style={'display': 'inline-block'}),
                dash.html.Div([ii_chart], style={'display': 'inline-block', 'margin': '0vh 2vh'}),
            ], style={'marginBottom': 0, 'marginTop': 0})
        ])

        dash.register_page('ii', path='/ii', layout=layout_ii_page)

        @app.callback(
            dash.Output(component_id='ii_chart', component_property='figure', allow_duplicate=True),
            [dash.Input('fs_currency_checklist', 'value')],
            prevent_initial_call=True
        )
        def checklist_selection_of_fs_currency(fs_currencies):
            ii_filters.fs_currencies = fs_currencies
            ii_fig, x_ind, y_ind = create_ii_fig()
            return ii_fig

        @app.callback(
            dash.Output(component_id='ii_chart', component_property='figure', allow_duplicate=True),
            [dash.Input('p_currency_checklist', 'value')],
            prevent_initial_call=True
        )
        def checklist_selection_of_p_currency(p_currencies):
            ii_filters.p_currencies = p_currencies
            ii_fig, x_ind, y_ind = create_ii_fig()
            return ii_fig

        @app.callback(
            dash.Output(component_id='ii_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='ii_ind_dd_x', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_x_indicator(chosen_indicator):
            global ii_filters

            ii_filters.x_indicator = chosen_indicator
            ii_fig, x_ind, y_ind = create_ii_fig()
            return ii_fig

        @app.callback(
            dash.Output(component_id='ii_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='ii_ind_dd_y', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_selection_of_y_indicator(chosen_indicator):
            global ii_filters

            ii_filters.y_indicator = chosen_indicator
            ii_fig, x_ind, y_ind = create_ii_fig()
            return ii_fig

        @app.callback(
            dash.Output(component_id='ii_sector_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='ii_industry_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='ii_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='ii_ticker_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_ticker_selection(chosen_ticker):
            global ii_filters

            ii_filters.tickers = chosen_ticker
            ii_fig, x_ind, y_ind = create_ii_fig()
            sectors_dd_l = options_for_dropdown(x_ind.filtered_sectors)
            industries_dd_l = options_for_dropdown(x_ind.filtered_industries)
            return sectors_dd_l, industries_dd_l, ii_fig

        @app.callback(
            dash.Output(component_id='ii_industry_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='ii_ticker_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='ii_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='ii_sector_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_sector_selection(chosen_sector):
            global ii_filters

            ii_filters.sector = chosen_sector
            ii_fig, x_ind, y_ind = create_ii_fig()
            industries_dd_l = options_for_dropdown(x_ind.filtered_industries)
            tickers_dd_l = options_for_dropdown(x_ind.filtered_tickers_l)
            return industries_dd_l, tickers_dd_l, ii_fig

        @app.callback(
            dash.Output(component_id='ii_sector_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='ii_ticker_dd', component_property='options', allow_duplicate=True),
            dash.Output(component_id='ii_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='ii_industry_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_industry_selection(chosen_industry):
            global ii_filters

            ii_filters.industry = chosen_industry
            ii_fig, x_ind, y_ind = create_ii_fig()
            sectors_dd_l = options_for_dropdown(x_ind.filtered_sectors)
            tickers_dd_l = options_for_dropdown(x_ind.filtered_tickers_l)
            return sectors_dd_l, tickers_dd_l, ii_fig

        @app.callback(
            dash.Output(component_id='ii_chart', component_property='figure', allow_duplicate=True),
            dash.Input(component_id='ii_split_dd', component_property='value'),
            prevent_initial_call=True
        )
        def dropdown_split_selection(chosen_split_type):
            global ii_filters

            ii_filters.split_type = chosen_split_type
            ii_fig, x_ind, y_ind = create_ii_fig()
            return ii_fig

    def score():
        global total_df, color_df, score_df
        score_layout = dash.html.Div([
            dash.html.Div([
                dash.html.Div(dashblinks.link_main(), style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                dash.html.Div([dashblinks.link_indicator_comparison()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                dash.html.Div([dashblinks.link_indicators_intersection()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'}),
                dash.html.Div([dashblinks.link_data_table()], style={'display': 'inline-block', 'margin': '0', 'padding': '0px 2px'})
                ], style={'textAlign': 'right'}),
            dash.html.Div([dash.dash_table.DataTable(id='score_table',
                                                     data=score_df.to_dict('records'),
                                                     columns=[{'id': c, 'name': c, 'hideable': True} for c in score_df.columns],
                                                     editable=True,
                                                     filter_action='native',
                                                     sort_action='native',
                                                     sort_mode='multi',
                                                     row_selectable='multi',
                                                     row_deletable=True,
                                                     style_cell={'minWidth': 85, 'maxWidth': 175, 'width': 95},
                                                     style_header={'whiteSpace': 'normal', 'height': 'auto'},
                                                     style_data={'whiteSpace': 'normal', 'height': 'auto'}
                                                     )
                           ])
            ])

        dash.register_page('score', path='/score', layout=score_layout)

    app = dash.Dash(__name__, pages_folder="", use_pages=True)
    main_page()
    financial_statements_page()
    indicator_comparison()
    indicators_intersection()
    dash_table()
    score()
    #chrome_path = "C:\Program Files\Google\Chrome\Application/chrome.exe"
    #url = 'http://127.0.0.1:8050/'
    #subprocess.Popen([chrome_path, url])
    app.run_server(debug=True)


def tickers_l_from_sql_tables(database):
    cursor, conn, engine = u.create_sql_connection(database)
    sql_table_list = u.get_all_tables(cursor)
    tickers_l_sql = set()
    for tabl in sql_table_list:
        tabl_split = tabl.split('_')
        if 'analysis' in tabl_split:
            tic = tabl_split[1]
        else:
            tic = tabl_split[0]
        #ticpos = tabl.find('_')
        #tic = tabl[:ticpos]
        tickers_l_sql.add(tic)
    tickers_l_sql = list(tickers_l_sql)
    cursor.close()
    return tickers_l_sql


if __name__ == '__main__':
    u.pandas_df_display_options()
    warnings.filterwarnings('ignore')
    timer = Timer()
    timer0 = Timer()
    tickers_l_sql_wsj = tickers_l_from_sql_tables('wsj')
    tickers_l_sql_wsja2 = tickers_l_from_sql_tables('wsja2')
    tickers_l_csv = pd.read_csv(r'C:\Users\barto\Desktop\Inwestor_2023\source_data\tickers_list.csv')
    tickers_l_csv = tickers_l_csv[tickers_l_csv['valid'] == 1]['ticker'].tolist()

    tickers_list = [tic for tic in tickers_l_csv if tic in tickers_l_sql_wsj and tic in tickers_l_sql_wsja2]
    print("Number of duplicated tickers ", len(tickers_list) - len(set(tickers_list)))
    #tickers_list = ['META', 'AAPL', 'GOOGL']
    fin_st_tickers_dropdown_l = []

    dd_chosen_ticker = DDChosen('ticker')
    dd_chosen_indicator = DDChosen('indicator')
    dd_chosen_price = ChoiceForPrice()
    indcomp_filters = IndcompFilters(dd_chosen_price)
    ii_filters = IiFilters()

    curr_choice_for_fin_st = CurrentChooiceForFinStatement()
    wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
    wsja2_cursor, wsja2_conn, wsja2_engine = u.create_sql_connection('wsja2')
    total_df = get_total_df()
    color_df, score_df = indicatorassessment.indicator_assessment(total_df)
    data_table_unfiltering = DataTableUnfiltering(color_df)
    dashboard()
