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

    df = df_raw.loc[df_raw["year"]>=1900]
    df = df.groupby(["year","Country"]).mean().reset_index()


    return df

def create_map(df,mapbox_token,geo_json):

    years = np.sort(df["year"].unique())
    plot_df = df[df["year"]==years[-1]]

    fig_data = go.Choroplethmapbox(
        geojson=geo_json,
        locations=plot_df["Country"],
        z=plot_df["AverageTemperature"],
        zmin=df["AverageTemperature"].min(),
        zmax=df["AverageTemperature"].max(),
        customdata=plot_df["AverageTemperature"],
        name="",
        text=plot_df["Country"],
        colorscale="RdBu",
        reversescale=True
    )

    fig_layout = go.Layout(
        mapbox_style="light",
        mapbox_accesstoken=mapbox_token,
        mapbox_center={"lat": 37.0902, "lon": -95.7129},
        margin={"r":0,"t":0,"l":0,"b":0},
    )

    fig_layout["updatemenus"] = [dict(
        type="buttons",
        buttons=[dict(
            label="Play",
            method="animate",
            args=[None,
            dict(frame=dict(duration=1000,
            redraw=True),fromcurrent=True)]
        ),
        dict(
            label="Pause",
            method="animate",
            args=[[None],
            dict(frame=dict(duration=0,
            redraw=True),
            mode="immediate")]
        )],
        direction="left",
        pad={"r": 10, "t": 35},
        showactive=False,
        x=0.1,
        xanchor="right",
        y=0,
        yanchor="top"
    )]

    
    sliders_dict = dict(active=len(years) - 1,
                        visible=True,
                        yanchor="top",
                        xanchor="left",
                        currentvalue=dict(font=dict(size=20),
                                        prefix="Date: ",
                                        visible=True,
                                        xanchor="right"),
                        pad=dict(b=10,
                                t=10),
                        len=0.875,
                        x=0.125,
                        y=0,
                        steps=[])
    
    fig_frames = []
    for year in years:
        plot_df = df[df["year"]==year]
        frame = go.Frame(data=[
            go.Choroplethmapbox(
                locations=plot_df["Country"],
                z=plot_df["AverageTemperature"],
                customdata=plot_df["AverageTemperature"],
                name="",
                text=plot_df["Country"]
            )],
            name=str(year))

        fig_frames.append(frame)

        slider_step = dict(
            args=[[str(year)],
            dict(mode="immediate",
            frame=dict(duration=100,
            redraw=True))],
            method="animate",
            label=str(year)
        )

        sliders_dict["steps"].append(slider_step)
        
    
    fig_layout.update(sliders=[sliders_dict])

    fig = go.Figure(data=fig_data, layout=fig_layout, frames=fig_frames)
        
    return fig

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
    fig_map = create_map(df,mapbox_token,world)   

    save_map = {
        'figure':fig_map,
    }

    ud.save_pickle(save_map, 'map_info.p')

    logger.info('World map updated.')
    logger.info('Data stored for dash application.')

