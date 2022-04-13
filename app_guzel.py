#General
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px

#Dash
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

#Logging info
from logzero import logger

#for custom scripts
import scripts.utilds_data as ud

#Date
from datetime import date

############################################################Data##############################################################


raw_dataset_path = ud.RAW_PATH + ud.config['path']['correlation']
df = pd.read_csv(raw_dataset_path)


######################################################Interactive Components############################################


slider_year = dcc.RangeSlider(
        id='year_slider',
        min=df['year'].min(),
        max=df['year'].max(),
        marks={str(i): '{}'.format(str(i)) for i in
               [1960, 1970, 1980, 1990, 2000, 2013]},
        value=[1970, 2000],
        step=1
    )

##################################################APP###################################################################

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([

    html.Div([
        html.Div([
            dcc.Graph(id='correlation_graph'),
        ], id='Graph1', style={'width': '50%'}, className='pretty_box'),
    ], id='3th row', style={'display': 'flex'}),
    html.Div([
            html.Br(),
                html.Label('Year Range Slider'),
                slider_year
    ], style={'width': '50%'})
])



######################################################Callbacks#########################################################

@app.callback(
    [
        Output("correlation_graph", "figure"),
    ],
    [
        Input("year_slider", "value"),
        Input("year_slider", "value")
    ]
)

def plots(start_date, end_date):
############################################First Bar Plot##########################################################

    df_0 = df.loc[(df["year"] >= start_date) &
                        (df["year"] <= end_date)].groupby(["Country", "continent"]).agg(
        {"gdp": np.sum, "AverageTemperature": np.mean, "GHG": np.sum, "temp_diff": np.sum}).reset_index()



    corr_fig = px.scatter(df_0, x="temp_diff", y="GHG", color="continent", template="simple_white", hover_name="Country",
                             size="gdp_test", size_max=80,
                             labels={
                                 "temp_diff": "Increase in average temperature",
                                 "GHG": "Greenhouse Gases Emissions"

                             },)

    corr_layout = dict(title=dict(text='Correlation between average temperature difference and GHG Emissions '),
                                    xaxis=dict(title='Average Temperature'),
                                    yaxis=dict(title="GHG Emission",
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)'
                              ))

    return go.Figure(data=corr_fig, layout=corr_layout)

if __name__ == '__main__':
    app.run_server(debug=True)



