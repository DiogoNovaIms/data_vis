#General
import plotly.graph_objects as go
import pandas as pd
import numpy as np

#Dash
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px


#Logging info
from logzero import logger

#for custom scripts
import scripts.utilds_data as ud

#Date
from datetime import date

world = ud.load_pickle("map_info.p")
raw_dataset_path = ud.RAW_PATH + ud.config['path']['correlation']
df = pd.read_csv(raw_dataset_path)



#WHATEVER YOU DO, DO NOT DELETE THIS
app = dash.Dash(__name__)
server = app.server
###################################




slider_year = dcc.RangeSlider(
        id='year_slider',
        min=df['year'].min(),
        max=df['year'].max(),
        marks={str(i): '{}'.format(str(i)) for i in
               [1960, 1970, 1980, 1990, 2000, 2013]},
        value=[1960, 2013],
        step=1,
    )



app.layout = html.Div([

    html.Div([
            html.H1('Global Temperature and its fatal effect on the Climate Change'),
        ], id='1st row', style={'textAlign': 'center'}, className='pretty_box'),
    html.Br(),
        html.Div([
            html.Div([
                html.H3('Disasters and GDP per country'),
            ], id='2nd row', style={'width': '20%'}, className='pretty_box'),
                html.Div(id='output-container-date-picker-single'),
                html.H3('Worldwide Greenhouse Gases Emissions from 1900 to 2013 years '),
                ], id='title_map', style={'textAlign': 'center'}, className='pretty_box'),
                html.Div([
                    dcc.Graph(
                        id='map',
                        figure=world['figure'],
                        style={'width':'99vw','height':'97vh'}
                    ),
        ]),

    html.Br(),
        html.Div([
            html.Div([
                html.H3('Correlation between average temperature difference and GHG Emissions'),
                    ], id='3d row', className='pretty_box'),
                html.Div([
                    dcc.Graph(id='correlation_graph'),
                ], id='Graph1', style={'width': '50%'}, className='pretty_box'),
            ], id='3th row'),
                html.Div([
                        html.Br(),
                            html.Label('Year Range Slider'),
                            slider_year
        ], style={'width': '45%'})

        #html.Img(
            #src=app.get_asset_url("colorbar.png"),
            #style={'height':'50%','width':'70%','textAlign':'center'}
            #)
    ])



######################################################Callbacks#########################################################

@app.callback(
    dash.dependencies.Output("correlation_graph", 'figure'),
    [dash.dependencies.Input('year_slider', 'value')
    ])
def update_graph(year):
    df_0 = df.loc[(df["year"] >= year[0]) &
                  (df["year"] <= year[1])].groupby(["Country", "continent"]).agg(
        {"gdp": np.sum, "AverageTemperature": np.mean, "GHG": np.sum, "temp_diff": np.sum}).reset_index()

    df_0["gdp_test"] = df_0["gdp"] * 2

############################################First Bar Plot##########################################################


    corr_fig = px.scatter(df_0, x="temp_diff", y="GHG", size="gdp_test", color="continent",
           hover_name="Country", log_x=False, log_y=True, size_max=100, range_x =[-3,5],
                  labels={
                     "temp_diff": "Increase in average temperature between " + str(year[0]) + " and " + str(year[1]),
                     "GHG": "Greenhouse Gases Emissions (log10 scale)"
                      }, custom_data=['Country', 'gdp'])

    corr_fig.add_vline(x=0,line_width=1, line_dash="dash",opacity=0.7)


    corr_layout = dict(xaxis=dict(title='Average Temperature'),
                       yaxis=dict(title="GHG Emission",
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)'
                              ))

    corr_fig.update_traces(
        hovertemplate="<br>".join([
            "Country: %{customdata[0]}",
            "GDP: %{customdata[1]}",
            "Increase in average temperature: %{x}",
            "Greenhouse Gases Emissions: %{y}",
        ])
    )

    corr_fig.update_yaxes(type="log", range=[0, 20])  # log range: 10^0=1, 10^20=100000000000000000000

    return go.Figure(data=corr_fig, layout=corr_layout)

####################
if __name__ == '__main__':
    app.run_server(debug=True)
####################