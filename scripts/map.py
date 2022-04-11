import json
import numpy as np
import pandas as pd
from plotly import graph_objs as go
import utilds_data as ud
from logzero import logger

def get_map_from_date(df_raw,date):

    df = df_raw.loc[df_raw["dt"]==date]

    return df

def get_yearly_data(df_raw):

    df = df_raw.loc[df_raw["year"]>=1900]
    df["AverageTemperature"] = df["AverageTemperature"].round(2)
    df["temp_diff"] = df["temp_diff"].round(2)
    #df = df.groupby(["year","Country"]).mean().reset_index()

    return df

def get_temperature_diff_between(df_by_year,start_date,end_date):

    df = df_by_year.loc[(df_by_year["year"] >= start_date) & 
                        (df_by_year["year"] <= end_date)].groupby(["Country"]).sum().reset_index()

    df["temp_diff"] = df["temp_diff"].round(2)
                  
    
    return df


def create_map(df,mapbox_token,geo_json,attribute):

    years = np.sort(df["year"].unique())
    plot_df = df[df["year"]==years[-1]]

    fig_data = go.Choroplethmapbox(
        geojson=geo_json,
        locations=plot_df["Country"],
        z=plot_df[attribute],
        zmin=df[attribute].min(),
        zmax=df[attribute].max(),
        customdata=plot_df[attribute],
        name="",
        text=plot_df["Country"],
        hovertemplate="%{text}<br>Average Temperature: %{customdata}°C",
        colorscale="YlOrRd",
        colorbar=dict(outlinewidth=1,
            outlinecolor="#333333",
            len=0.9,
            lenmode="fraction",
            xpad=30,
            xanchor="right",
            bgcolor=None,
            title=dict(text="Cases",
                        font=dict(size=14))
        )
            #tickvals=[0,1,2,3,4,5,6],
            #ticktext=["1", "10", "100", "1K", "10K", "100K", "1M"],
            #tickcolor="#333333",
            #tickwidth=2,
            #tickfont=dict(color="#333333",
            #                size=12)),
        #reversescale=True
    )

    fig_layout = go.Layout(
        mapbox_style="light",
        mapbox_accesstoken=mapbox_token,
        #mapbox_center={"lat": 37.0902, "lon": -95.7129},
        margin={"r":0,"t":0,"l":0,"b":0},
    )

    fig_layout["updatemenus"] = [dict(
        type="buttons",
        buttons=[dict(
            label="Play",
            method="animate",
            args=[None,
            dict(frame=dict(duration=300,
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
        #pad={"r": 10, "t": 35},
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
                        pad=dict(b=10,t=10),
                        len=0.875,
                        x=0,
                        y=0,
                        steps=[])
    
    fig_frames = []
    for year in years:
        plot_df = df[df["year"]==year]
        frame = go.Frame(data=[
            go.Choroplethmapbox(
                locations=plot_df["Country"],
                z=plot_df[attribute],
                customdata=plot_df[attribute],
                name="",
                text=plot_df["Country"],
        
            )],
            name=str(year))

        fig_frames.append(frame)

        slider_step = dict(
            args=[[str(year)],
            dict(mode="immediate",
            frame=dict(duration=500,
            redraw=True))],
            method="animate",
            label=str(year)
        )

        sliders_dict["steps"].append(slider_step)
        
    
    fig_layout.update(sliders=[sliders_dict])

    fig = go.Figure(data=fig_data, layout=fig_layout, frames=fig_frames)
        
    return fig

if __name__ == "__main__":

    #Get mapbox token
    mapbox_token = ud.config['mapbox']['token']
    raw_dataset_path = ud.RAW_PATH + ud.config['path']['name']
    geo_world = ud.RAW_PATH + ud.config['geoworld']['name']

    df_raw = pd.read_csv(raw_dataset_path)

    with open(geo_world) as world_file:
        world = json.load(world_file)

    df = get_yearly_data(df_raw)
    #Create the map figure

    #df = get_temperature_diff_between(df,1900,2000)
    fig_map = create_map(df,mapbox_token,world,"AverageTemperature")   


    save_map = {
        'figure':fig_map,
    }

    ud.save_pickle(save_map, 'map_info.p')

    logger.info('World map updated.')
    logger.info('Data stored for dash application.')

