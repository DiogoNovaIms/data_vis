from turtle import width
from click import style
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np


# Datasets

df_countries = pd.read_csv("GlobalLandTemperaturesByCountry_clean.csv")

#Countries list
countries = np.unique(df_countries['Country'])

#
avg_temp = []
for country in countries:
    avg_temp.append(df_countries.loc[(df_countries['Country'] == country) & 
    (df_countries['year']==2008)]['AverageTemperature'].mean())

# World map
data = [ dict(
        type = 'choropleth',
        locations = countries,
        z = avg_temp,
        locationmode = 'country names',
        text = countries,
        #marker = dict(
            #line = dict(color = 'rgb(0,0,0)', width = 1)),
            #colorbar = dict(autotick = True, tickprefix = '',
            #title = '# Average\nTemperature,\n°C'),
        #The following line is also needed to create Stream
        #stream = stream_id
            )
       ]

layout = dict(
    #title = 'Average land temperature in countries 2',
    geo = dict(
        showframe = False,
        showocean = True,
        oceancolor = 'rgb(0,255,255)',
        type = 'equirectangular',
        autosize=False,
    ),
)

fig = dict(data=data, layout=layout)

#WHATEVER YOU DO, DO NOT DELETE THIS
app = dash.Dash(__name__)
server = app.server
###################################

app.layout = html.Div([
    dcc.Graph(
        id='example-graph',
        figure=fig,
    )
])


#@app.callback(
#    Output(component_id='div', component_property='children'),
#    [Input(component_id='input', component_property='value')]
#)
#def update_output_div(input_value):
#    return 'You\'ve entered "{}"'.format(input_value)

####################
if __name__ == '__main__':
    app.run_server(debug=True)
####################