# %% [markdown]
# Code to filter the database and create a new

# %%
#import libraries
import os
import pandas as pd
import numpy as np
import requests
import math

# %%
def validate_address(address_lines, region_code):
    url = f"https://addressvalidation.googleapis.com/v1:validateAddress?key={api_key}"

    payload = {
        "address": {
            "regionCode": region_code,
            "addressLines": address_lines
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    location = response.json()['result']['geocode']['location']
    latitude = location['latitude']
    longitude = location['longitude']

    return [latitude, longitude] #function to validate address and get lat/lon

# %%
#api Key
api_key= str(open("api_code.txt", 'r', encoding='utf-8').readline().strip())

## Load the dataset csv
fuorisalonedb = pd.read_csv("Data/fuorisalone.csv")



#filter for events of sunday 13/04

fuorisalonedb_sunday= fuorisalonedb[fuorisalonedb['Domenica'].astype(str) != '-1']

print(f"events on sunday: {fuorisalonedb_sunday.shape[0]}")


#add to the dataframe the lat/lon of the address
fuorisalonedb_sunday[['lat', 'lon']] = fuorisalonedb_sunday['Event_Location'].apply(
    lambda x: pd.Series(get_lat_lon(x)))



#save the dataframe with lat/lon
fuorisalonedb_sunday.to_csv("Data/fuorisalone_sunday.csv", index=False)



