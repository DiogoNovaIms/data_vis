import json
import numpy as np
import pandas as pd
from plotly import graph_objs as go
import utilds_data as ud
from logzero import logger
from plotly.subplots import make_subplots
from PIL import Image

def get_yearly_data(df_raw):

    df = df_raw.loc[df_raw["year"]>=1900]
    df["AverageTemperature"] = df["AverageTemperature"].round(2)
    df["temp_diff"] = df["temp_diff"].round(2)
    df["GHG"] = df["GHG"].round(2)
    df["GHG"] = df["GHG"].fillna(0)

    #df = df.groupby(["year","Country"]).mean().reset_index()

    return df

def get_temperature_diff_between(df_by_year,start_date,end_date):

    df = df_by_year.loc[(df_by_year["year"] >= start_date) & 
                        (df_by_year["year"] <= end_date)].groupby(["Country"]).sum().reset_index()

    df["temp_diff"] = df["temp_diff"].round(2)
                  
    
    return df

def create_final(df,mapbox_token,geo_json,attribute):
    fig = go.Figure

    years = np.sort(df["year"].unique())
    plot_df = df[df["year"]==years[-1]]
    bar_df = plot_df.nlargest(10,"GHG")

    hottest_temperature = plot_df["AverageTemperature"].max()
    hottest_data = plot_df.loc[plot_df["AverageTemperature"]==hottest_temperature]

    data = [
        go.Choroplethmapbox(
        geojson=geo_json,
        locations=plot_df["Country"],
        z=plot_df[attribute],
        zmin=-40,
        zmax=40,
        customdata=plot_df[attribute],
        text=plot_df["Country"],
        hovertemplate="%{text}<br>Average Temperature: %{customdata}°C",
        colorscale="RdBu",
        reversescale=True,
        showscale=False,
        subplot="mapbox",
        name="choroplethmapbox",
        colorbar=dict(outlinewidth=1,
            outlinecolor="#333333",
            len=0.9,
            lenmode="fraction",
            orientation="h",
            xanchor="center",
            yanchor="bottom",
            bgcolor=None,
            y=0.05,
            #title=dict(text="Cases",
            #            font=dict(size=14))
        )
    ),

    go.Scattermapbox(
        lat = plot_df["Latitude"],
        lon = plot_df["Longitude"],
        mode = "markers+text",
        marker=go.scattermapbox.Marker(
            size= plot_df["GHG"]*300/df["GHG"].max(),
            sizemin=2,
            opacity=0.7,
            color = "rgb(235,0,100)",
        ),
        text=plot_df["Country"],
        subplot="mapbox",
        name="scattermapbox",
    ),

    go.Bar(
        x = bar_df["GHG"],
        y = bar_df["Country"],
        orientation="h",
        xaxis="x",
        yaxis="y",
        name="bar",
        textposition='outside',
        cliponaxis=False,
        texttemplate='%{x}<br>%{y}',
    ),

    go.Table(
        header = dict(values=[["Hottest Country"]],
                      fill_color='white',
                      font=dict(color='black', size=15),),
        cells = dict(values=[[hottest_data["Country"] +" (" + str(hottest_temperature)+" C°)" ]], 
        align="center",
        fill_color="white"),
        name = "table",
        domain = dict(x=[0.30,0.49],
                      y=[0.1,0.2])
    )
    ]

    layout = go.Layout(
        autosize=True,
        showlegend=False,
        hovermode="closest",
        plot_bgcolor='rgba(0,0,0,0)',
        margin = dict(
            l = 0,        # left
            r = 0,        # right
            t = 0,        # top
            b = 0,        # bottom
        ),
        mapbox=dict(

            style="light",
            accesstoken=mapbox_token,
            bearing=0,
            pitch=0,
            domain={
                'x': [0.2, 1],
                'y': [0.2, 1]
            }

        ),

        xaxis={
            'domain': [0, 0.15],
            'range': [0,df["GHG"].max()]
        },

        yaxis={
            'domain': [0.6, 1],
            'tickmode': 'linear',
            'visible': False,
            'showticklabels':False,
        },
    )

    #Update menus
    layout["updatemenus"] = [dict(
        type="buttons",
        buttons=[dict(
            label="Play",
            method="animate",
            args=[None,
            dict(frame=dict(duration=250,
            redraw=True),fromcurrent=True),dict(transition=dict(duration=0,redraw=True),fromCurrent=True)]
        ),
        dict(
            label="Pause",
            method="animate",
            args=[[None],
            dict(frame=dict(duration=0,
            redraw=True),
            mode="immediate")]
        )],
        direction="right",
        pad={"r":150,"t": 40},
        showactive=False,
        x=0.2,
        xanchor="right",
        y=0,
        yanchor="top"
    )]

    sliders_dict = dict(active=len(years) - 1,
                        visible=True,
                        yanchor="bottom",
                        xanchor="left",
                        currentvalue=dict(font=dict(size=20),
                                        prefix="Date: ",
                                        visible=True,
                                        xanchor="right"),
                        pad=dict(b=300,l=150),
                        len=0.975,
                        x=0,
                        y=0,
                        steps=[])
    
    fig_frames = []
    steps = []
    for year in years:#range(years[0],years[-1],10):
        plot_df = df[df["year"]==year]
        bar_df = plot_df.nlargest(10,"GHG")
        hottest_temperature = plot_df["AverageTemperature"].max()
        hottest_data = plot_df.loc[plot_df["AverageTemperature"]==hottest_temperature]

        frame = go.Frame(data=[
            go.Choroplethmapbox(
                locations=plot_df["Country"],
                z=plot_df[attribute],
                customdata=plot_df[attribute],
                #name="",
                text=plot_df["Country"],
                #showscale=False,
            ),
            go.Scattermapbox(
                lat = plot_df["Latitude"],
                lon = plot_df["Longitude"],
                mode = "markers+text",
                marker=go.scattermapbox.Marker(
                    size= plot_df["GHG"]*300/df["GHG"].max(),
                    sizemin=2,
                    opacity=0.7
                ),
                text=plot_df["Country"],
                marker_color = "rgb(235,0,100)",
            ),
            go.Bar(
                x = bar_df["GHG"],
                y = bar_df["Country"],
                orientation="h",
            ),
            go.Table(
                header = dict(values=[["Hottest Country"]]),
                cells = dict(values=[[hottest_data["Country"] +" (" + str(hottest_temperature)+" C°)" ]],
                align="center"),
            ),

            ],
            name=str(year),
            traces = [0, 1, 2, 3])

        fig_frames.append(frame)

        slider_step = dict(
            args=[[str(year)],
            dict(mode="immediate",
            frame=dict(duration=500,
            redraw=True))],
            method="animate",
            label=str(year)
        )

        steps.append(slider_step)

    sliders_dict["steps"] = steps

    layout.update(sliders=[sliders_dict])

    fig = go.Figure(data=data,layout=layout,frames=fig_frames)

    return fig

def create_final_no_bar(df,mapbox_token,geo_json,attribute,df_global):

    years = np.sort(df["year"].unique())
    plot_df = df[df["year"]==years[-1]]

    hottest_temperature = plot_df["AverageTemperature"].max()
    hottest_data = plot_df.loc[plot_df["AverageTemperature"]==hottest_temperature]

    coldest_temperature = plot_df["AverageTemperature"].min()
    coldest_data = plot_df.loc[plot_df["AverageTemperature"]==coldest_temperature]

    most_emissions = plot_df["GHG"].max()
    most_emissions_data = plot_df.loc[plot_df["GHG"]==most_emissions]

    plot_df_global = df_global[df_global["year"]==years[-1]]

    average_temperature = plot_df_global["LandAndOceanAverageTemperature"].mean()

    data = [
        go.Choroplethmapbox(
        geojson=geo_json,
        locations=plot_df["Country"],
        z=plot_df[attribute],
        zmin=-40,
        zmax=40,
        customdata=plot_df[attribute],
        text=plot_df["Country"],
        hovertemplate="%{text}<br>Average Temperature: %{customdata}°C",
        colorscale="RdBu",
        reversescale=True,
        showscale=False,
        subplot="mapbox",
        name="choroplethmapbox",
        colorbar=dict(outlinewidth=1,
            outlinecolor="#333333",
            len=0.9,
            lenmode="fraction",
            orientation="h",
            xanchor="center",
            yanchor="bottom",
            bgcolor=None,
            y=0.05,
            #title=dict(text="Cases",
            #            font=dict(size=14))
        )
    ),

    go.Scattermapbox(
        lat = plot_df["Latitude"],
        lon = plot_df["Longitude"],
        mode = "markers+text",
        marker=go.scattermapbox.Marker(
            size= plot_df["GHG"]*300/df["GHG"].max(),
            sizemin=2,
            opacity=0.7,
            color = "rgb(235,0,100)",
        ),
        text=plot_df["Country"],
        subplot="mapbox",
        name="scattermapbox",
    ),

    go.Table(
        header = dict(values=[["Hottest Country"]],
                      fill_color='white',
                      font=dict(color='black', size=15),align="center"),
        cells = dict(values=[[hottest_data["Country"] +" (" + str(hottest_temperature)+" C°)" ]], 
        align="center",
        fill_color="white"),
        name = "table",
        domain = dict(x=[0,0.2],
                      y=[0,0.13])
    ),
    go.Table(
        header = dict(values=[["Coldest Country"]],
                      fill_color='white',
                      font=dict(color='black', size=15),align="center"),
        cells = dict(values=[[coldest_data["Country"] +" (" + str(coldest_temperature)+" C°)" ]], 
        align="center",
        fill_color="white"),
        name = "table",
        domain = dict(x=[0.2,0.4],
                      y=[0,0.13],)
    ),
    go.Table(
        header = dict(values=[["Current year"]],
                      fill_color='white',
                      font=dict(color='black', size=20),align="center"),
        cells = dict(values=[[str(2010)]], 
        align="center",
        fill_color="white",
        font=dict(size=20)),
        name = "table",
        domain = dict(x=[0.4,0.6],
                      y=[0,0.13],)
    ),
    go.Table(
        header = dict(values=[["Most emissions"]],
                      fill_color='white',
                      font=dict(color='black', size=15),align="center"),
        cells = dict(values=[[most_emissions_data["Country"] +" (" + str(round(most_emissions/1000000000,2))+" billion)" ]], 
        align="center",
        fill_color="white"),
        name = "table",
        domain = dict(x=[0.6,0.8],
                      y=[0,0.13],)
    ),
    go.Table(
        header = dict(values=[["Average temperature"]],
                      fill_color='white',
                      font=dict(color='black', size=15),align="center"),
        cells = dict(values=[[str(round(average_temperature,2))+" C°" ]], 
        align="center",
        fill_color="white"),
        name = "table",
        domain = dict(x=[0.8,1],
                      y=[0,0.13],)
    ),

    ]

    layout = go.Layout(
        autosize=True,
        showlegend=False,
        hovermode="closest",
        plot_bgcolor='rgba(0,0,0,0)',
        margin = dict(
            l = 0,        # left
            r = 0,        # right
            t = 0,        # top
            b = 0,        # bottom
        ),
        mapbox=dict(

            style="light",
            accesstoken=mapbox_token,
            bearing=0,
            pitch=0,
            domain={
                'x': [0, 1],
                'y': [0.15, 1]
            }

        ),
    )


    #Update menus
    layout["updatemenus"] = [dict(
        type="buttons",
        buttons=[dict(
            label="Play",
            method="animate",
            args=[None,
            dict(frame=dict(duration=250,
            redraw=True),fromcurrent=True),dict(transition=dict(duration=0,redraw=True),fromCurrent=True)]
        ),
        dict(
            label="Pause",
            method="animate",
            args=[[None],
            dict(frame=dict(duration=0,
            redraw=True),
            mode="immediate")]
        )],
        direction="right",
        pad={"r":150,"t": 40},
        showactive=False,
        x=0.2,
        xanchor="right",
        y=0.08,
        yanchor="top"
    )]

    sliders_dict = dict(active=2010,
                        visible=True,
                        yanchor="top",
                        xanchor="left",
                        currentvalue=dict(font=dict(size=20,color="white"),
                                        visible=True,
                                        xanchor="right"),
                        pad=dict(b=10,l=150),
                        len=0.975,
                        x=0,
                        y=0.11,
                        steps=[])
    
    fig_frames = []
    steps = []
    for year in range(years[0],years[-1],5):#range(years[0],years[-1],10):

        plot_df = df[df["year"]==year]

        hottest_temperature = plot_df["AverageTemperature"].max()
        hottest_data = plot_df.loc[plot_df["AverageTemperature"]==hottest_temperature]

        coldest_temperature = plot_df["AverageTemperature"].min()
        coldest_data = plot_df.loc[plot_df["AverageTemperature"]==coldest_temperature]

        most_emissions = plot_df["GHG"].max()
        most_emissions_data = plot_df.loc[plot_df["GHG"]==most_emissions]

        plot_df_global = df_global[df_global["year"]==year]


        frame = go.Frame(data=[
            go.Choroplethmapbox(
                locations=plot_df["Country"],
                z=plot_df[attribute],
                customdata=plot_df[attribute],
                #name="",
                text=plot_df["Country"],
                #showscale=False,
            ),
            go.Scattermapbox(
                lat = plot_df["Latitude"],
                lon = plot_df["Longitude"],
                mode = "markers+text",
                marker=go.scattermapbox.Marker(
                    size= plot_df["GHG"]*300/df["GHG"].max(),
                    sizemin=2,
                    opacity=0.7
                ),
                text=plot_df["Country"],
                marker_color = "rgb(235,0,100)",
            ),
            go.Table(
                cells = dict(values=[[hottest_data["Country"] +" (" + str(hottest_temperature)+" C°)" ]],
                align="center"),
            ),
            go.Table(
                cells = dict(values=[[coldest_data["Country"] +" (" + str(coldest_temperature)+" C°)" ]],
                align="center"),
            ),
            go.Table(
                cells = dict(values=[[str(year)]],
                align="center"),
            ),

            go.Table(
                cells = dict(values=[[most_emissions_data["Country"] +" (" + str(round(most_emissions/1000000000,2))+" billion)" ]],
                align="center"),
            ),

            go.Table(
                cells = dict(values=[[str(round(plot_df_global["LandAndOceanAverageTemperature"].mean(),2))+" C°" ]]), 
            ),

            ],
            name=str(year),
            traces = [0, 1, 2, 3, 4, 5, 6, 7])

        fig_frames.append(frame)

        slider_step = dict(
            args=[[str(year)],
            dict(mode="immediate",
            frame=dict(duration=500,
            redraw=True))],
            method="animate",
            label=str(year)
        )

        steps.append(slider_step)

    sliders_dict["steps"] = steps

    layout.update(sliders=[sliders_dict])

    fig = go.Figure(data=data,layout=layout,frames=fig_frames)

    fig.add_layout_image(
        dict(
            source=Image.open("assets/colorbar_good.png"),
            xref="paper", yref="paper",
            x=0.5, y=0.15,
            sizex=1, sizey=1,
            opacity=0.7,
            xanchor="center", yanchor="bottom"
        )
    )

    return fig

if __name__ == "__main__":

    #Get mapbox token
    mapbox_token = ud.config['mapbox']['token']
    raw_dataset_path = ud.RAW_PATH + ud.config['path']['name']
    geo_world = ud.RAW_PATH + ud.config['geoworld']['name']
    global_data = ud.RAW_PATH + ud.config['path']['global']

    df_global = pd.read_csv(global_data)
    df_raw = pd.read_csv(raw_dataset_path)

    with open(geo_world) as world_file:
        world = json.load(world_file)

    df_raw = get_yearly_data(df_raw)
    #Create the map figure

    #df = get_temperature_diff_between(df,1900,2000)
    fig_map = create_final_no_bar(df_raw,mapbox_token,world,"AverageTemperature",df_global)   
    #fig_map = get_map_from_date(df_raw,mapbox_token,world)

    save_map = {
        'figure':fig_map,
    }

    ud.save_pickle(save_map, 'map_info.p')

    logger.info('World map updated.')
    logger.info('Data stored for dash application.')

