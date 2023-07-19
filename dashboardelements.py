import dash


### main ###


def main_h1():
    ele = dash.html.H1(id='h1_ticker_name',
                       children='None ticker selected',
                       style={'font-size': '20px'})
    return ele


def main_multi_dropdown_style():
    style = {'width': '102vh',
             'height': '4vh',
             'display': 'inline-block',
             'background-color': 'white',
             'color': 'black',
             'borderWidth': '2px',
             'borderColor': 'blue',
             'borderRadius': '6px',
             'margin': '2px 2px'}
    return style


def main_single_dropdown_style():
    style = {'width': '10vh',
             'height': '4vh',
             'display': 'inline-block',
             'background-color': 'white',
             'color': 'black',
             'borderWidth': '2px',
             'borderColor': 'blue',
             'borderRadius': '6px',
             'margin': '2px 2px'}
    return style


### finst ###


def finst_h1():
    ele = dash.html.H1(id='finst_h1_ticker_name',
                       children='None ticker selected',
                       style={'font-size': '20px'})
    return ele


def finst_dropdown_style():
    style = {'width': '30vh',
             'height': '4vh',
             'vertical-align': 'center',
             'background-color': 'white',
             'color': 'black',
             'borderWidth': '2px',
             'borderColor': 'blue',
             'borderRadius': '6px',
             'margin': '2px 2px'}
    return style


def finst_button_style():
    style = {'width': '20vh',
             'height': '4vh',
             'display': 'inline-block',
             'vertical-align': 'center',
             'background-color': 'blue',
             'color': 'white',
             'borderWidth': '2px',
             'borderColor': 'blue',
             'borderRadius': '6px',
             'margin': '2px 2px'}
    return style

### indcomp ###


def indcomp_multi_dropdown_style():
    style = {'width': '20vh',
             'height': '12vh',
             'alignItems': 'top',
             'background-color': 'white',
             'color': 'black',
             'fontSize': '12',
             'borderWidth': '2px',
             'borderColor': 'blue',
             'borderRadius': '6px',
             'margin': '2px 2px'}
    return style


def indcomp_single_dropdown_style():
    style = {'width': '20vh',
             'height': '4vh',
             'alignItems': 'top',
             'background-color': 'white',
             'color': 'black',
             'fontSize': '12',
             'borderWidth': '2px',
             'borderColor': 'blue',
             'borderRadius': '6px',
             'margin': '2px 2px'}
    return style


###   ###

def dropdown_ele(id, options, placeholder, multi, width, height):
    if multi:
        style = indcomp_multi_dropdown_style()
    else:
        style = indcomp_single_dropdown_style()

    ele = dash.dcc.Dropdown(id=id,
                            options=options,
                            placeholder=placeholder,
                            multi=multi,
                            style=style)
    return ele


def get_indicator_comparison_filters_elements_l(indicators_dd_l, split_dd_l, sectors_dd_l, industries_dd_l,
                                                tickers_highlight_dd_l, price_period_type_dd_l, price_val_type_dd_l,
                                                price_summarization_dd_l, dd_chosen_price):
    indicator_comparison_filters_elements_l = [
        dash.dcc.Dropdown(id='indcomp_ind_dd',
                          options=indicators_dd_l,
                          placeholder='Select indicator',
                          multi=False,
                          style={'width': '300px',
                                 'height': '80px'}),
        dash.dcc.Dropdown(id='indcomp_split_dd',
                          options=split_dd_l,
                          placeholder='Select split option',
                          multi=False,
                          style={'width': '300px',
                                 'height': '40px'}),
        dash.dcc.Dropdown(id='indcomp_sector_dd',
                          options=sectors_dd_l,
                          placeholder='Select sector',
                          multi=True,
                          style={'width': '300px',
                                 'height': '80px'}),
        dash.dcc.Dropdown(id='indcomp_industry_dd',
                          options=industries_dd_l,
                          placeholder='Select industry',
                          multi=True,
                          style={'width': '300px',
                                 'height': '80px'}),
        dash.dcc.Dropdown(id='indcomp_ticker_highlight_dd',
                          options=tickers_highlight_dd_l,
                          placeholder='Select ticker',
                          multi=True,
                          style={'width': '300px',
                                 'height': '80px'}),
        dash.dcc.Dropdown(id='indcomp_price_period_type',
                          options=price_period_type_dd_l,
                          placeholder=dd_chosen_price.period_type,
                          multi=False,
                          style={'width': '300px',
                                 'height': '80px'}),
        dash.dcc.Dropdown(id='indcomp_price_val_type',
                          options=price_val_type_dd_l,
                          placeholder=dd_chosen_price.val_type,
                          multi=False,
                          style={'width': '300px',
                                 'height': '80px'}),
        dash.dcc.Dropdown(id='indcomp_price_summarization',
                          options=price_summarization_dd_l,
                          placeholder=dd_chosen_price.summarization,
                          multi=False,
                          style={'width': '300px',
                                 'height': '80px'})
    ]
    return indicator_comparison_filters_elements_l
