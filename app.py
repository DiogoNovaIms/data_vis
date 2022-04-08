#General
import plotly.graph_objects as go
import pandas as pd
import numpy as np

#Dash
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

#Logging info
import logging
import logzero
from logzero import logger

#for custom scripts
import scripts.utilds_data as ud

world = ud.load_pickle("map_info.p")



#WHATEVER YOU DO, DO NOT DELETE THIS
app = dash.Dash(__name__)
server = app.server
###################################

app.layout = html.Div([
    dcc.Graph(
        id='map',
        figure=world['figure'],
        config={'scrollZoom': False},
        style={'width': '100vw', 'height': '100vh'}
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