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

df = pd.read_csv(path + "GlobalLandTemperaturesByCountry+GHG.csv")

disasters = pd.read_csv(path + 'Disasters.csv')

nat_dis = pd.read_csv(path + '1900_2021_DISASTERS.xlsx - emdat data.csv')

######################################################Interactive Components############################################

country_options = [dict(label=country, value=country) for country in df['Country'].unique()]

year_option = [dict(label=Year, value=Year) for Year in disasters['Year'].unique()]

disaster_option = [dict(label=disaster, value=disaster) for disaster in nat_dis['Disaster Type'].unique()]


dropdown_country = dcc.Dropdown(
        id='country_drop',
        options=country_options,
        value=['Portugal'],
        multi=True
    )

radio_disaster_option = dcc.RadioItems(
    id='disaster_types',
    options=disaster_option,
    value="Drought",
    labelStyle={'display': 'block', "text-align": "justify"}

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
        value=disasters["Year"]
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
            html.Label('Year'),
            dropdown_year,
            html.Br(),
            html.Label('Projection'),
            radio_projection,
            html.Br(),
            html.P("Select a disaster category", className="control_label",style={"text-align": "center","font-weight":"bold"}),
                        radio_disaster_option,
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
            dcc.Graph(id='bar_graph1'),
           ], id='Graph2', style={'width': '100%'}, className='pretty_box'),
       html.Div([
            dcc.Graph(id='bar_graph2'),
           ], id='Graph3', style={'width': '100%'}, className='pretty_box'),
       ])
  ])

######################################################Callbacks#########################################################
@app.callback(
    [
        Output("choropleth", "figure"),
        Output("disasters", "figure"),
        Output("bar_graph1", "figure"),
        Output("bar_graph2", "figure")
    ],
    [
        Input("button", "n_clicks")
    ],
    [
        State("projection", "value"),
        State("year_slider", "value"),
        State("year_option", "value"),
        State("country_drop", "value")
    ]
)


def plots(n_clicks, projection, year, Year, countries):
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

############################################Third Bar Plot##########################################################

    data_bar = []
    for country in countries:
        df_bar = df.loc[(df['Country'] == country)]

        x_bar = df_bar['year']
        y_bar = df_bar["AverageTemperature"]

        data_bar.append(dict(type='bar', x=x_bar, y=y_bar, name=country))

    layout_bar = dict(title=dict(text='Average Temperature from 1743 to 2013'),
                      yaxis=dict(title='Average Temperature'),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)'
                      )

############################################Fourth Bar Plot##########################################################

    df_bar = df.loc[(df['year'] == year)].groupby(['Country'])[["GHG", "AverageTemperature"]].mean().reset_index()

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_bar["Country"],
        y=np.log(df_bar["GHG"]),
        name="GHG EMission",
        marker_color='#0d0887'
    ))

    fig_bar.add_trace(go.Bar(
        x=df_bar["Country"],
        y=df_bar["AverageTemperature"],
        name="Average Temperature",
        marker_color='#fdca26'
    ))


    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig_bar.update_layout(barmode='group', xaxis_tickangle=-45)
    fig_bar.update_layout(plot_bgcolor='white')
    fig_bar.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey')
    fig_bar.update_xaxes(showline=True, linewidth=2, linecolor='black')

    return go.Figure(data=data_choropleth, layout=layout_choropleth), \
           go.Figure(data=fig_disasters, layout=layout_disasters), \
           go.Figure(data=data_bar, layout=layout_bar), \
           go.Figure(data=fig_bar)




if __name__ == '__main__':
    app.run_server(debug=True)


  