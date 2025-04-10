# %% [markdown]
# Create a dataaìbase starting from the fuorisalone website containing as follow:
# 
# Event name | Event location | Event date (programma)* | Event description | Event image | Event link 

# %%
#import libraries
import os
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re

# %%
def get_event_links(url_fuorisalone_landing): # Function to scrape event links from the given URL
    
    event_links = []
    page = 1

    while True:
        # Build the URL for the current page
        if page == 1:
            url = url_fuorisalone_landing
        else:
            url = f"{url_fuorisalone_landing}?&page={page}"
        
        print(f"Scraping: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            break  # Stop if the page is not found
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all event links that match the pattern
        anchors = soup.find_all('a', href=True)
        page_links = [a['href'] for a in anchors if a['href'].startswith(url_fuorisalone_landing + "/") and "lista?" not in str(a['href']) and "mappa" not in str(a['href'])]
        print(f"Found {len(page_links)} links on page {page}.")
        print(page_links)
        
        if not page_links or page >= 31: #30 normally
            break  # Stop if no event links found (last page)
        
        # Avoid duplicates
        for link in page_links:
            if link not in event_links:
                event_links.append(link)

        page += 1  # Move to next page


    return event_links  # Return the list of event links


# %%
def get_event_schedule(event_link): #get the event schedule as dictionary
    response = requests.get(event_link)
    soup = BeautifulSoup(response.text, 'html.parser')


    # structure of the event schedule:
    #event_schedule= {"Lunedì": {"Event_1": [start_time, end_time, description], "Event_2": [start_time, end_time, description]}, "Martedì":  {"Event_1": [start_time, end_time, description]}} 
    #start_time is a string hh:mm, end_time is a string hh:mm, description is a string

    event_schedule = {}

    for num_days in range(1, 8):
        giorni_class = f'giorni_palinsesto_2020 num_giorni_{num_days}'
        giorni_container = soup.find('div', class_=giorni_class)
        
        if not giorni_container:
            continue

        days = giorni_container.find_all('div', class_='col-xs-12 col-sm-2 giorno_palinsesto nopadding today-open')

        for day in days:
            day_name_div = day.find('div', class_='data_palinsesto')
            if not day_name_div:
                continue

            # Extract day name (e.g., "Lunedì")
            day_name = day_name_div.get_text(strip=True).split(' ')[-1]

            # Initialize dictionary for events in this day
            event_schedule[day_name] = {}

            events_divs = day.find_all('div', class_='ora_palinsesto')
            for idx, event_div in enumerate(events_divs, start=1):
                # Extract times
                time_span = event_div.find('span')
                if time_span:
                    times = time_span.get_text(strip=True).split('-')

                    try: start_time = times[0].strip()
                    except: start_time = "N/A"
                    
                    try: end_time = times[1].strip()
                    except: end_time = "N/A"

                else:
                    start_time = end_time = "N/A"

                # Extract event description
                description_parts = event_div.get_text(separator='\n', strip=True).split('\n')
                description = description_parts[1] if len(description_parts) > 1 else "No description"

                # Add to the day's events
                event_key = f"Event_{idx}"
                event_schedule[day_name][event_key] = [start_time, end_time, description]

    return event_schedule


# %%
def refine_event_schedule(event_schedule):  # Function to refine the event schedule dictionary
    days_of_week = ["7/4Lunedì", "8/4Martedì", "9/4Mercoledì", "10/4Giovedì", "11/4Venerdì", "12/4Sabato", "13/4Domenica"]
    formatted_schedule = {}

    for day in days_of_week:
        # Check if there is an event for the current day
        if day in event_schedule and event_schedule[day]:
            events_list = []
            for event_key, details in event_schedule[day].items():
                start, end, desc = details
                event_str = f"{event_key}:[{start},{end},{desc}]"
                events_list.append(event_str)
            # Join events for the day into one string
            formatted_schedule[day] = ', '.join(events_list)
        else:
            formatted_schedule[day] = '-1'

    return formatted_schedule

# %%
#data in

url_fuorisalone_landing = 'TARGET_URL it/2025/eventi' #replace with the actual URL

#database initialization: Event name (string) | Event location (string address) | Event date (programma)* (data period) | Event description (string) | Event link (string)
fuorisalonedb = pd.DataFrame(columns=["Event_Name", "Event_Location", "Event_Date", "Event_Description","Event_Link", "Event_Schedule", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"])


#folders
#erease the csv file if it exists
if os.path.exists('Data/fuorisalone.csv'):
    os.remove('Data/fuorisalone.csv')


fuorisalonedb.to_csv('Data/fuorisalone.csv', index=False)

image_folder = 'Data/Pictures/'

# %%
###get the data from the website###



##get event links##
event_links= get_event_links(url_fuorisalone_landing) #get the event links from the landing page


#loop through the events and extract the data
n_event=0
for event_link in event_links:

    #generate the request to the event page
    response = requests.get(event_link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

    ##fill the database##
    event_name = soup.find('h1', class_='event_title strong col-xs-12 col-md-9 col-lg-8 nopadding') #get the event name
    event_location = soup.find('a', class_='link-indirizzo-location') #get the event location
    event_active_date= soup.find('div', class_='ev-days-text') #get the event date


    event_description_div = soup.find('div', class_='col-xs-12 nopadding contenitore-descrizione') #get the event description
    if event_description_div:
        paragraphs = event_description_div.find_all('p')
        event_description = ' '.join(p.get_text(separator=' ', strip=True) for p in paragraphs)


    #add event schedule
    event_schedule= get_event_schedule(event_link) #get the event schedule

    #refine the event schedule
    event_schedule_pretty = refine_event_schedule(event_schedule) #refine the event schedule, dictionary: 

    #print the event data
    # print(f"Event Name: {event_name.get_text(strip=True) if event_name else 'N/A'}")
    # print(f"Event Location: {event_location.get_text(strip=True) if event_location else 'N/A'}")
    # print(f"Event Active Date: {event_active_date.get_text(strip=True) if event_active_date else 'N/A'}")
    # print(f"Event Description: {event_description if event_description else 'N/A'}")
    # print(f"Event Link: {event_link}")
    # print(f"Event Schedule: {event_schedule}")
    # print("\n\n")

    n_event+=1
    print(f"Event {n_event}/{len(event_links)}")
        

    #add the data to the database using concat
    fuorisalonedb = pd.concat([fuorisalonedb, pd.DataFrame([[event_name.get_text(strip=True) if event_name else 'N/A', 
                                                             event_location.get_text(strip=True) if event_location else 'N/A', 
                                                             event_active_date.get_text(strip=True) if event_active_date else 'N/A', 
                                                             event_description if event_description else 'N/A', 
                                                             event_link, 
                                                             event_schedule,
                                                            event_schedule_pretty["7/4Lunedì"],
                                                            event_schedule_pretty["8/4Martedì"],
                                                            event_schedule_pretty["9/4Mercoledì"],
                                                            event_schedule_pretty["10/4Giovedì"],
                                                            event_schedule_pretty["11/4Venerdì"],
                                                            event_schedule_pretty["12/4Sabato"],
                                                            event_schedule_pretty["13/4Domenica"]]],
                                                            columns=["Event_Name", "Event_Location", "Event_Date", "Event_Description","Event_Link", "Event_Schedule", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"])], ignore_index=True)
 


#print(fuorisalonedb)

# %%
#save the database to a csv file
fuorisalonedb.to_csv('Data/fuorisalone.csv', index=False)


