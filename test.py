import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

#mapbox api token
mapbox_token = "pk.eyJ1IjoibTIwMjEwNjMzIiwiYSI6ImNsMW5yNGQ0bjB2OHgzY29ibWo5ZXoxbnIifQ.7h2zkrNJdHMVS9UiflpyVQ"

#Load dataset
df_countries = pd.read_csv("GlobalLandTemperaturesByCountry+GHG.csv")

world_path = 'custom.geo.json'
with open(world_path) as f:
    geo_world = json.load(f)

test_date = "2008-05-01"
#Working dataset
df = df_countries.loc[df_countries['dt']==test_date]

fig = go.Figure(
    go.Scattermapbox(
        lat=df['Latitude'],
        lon=df['Longitude'],
        mode='markers',
    )
)


# Specify layout information
fig.update_layout(
    mapbox=dict(
        accesstoken=mapbox_token,
        center=go.layout.mapbox.Center(lat=45, lon=-73),
        zoom=1
    )
)

fig.show()