import dash

def dropdown_ele(id, options, placeholder, multi, width, height):
    ele = dash.dcc.Dropdown(id=id,
                                          options=options,
                                          placeholder=placeholder,
                                          multi=multi,
                                          style={'width': str(width) + 'px',
                                                 'height': str(height) + 'px'})
    return ele




def get_indicator_comparison_filters_elements_l(indicators_dd_l, split_dd_l, sectors_dd_l, industries_dd_l, tickers_highlight_dd_l, price_period_type_dd_l, price_val_type_dd_l, price_summarization_dd_l, dd_chosen_price):
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
