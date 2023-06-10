import dash


def link_main():
    obj = dash.dcc.Link(dash.html.Button('Main'), id='main_page_link', href='/', refresh=True)
    return obj


def link_finst():
    obj = dash.dcc.Link(dash.html.Button('Financial statement', id='button_link_to_finst', disabled=True), id='link_to_finst', href='/finst')
    return obj


def link_indicator_comparison():
    obj = dash.dcc.Link(dash.html.Button('Indicator comparison', id='button_link_to_ind_comp'), id='link_to_ind_comp', href='/indcomp')
    return obj



