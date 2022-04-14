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
mapbox_access_token = "pk.eyJ1IjoibTIwMjEwNjMzIiwiYSI6ImNsMW5yNGQ0bjB2OHgzY29ibWo5ZXoxbnIifQ.7h2zkrNJdHMVS9UiflpyVQ"

data = [
    go.Scattermapbox(
        lat=['45.5017'],
        lon=['-73.5673'],
        mode='markers',
        marker=dict(
            size=14
        ),
        name='mapbox 1',
        text=['Montreal'],
        subplot='mapbox'
    ),
    go.Scattermapbox(
        lat=['45.7'],
        lon=['-73.7'],
        mode='markers',
        marker=dict(
            size=14
        ),
        name='mapbox 1',
        text=['Montreal 2'],
        subplot='mapbox'
    ),
    go.Scatter(
        y=[1, 3, 2],
        xaxis='x',
        yaxis='y',
        name='scatter 1'
    ),
    go.Scatter(
        y=[3, 2, 1],
        xaxis='x',
        yaxis='y',
        name='scatter 2'
    ),
    go.Bar(
        y=[1, 2, 3],
        xaxis='x2',
        yaxis='y2',
        name='scatter 3'
    ),
    go.Scatter(
        y=[3, 2, 1],
        xaxis='x2',
        yaxis='y2',
        name='scatter 4'
    ),
]

layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=45,
            lon=-73
        ),
        pitch=0,
        zoom=5,
        domain={
            'x': [0.3, 0.6],
            'y': [0.7, 1.0]
        }
    ),
    xaxis={
        'domain': [0.3, 0.6]
    },
    yaxis={
        'domain': [0.36, 0.6]
    },
    xaxis2={
        'domain': [0.3, 0.6],
        'side': 'bottom',
        'anchor': 'y2'
    },
    yaxis2={
        'domain': [0, 0.3],
        'anchor': 'x2'
    },
    height=700,
    width=700
)

fig = go.Figure(data=data, layout=layout)
fig.show()