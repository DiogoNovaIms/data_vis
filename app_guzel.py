import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

############################################################Data##############################################################

#path = r'C:\Users\bayaz\Documents\NOVA\Data Visualization\Project code'
path = ''

df = pd.read_csv(path + "GlobalLandTemperaturesByCountry_clean.csv")

disasters = pd.read_csv(path + 'Disasters.csv')

######################################################Interactive Components############################################

country_options = [dict(label=country, value=country) for country in df['Country'].unique()]

year_option = [dict(label=Year, value=Year) for Year in disasters['Year'].unique()]


dropdown_country = dcc.Dropdown(
        id='country_drop',
        options=country_options,
        value=['Afghanistan'],
        multi=True
    )

slider_year = dcc.Slider(
        id='year_slider',
        min=df['year'].min(),
        max=df['year'].max(),
        marks={str(i): '{}'.format(str(i)) for i in
               [1743, 1797, 1851, 1905, 1959, 2013]},
        value=df['year'].min(),
        step=1
    )
dropdown_year = dcc.Dropdown(
        id='year_option',
        options=year_option,
        value=disasters['Year'],
    )

radio_projection = dcc.RadioItems(
        id='projection',
        options=[dict(label='Equirectangular', value=0),
                 dict(label='Orthographic', value=1)],
        value=0
    )
##################################################APP###################################################################

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([

  html.Div([
        html.H1('Climate Change Dashboard'),
    ], id='1st row', className='pretty_box'),
  html.Div([
        html.Div([
            html.Label('Country Choice'),
            dropdown_country,
            html.Br(),
            html.Label('Projection'),
            radio_projection,
            html.Br(),
            html.Button('Submit', id='button')
        ], id='Iteraction', style={'width': '30%'}, className='pretty_box'),
  html.Div([
       html.Div([
           dcc.Graph(id='choropleth'),
            html.Label('Year Slider'),
            slider_year,
            html.Br(),
           ], id='Map', className='pretty_box')
       ], id='Else', style={'width': '70%'})
    ], id='2nd row', style={'display': 'flex'}),
  html.Div([
       html.Div([
            dcc.Graph(id='disasters'),
           ],id='Graph1', style={'width': '50%'}, className='pretty_box'),
       html.Div([
            html.Label('Year Drop'),
            dropdown_year,
            html.Br(),
       ])
  ])
])
######################################################Callbacks#########################################################
@app.callback(
    [
        Output("choropleth", "figure"),
        Output("disasters", "figure")
    ],
    [
        Input("button", "n_clicks")
    ],
    [
        State("projection", "value"),
        State("year_slider", "value"),
        State("year_option", "value")
    ]
)


def plots(n_clicks, projection, year, Year):
#############################################First Choropleth######################################################

    df_short = df.loc[(df['year'] == year)].groupby(['Country'])[['AverageTemperature']].mean().reset_index()

    z = df_short['AverageTemperature']

    data_choropleth = dict(type='choropleth',
                           locations=df_short['Country'],
                           locationmode='country names',
                           z=z,
                           text=df_short['Country'],
                           colorscale='inferno',
                           colorbar=dict(title='Average Temperature'),

                           hovertemplate='Country %{text} <br>''Average Temperature: %{z}',
                           name=''
                           )

    layout_choropleth = dict(geo=dict(scope='world',  # default
                                      projection=dict(type=['equirectangular', 'orthographic'][projection]
                                                      ),
                                      # showland=True,   # default = True
                                      landcolor='black',
                                      lakecolor='white',
                                      showocean=True,  # default = False
                                      oceancolor='azure',
                                      bgcolor='#f9f9f9'
                                      ),

                             title=dict(
                                 text='World Choropleth Map on the year ' + str(
                                     year),
                                 x=.5  # Title relative position according to the xaxis, range (0,1)

                             ),
                             paper_bgcolor='#f9f9f9'
                             )
############################################Second Plot##########################################################
    disasters_0 = disasters.loc[disasters['Year'] == Year]

    fig_disasters = px.scatter(disasters_0, x=disasters_0["AverageTemperature"], y=disasters_0["GHG"],
               size=disasters_0["Disasters"], color=disasters_0["continent"],
               hover_name=disasters_0["Country"], log_x=False, size_max=60)

    layout_disasters = dict(title=dict(text='All Natural Disasters from 1900 until 2021'),
                            xaxis=dict(title='Average Temperature'),
                            yaxis=dict(title="GHG Emission",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                      ))






    return go.Figure(data=data_choropleth, layout=layout_choropleth), \
           go.Figure(data=fig_disasters, layout=layout_disasters)



if __name__ == '__main__':
    app.run_server(debug=True)


  