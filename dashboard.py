import pandas as pd
import utilities as u
import warnings

import time
import dash


from tickerclass import Ticker


def dashboard():
    warnings.simplefilter("always")
    u.pandas_df_display_options()
    tickers_list = ['GOOGL', 'META', 'NFLX']                                                   #dodac jako argument
    wsj_cursor, wsj_conn, wsj_engine = u.create_sql_connection('wsj')
    wsja_cursor, wsja_conn, wsja_engine = u.create_sql_connection('wsja')
    tic = Ticker(tickers_list[1], wsj_cursor, wsj_conn, wsj_engine, wsja_cursor, wsja_conn, wsja_engine)
    tic.set_df_year()
    tic.set_df_quarter()
    tic.set_income_statment_df_year()
    tic.set_income_statment_df_quarter()


    app = dash.Dash(__name__, pages_folder='', use_pages=True)
    dash.register_page('home', layout = dash.html.Div([
        dash.html.H1('Multi-page app with Dash Pages'),

        dash.html.Div(
            [
                dash.html.Div(
                    dash.dcc.Link(
                        f"{page['name']} - {page['path']}", href=page["relative_path"]
                    )
                )
                for page in dash.page_registry.values()
            ]
        ),

        dash.page_container
    ]))

    dash.register_page('analysis parameters',
    layout = dash.dash_table.DataTable(tic.df_y.to_dict('records'), [{"name": i, "id": i} for i in tic.df_y.columns])
                       )

    dash.register_page('income_statement',
    layout = dash.dash_table.DataTable(tic.is_df_y.to_dict('records'),
                                           [{"name": i, "id": i} for i in tic.is_df_y.columns])
    #layout = dash.dash_table.DataTable(tic.is_df_q.to_dict('records'),
    #                                       [{"name": i, "id": i} for i in tic.is_df_q.columns])
    )



    app.run_server(debug=True)











    #indicators_dict = get_indicators_dict(wsj_conn)
    #sql_analysis_tables = get_all_analysis_tables(cursor)
    #adb = AnalysisDatabase(tickers_list, indicators_dict, wsj_conn)
    #print(adb.META.tables.year)
    #print(adb.META.get_df(wsj_conn))






start_time = time.time()
dashboard()
end_time = time.time()
print(end_time - start_time)


