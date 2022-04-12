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
from logzero import logger

#for custom scripts
import scripts.utilds_data as ud

#Date
from datetime import date

world = ud.load_pickle("map_info.p")



#WHATEVER YOU DO, DO NOT DELETE THIS
app = dash.Dash(__name__)
server = app.server
###################################

app.layout = html.Div([
    html.Div(id='output-container-date-picker-single'),
    dcc.Graph(
        id='map',
        figure=world['figure'],
        style={'width':'99vw','height':'97vh'}
    ),
    
    #html.Img(
        #src=app.get_asset_url("colorbar.png"),
        #style={'height':'50%','width':'70%','textAlign':'center'}
        #)
])


#@app.callback(
#    Output('map', 'children'),
#    Input('my-date-picker-single', 'date'))

#def update_output_div(input_value):
#    return 'You\'ve entered "{}"'.format(input_value)

####################
if __name__ == '__main__':
    app.run_server(debug=True)
####################