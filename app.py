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

disasters_path = ud.RAW_PATH + ud.config['path']['disasters']
df_disasters = pd.read_csv(disasters_path)



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
        html.H3('Worldwide Average Temperature Evolution from 1900 to 2010'),
        dcc.Graph(
            id='map',
            figure=world['figure'],
            style={'height':'97%','width':'93.5vw'}
        ),
    ],className='first_row_containers',
),
        html.Div([
            html.Div([
                dcc.Graph(id='correlation_graph'),
                slider_year,
            ], id='Graph1',className="second_row_containers"),
            html.Div([
                dcc.Dropdown(
                    options=[{'label': c, 'value': c}
                              for c in (df_disasters['Country'].unique())],
                    value='World',
                id = 'dropdown_countries',
                ),
                dcc.Graph(id='disasters_graph',
                style={'height':'60vh'}),
            ], id='Graph2',className="second_row_containers"),
        ], id='3rd row'),

    html.Div(
        [
            html.H3("Authors", style={"margin-top": "0", "text-align": "center"}),

            html.P(
                "Diogo Hipólito (m20210633@novaims.unl.pt)  -  Guzel Bayazitova (m20210699novaims.unl.pt)  -  Jessica Routzahn (m20210987@novaims.unl.pt)  -  Mohamed Ali Felfel (m20211322@novaims.unl.pt)",
                style={"text-align": "center", "font-size": "10pt"}),

        ],
        className="pretty_container",
    ),
    html.Div(
        [
            html.H3("Sources", style={"margin-top": "0", "text-align": "center"}),
            dcc.Markdown(
                """\
                     - Climate Change: Earth Surface Temperature Data: https://www.kaggle.com/datasets/berkeleyearth/climate-change-earth-surface-temperature-data?select=GlobalLandTemperaturesByCity.csv
                     - CO2 and GHG emission data: https://www.kaggle.com/datasets/srikantsahu/co2-and-ghg-emission-data
                     - ALL NATURAL DISASTERS 1900-2021 / EOSDIS: https://www.kaggle.com/datasets/brsdincer/all-natural-disasters-19002021-eosdis
                    """
                , style={"font-size": "10pt"}),

        ],
        className="pretty_container",
    ),
           

        #html.Img(
            #src=app.get_asset_url("colorbar.png"),
            #style={'height':'50%','width':'70%','textAlign':'center'}
            #)
    ], )



######################################################Callbacks#########################################################
@app.callback(
    dash.dependencies.Output("disasters_graph", 'figure'),
    [dash.dependencies.Input('dropdown_countries', 'value')
    ]
)
def update_disasters_graph(country):

    df_country = df_disasters.loc[df_disasters["Country"]==country]
    
    fig_data = px.bar(df_country, x="Year", y="Count", color="Disaster Type",title="Natural Disasters frequency: " + str(country),
        category_orders={"Disaster Type": ["Flood","Storm","Earthquake","Epidemic","Landslide","Animal accident"]}, range_x=[1979,2022])
    
    fig_layout = dict(#xaxis=dict(title='Average Temperature'),
                       yaxis=dict(title="",
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)'
                              ))

    return go.Figure(data=fig_data,layout=fig_layout)



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


    corr_fig = px.scatter(df_0, x="temp_diff", y="GHG", size="gdp_test", color="continent", title='Correlation between average temperature difference and GHG Emissions',
           hover_name="Country", log_x=False, size_max=100, range_x =[-3,5],
                  labels={
                     "temp_diff": "Increase in average temperature between " + str(year[0]) + " and " + str(year[1]),
                     "GHG": "Greenhouse Gases Emissions"
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

    return go.Figure(data=corr_fig, layout=corr_layout)

####################
if __name__ == '__main__':
    app.run_server(debug=True)
####################