import json
import numpy as np
import pandas as pd
from plotly import graph_objs as go
import plotly.express as px
import utilds_data as ud
from logzero import logger

def get_map_from_date(df_raw,date):

    df = df_raw.loc[df_raw["dt"]==date]

    return df

def get_yearly_data(df_raw):

    df = df_raw.groupby(["year","Country"]).mean().reset_index()


    return df

def create_map_fig_old(df,mapbox_token,world):

    

    fig = px.choropleth_mapbox(
        df,
        geojson=world,
        locations='Country',
        color=df['AverageTemperature'],
        color_continuous_scale='YlOrRd',
        range_color=(0, df['AverageTemperature'].max()),
        hover_name='Country',
        hover_data={'GHG': False, 'Country': False, 'AverageTemperature': True},
        zoom=1,
        center={'lat': 19, 'lon': 11},
        opacity=0.6,
        mapbox_style='open-street-map',

    )

    return fig

    # Global Layout
    layout = go.Layout(
        height=600,
        autosize=True,
        hovermode='closest',
        paper_bgcolor='rgba(0,0,0,0)',
        mapbox={
            'accesstoken':mapbox_token,
            'bearing':0,
            'center':{"lat": 37.86, "lon": 2.15},
            'pitch':0,
            'zoom':1.7,
            'style':'light',
        },
        margin={"r":0,"t":0,"l":0,"b":0}
    )

def create_map_fig(df,mapbox_token,world):

    years= df["year"].unique().tolist()

    frames = [{
        'name':'frame_{}'.format(year),
        'data':[{
            'type':'choroplethmapbox',
            'geojson':world,
            'featureidkey':'properties.name_long',
            'locations':df.xs(year).index.tolist(),
            'colorscale':'YlOrRd',
            'z':[20,20,180]
        }]
    } for year in years]

    
    data = frames[-1]['data']

    active_frame = len(years)-1

    # Slider to navigate between frames
    sliders = [{
        'active':active_frame,
        'transition':{'duration': 0},
        'x':0.08,     #slider starting position  
        'len':0.88,
        'currentvalue':{
            'font':{'size':15}, 
            'prefix':'📅', # Day:
            'visible':True, 
            'xanchor':'center'
            },  
        'steps':[{
            'method':'animate',
            'args':[
                ['frame_{}'.format(year)],
                {
                    'mode':'immediate',
                    'frame':{'duration':250, 'redraw': True}, #100
                    'transition':{'duration':100} #50
                }
                ],
            'label':year
        } for year in years]
    }]

    #Play button
    play_button = [{
        'type':'buttons',
        'showactive':True,
        'y':-0.08,
        'x':0.045,
        'buttons':[{
            'label':'🎬', # Play
            'method':'animate',
            'args':[
                None,
                {
                    'frame':{'duration':250, 'redraw':True}, #100
                    'transition':{'duration':100}, #50
                    'fromcurrent':True,
                    'mode':'immediate',
                }
            ]
        }]
    }]

    # Global Layout
    layout = go.Layout(
        height=600,
        autosize=True,
        hovermode='closest',
        paper_bgcolor='rgba(0,0,0,0)',
        mapbox={
            'accesstoken':mapbox_token,
            'bearing':0,
            'center':{"lat": 37.86, "lon": 2.15},
            'pitch':0,
            'zoom':1.7,
            'style':'light',
        },
        updatemenus=play_button,
        sliders=sliders,
        margin={"r":0,"t":0,"l":0,"b":0}
    )


    return go.Figure(data=data,layout=layout,frames=frames)

if __name__ == "__main__":

    #Get mapbox token
    mapbox_token = ud.config['mapbox']['token']
    raw_dataset_path = ud.RAW_PATH + ud.config['path']['name']
    geo_world = ud.RAW_PATH + ud.config['geoworld']['name']

    df_raw = pd.read_csv(raw_dataset_path)

    with open(geo_world) as world_file:
        world = json.load(world_file)

    #date = "1990-09-01"
    #df = get_map_from_date(df_raw,date)

    df = get_yearly_data(df_raw)
    #Create the map figure
    fig_map = create_map_fig(df,mapbox_token,world)   

    save_map = {
        'figure':fig_map,
    }

    ud.save_pickle(save_map, 'map_info.p')

    logger.info('World map updated.')
    logger.info('Data stored for dash application.')

