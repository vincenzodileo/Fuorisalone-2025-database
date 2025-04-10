# %% [markdown]
# Find distance matrix and plots

# %%
from geopy.distance import geodesic
import pandas as pd
import numpy as np
import os
import folium
from folium.plugins import HeatMap

# %%
def find_distance(lat_1, lon_1, lat_2, lon_2):
    
    return geodesic((lat_1, lon_1), (lat_2, lon_2)).kilometers #distance in kilometers

# %%
def get_heatmap(fuorisalone_sunday, graph_path): #produce interactive heatmap using folium
    # Create a map centered around the average location of the points
    m = folium.Map(location=[fuorisalone_sunday['lat'].mean(), fuorisalone_sunday['lon'].mean()], zoom_start=14)
    # Create a heatmap layer
    heat_data = [[row['lat'], row['lon']] for index, row in fuorisalone_sunday.iterrows()]
    HeatMap(heat_data).add_to(m)
    # Save the map to an HTML file
    m.save(graph_path)


    return
    

# %%
def get_pinpointmap(fuorisalone_sunday, graph_path): #produce interactive pinpoint map using folium

    # Create a map centered around the average location of the points
    m = folium.Map(location=[fuorisalone_sunday['lat'].mean(), fuorisalone_sunday['lon'].mean()], zoom_start=14)
    # Add points to the map

    for index, row in fuorisalone_sunday.iterrows():
        folium.Marker(location=[row['lat'], row['lon']], popup=row['Event_Name']).add_to(m)
    
    # Save the map to an HTML file
    m.save(graph_path)

    return


# %%
#load the data
fuorisalone_sunday = pd.read_csv("Data/fuorisalone_sunday.csv")


get_heatmap(fuorisalone_sunday, "Data/fuorisalone_sunday_heatmap.html")
get_pinpointmap(fuorisalone_sunday, "Data/fuorisalone_sunday_pinpointmap.html")



