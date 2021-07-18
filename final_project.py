#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Tue Jul  6 17:45:57 2021@author: brittanymullaney
Name: Brittany Mullaney
CS602-SN1
Professor: Rude
Data: Skyscrapers
Description:
This app takes a dive into the top 100 tallest skyscrapers around the world. 
You will be able to see an wikipedia summary on what Skyscrapers are.
You will also be able to locate the Skyscrapers on a map and by city.
You will also learn a bit about the Skyscrapers depending on the city of your choice.
Lastly, you'll see a comparison of the tallest Skyscrapers globally.
"""

from matplotlib.backends.backend_agg import RendererAgg
import numpy as np
import pandas as pd
import pydeck as pdk
import seaborn as sns
import matplotlib 
from matplotlib.figure import Figure
import wikipedia
import streamlit as st


@st.cache
def load_data(): # LOAD THE DATA
    data = pd.read_csv('Skyscrapers2021.csv')
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    return data
data = load_data()


_lock = RendererAgg.lock

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns(
    (.1, 2, .2, 1, .1))

row0_1.title('Skyscrapers 2021')
with row0_2:
    st.write('')

row1_spacer1, row1_1, row1_spacer2 = st.beta_columns((.1, 3.2, .1))


with row1_1:
    st.markdown("Hey there! Welcome to the Skyscraper Analysis App.")
    result = wikipedia.page("Skyscrapers") #pulling wikipedia page
    st.subheader("Wikipedia Summary for 'Skyscrapers':")
    st.write(result.summary) #show a wikipedia summary of Skyscrapers 


# CREATE A SIDEBAR DROP DOWN LIST OF ALL THE CITIES
cityList = [] #get unique city list for drop down
for city in data['city']:
    if city in cityList:
        pass
    else:
        cityList.append(city)

cityList.sort() #sort the list ascending
cityOption = st.sidebar.selectbox('Please choose a city:',cityList)
count_df = data[data['city']==cityOption]
index = count_df.index
rows = len(index) #counting the # rows/skyscrapers per city
st.header(f'Skyscrapers in {cityOption}')
if rows == 1:
    st.markdown(f'There is {rows} Skyscrapers in {cityOption}!')
else:    
    st.markdown(f'There are {rows} Skyscrapers in {cityOption}!')



row3_space1, row3_1, row3_space2, row3_2, row3_space3 = st.beta_columns(
    (.1, 1, .1, 1, .1)) #spacing and formatting app

with row3_1, _lock:
    st.subheader(f'Map of Skyscrapers in {cityOption}:')
# CREATE A MAP OF SKYSCRAPERS WITHIN EACH CITY (WITH TOOLTIP)
    locations = data[['name','city','completion','feet','latitude','longitude']]
    map_data = pd.DataFrame(locations)
    map_result = map_data[map_data['city']==cityOption]
    
    layer1 = pdk.Layer('ScatterplotLayer',
                       data=map_result,
                       get_position='[longitude, latitude]',
                       auto_highlight=True,
                       get_radius=300,
                       get_color=[119,0,119,200],
                       pickable=True)
    
    tool_tip = {"html": "<b>Skyscraper:</b> {name}"
                "<br/> <b>City:</b> {city}"
                "<br/> <b>Year Complete:</b> {completion}"
                "<br/> <b>Height (ft):</b> {feet}",
                "style": { "backgroundColor": "midnightblue", "color": "white"}}
    
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
        latitude=map_result['latitude'].mean(), #default avg location of the skyscrapers 
        longitude=map_result['longitude'].mean(),
        zoom=10,
        pitch=20),
        layers=[layer1],
        tooltip=tool_tip))


with row3_2, _lock:
# CREATE A TABLE FILTERED TO OPTION
    st.subheader(f'Details about the Skyscrapers in {cityOption}:')
    skyscrapers = data[['city','name','completion','feet','floors','material','function']]
    table_data = pd.DataFrame(skyscrapers)
    result = table_data[table_data['city']==cityOption]
    st.table(result[['name','completion','feet','floors','material','function']])
    
st.header('Skyscrapers Around the World')
number = st.slider("Choose the number of Skyscrapers you'd like to compare:", 3, 10, 5) #user input number of skyscrapers to see

row4_space1, row4_1, row4_space2, row4_2, row4_space3 = st.beta_columns(
    (.1, 1, .1, 1, .1)) #spacing and formatting the app

with row4_1, _lock:
    # CREATE A CHART OF TALLEST SKYSCRAPERS BY HEIGHT
    height = data[['name','feet']]
    height_data = pd.DataFrame(height)
    newheight = [x[:-3] for x in height['feet']] #removing 'ft' string
    newheight = [int(x.replace(',', '')) for x in newheight] #convert to int and replace it
    height_data.feet = newheight
    x = height_data.nlargest(int(number),['feet'])
        
    st.subheader(f'Top {number} Tallest Skyscrapers by Height (ft)')
    fig = Figure()
    ax = fig.subplots()
    splot = sns.barplot(x=x['feet'],y=x['name'], palette="Blues_d", ax=ax)
    for p in splot.patches:
        splot.annotate("%.0f" % p.get_width(), xy=(p.get_width(), p.get_y()+p.get_height()/2),
                       xytext=(5, 0), textcoords='offset points', ha="right", va="center")
    ax.set_xlabel('Height (ft)')
    ax.set_ylabel('Name')
    st.pyplot(fig)

with row4_2, _lock:
    # CREATE A CHART OF TALLEST SKYSCRAPERS BY NO. FLOORS
    height = data[['name','floors']]
    height_data = pd.DataFrame(height)
    x = height_data.nlargest(int(number),['floors']) #convert floors to int       
    st.subheader(f'Top {number} Skyscrapers by No. of Floors')
    fig = Figure()
    ax = fig.subplots()
    splot = sns.barplot(x=x['floors'],y=x['name'], palette="Greens_d", ax=ax)
    for p in splot.patches:
        splot.annotate("%.0f" % p.get_width(), xy=(p.get_width(), p.get_y()+p.get_height()/2),
                       xytext=(5, 0), textcoords='offset points', ha="right", va="center")
    ax.set_xlabel('No. of Floors')
    ax.set_ylabel('Name')
    st.pyplot(fig)
 
    
# CREATE A MAP OF ALL SKYSCRAPERS (WITH TOOLTIP)
locations = data[['name','city','completion','feet','latitude','longitude']]
map_data = pd.DataFrame(locations)
# map layer - scatterplot
layer1 = pdk.Layer('ScatterplotLayer',
                   data=map_data,
                   get_position='[longitude, latitude]',
                   get_radius=150000,
                   get_color=[30,100,0,100],
                   pickable=True)

tool_tip = {"html": "<b>Skyscraper:</b> {name}"
            "<br/> <b>City:</b> {city}"
            "<br/> <b>Year Complete:</b> {completion}"
            "<br/> <b>Height (ft):</b> {feet}",
            "style": { "backgroundColor": "forestgreen",
                      "color": "white"}}
    
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=0, #default to center of map
        longitude=0,
        zoom=1,
        pitch=20),
    layers=[layer1],
    tooltip=tool_tip))

