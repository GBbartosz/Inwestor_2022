import dash

def link_style():
    style = {'height': '3vh',
             'background-color': 'blue',
             'color': 'white',
             'border': '2px',
             'border-radius': '6px'}
    return style

def link_main():
    obj = dash.dcc.Link(dash.html.Button('Main',
                                         style=link_style()),
                        id='main_page_link',
                        href='/',
                        refresh=True)
    return obj


def link_finst():
    obj = dash.dcc.Link(dash.html.Button('Financial statement',
                                         id='button_link_to_finst',
                                         disabled=True,
                                         style=link_style()),
                        id='link_to_finst',
                        href='/finst')
    return obj


def link_indicator_comparison():
    obj = dash.dcc.Link(dash.html.Button('Indicator comparison',
                                         id='button_link_to_ind_comp',
                                         style=link_style()),
                        id='link_to_ind_comp',
                        href='/indcomp')
    return obj


def link_indicators_intersection():
    obj = dash.dcc.Link(dash.html.Button('Indicators intersection',
                                         id='button_link_to_ii',
                                         style=link_style()),
                        id='link_to_ii',
                        href='/ii')
    return obj


def link_data_table():
    obj = dash.dcc.Link(dash.html.Button('Data table',
                                         id='button_link_to_data_table',
                                         style=link_style()),
                        id='link_to_data_table',
                        href='/data_table')
    return obj


def link_score():
    obj = dash.dcc.Link(dash.html.Button('Score',
                                         id='button_link_to_score',
                                         style=link_style()),
                        id='link_to_score',
                        href='/score')
    return obj
