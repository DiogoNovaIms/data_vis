import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import scripts.utilds_data as ud
############################################################Data##############################################################

#path = r'C:\Users\bayaz\Documents\NOVA\Data Visualization\Project code'
path = ''

raw_dataset_path = ud.RAW_PATH + ud.config['path']['name']
df = pd.read_csv(raw_dataset_path)

######################################################Interactive Components############################################

country_options = [dict(label=country, value=country) for country in df['Country'].unique()]

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
            html.Label('Year Slider'),
            slider_year,
            html.Br(),
            html.Label('Projection'),
            radio_projection,
            html.Br(),
            html.Button('Submit', id='button')
        ], id='Iteraction', style={'width': '30%'}, className='pretty_box'),
  html.Div([
       html.Div([
           dcc.Graph(id='choropleth'),
           ], id='Map', className='pretty_box')
       ], id='Else', style={'width': '70%'})
    ], id='2nd row', style={'display': 'flex'})
])
######################################################Callbacks#########################################################
@app.callback(
        Output("choropleth", "figure"),
    [
        Input("button", "n_clicks")
    ],
    [
        State("projection", "value"),
        State("year_slider", "value"),
    ]
)

#############################################Second Choropleth######################################################
def plots(n_clicks, projection, year):

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
    return go.Figure(data=data_choropleth, layout=layout_choropleth)


if __name__ == '__main__':
    app.run_server(debug=True)


  