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
def load_data(): # loading the data using pandas
    data = pd.read_csv('Skyscrapers2021.csv')
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    return data

def wiki_data(): #new module that we haven't used in class
    st.markdown("Hey there! Welcome to the Skyscraper Analysis App. This app dives into the top 100 tallest skyscrapers around the world.")
    result = wikipedia.page("Skyscrapers") #pulling wikipedia page info
    st.header("What is a Skyscraper?")
    st.subheader("Here's a Wikipedia Summary for 'Skyscrapers':")
    with st.beta_expander('Expand to see a summary'):
        st.write(result.summary) #show a wikipedia summary of Skyscrapers    

def wiki_search(data,cityOption): 
    st.markdown(f"Do you want to search '**_{cityOption} Skyscrapers_**' on Wikipedia?")
    results = wikipedia.search(f'{cityOption} Skyscrapers') #search for info about the selected city
    agree = st.checkbox("Yes, I'd like to see some additional info.") #ability to show/hide option   
    return results, agree

def wiki_results(results,agree): #seperated the results for formatting purposes
    if agree:
        pageSelector = st.selectbox("Please choose the page you'd like to read about:",results) #specified page options to choose from
        page = wikipedia.page(pageSelector) #look up page option
        with st.beta_expander('Expand to see the summary'): #allow user to minimize summary
            st.write(page.summary)
    
def city_List(data):
    st.header('Skyscrapers by City')    
    cityList = [] #get unique city list for drop down
    for city in data['city']:
        if city in cityList:
            pass
        else:
            cityList.append(city)
    cityList.sort() #sort the list
    cityOption = st.selectbox('Please choose a city to look at:',cityList)          
    return cityOption

def city_count(data,cityOption):
    count_df = data[data['city']==cityOption] #filter list of names based on city chosen
    index = count_df.index
    rows = len(index) #counting the number of skyscrapers per city    
    if rows == 1:
        st.markdown(f'_There is {rows} Skyscrapers in **{cityOption}**!_ :sunglasses:')
    else:    
        st.markdown(f'_There are {rows} Skyscrapers in **{cityOption}**!_ :sunglasses:')
    
def city_Map(data,cityOption):    
    st.subheader(f'Map of Skyscrapers in {cityOption}:')
    locations = data[['name','city','completion','feet','latitude','longitude']] #pull data for map
    map_data = pd.DataFrame(locations)
    map_result = map_data[map_data['city']==cityOption] #filter map to chosen city
    
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
    #create map of skyscapers based on chosen city
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
        latitude=map_result['latitude'].mean(), #default avg location of the skyscrapers 
        longitude=map_result['longitude'].mean(),
        zoom=10,
        pitch=20),
        layers=[layer1],
        tooltip=tool_tip))

def city_Table(data,cityOption):
    st.subheader(f'Details about the Skyscrapers in {cityOption}:')
    city_count(data, cityOption)
    skyscrapers = data[['city','name','completion','feet','floors','material','function']] #pull data for table
    table_data = pd.DataFrame(skyscrapers)
    result = table_data[table_data['city']==cityOption] #filter table data to chosen city
    st.table(result[['name','completion','feet','floors','material','function']])
    
def slider(data):
    st.header('Skyscrapers Around the World')
    sliderNumber = st.slider("Choose the number of Skyscrapers you'd like to compare:", 3, 10, 5) #user input number of skyscrapers to see
    return sliderNumber
    
def tall_Height(data,sliderNumber):    
    height = data[['name','feet']]
    height_data = pd.DataFrame(height)
    newheight = [x[:-3] for x in height['feet']] #removing 'ft' string
    newheight = [int(x.replace(',', '')) for x in newheight] #convert to int and replace it
    height_data.feet = newheight
    x = height_data.nlargest(int(sliderNumber),['feet'])
        
    st.subheader(f'Top {sliderNumber} Tallest Skyscrapers by Height (ft)')
    fig = Figure()
    ax = fig.subplots()
    splot = sns.barplot(x=x['feet'],y=x['name'], palette="Blues_d", ax=ax)
    for p in splot.patches:
        splot.annotate("%.0f" % p.get_width(), xy=(p.get_width(), p.get_y()+p.get_height()/2),
                       xytext=(5, 0), textcoords='offset points', ha="right", va="center")
    ax.set_xlabel('Height (ft)')
    ax.set_ylabel('Name')
    st.pyplot(fig)

def tall_Floors(data,sliderNumber):
    height = data[['name','floors']]
    height_data = pd.DataFrame(height)
    x = height_data.nlargest(int(sliderNumber),['floors']) #convert floors to int       
    st.subheader(f'Top {sliderNumber} Skyscrapers by No. of Floors')
    fig = Figure()
    ax = fig.subplots()
    splot = sns.barplot(x=x['floors'],y=x['name'], palette="Greens_d", ax=ax)
    for p in splot.patches:
        splot.annotate("%.0f" % p.get_width(), xy=(p.get_width(), p.get_y()+p.get_height()/2),
                       xytext=(5, 0), textcoords='offset points', ha="right", va="center")
    ax.set_xlabel('No. of Floors')
    ax.set_ylabel('Name')
    st.pyplot(fig)    

def all_Map(data):
    st.write("Here's a map of all the top 100 tallest Skyscrapers:")
    locations = data[['name','city','completion','feet','latitude','longitude']]
    map_data = pd.DataFrame(locations)
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


def main():
    st.set_page_config(layout="wide")
    data = load_data()
    _lock = RendererAgg.lock
    
    row0_spacer1, row0_1, row0_spacer2, row0_2 = st.beta_columns((.1, 3, .8, 1))
    row0_1.title('Skyscrapers 2021')
    row0_2.markdown('_Created by: Brittany Mullaney \n Bentley University_')

    with row0_2:
        st.write('')
    
    row1_spacer1, row1_1, row1_spacer2 = st.beta_columns((.1, 3.2, .1)) #indent next row
    with row1_1:
        wiki_data()

    if st.sidebar.checkbox('All Skyscrapers'):
        row4_spacer1, row4_1, row4_spacer2 = st.beta_columns((.1, 2,.1))       
        with row4_1:
            sliderNumber = slider(data)
    
        row5_space1, row5_1, row5_space2, row5_2, row5_space3 = st.beta_columns((.1, 1, .1, 1, .1))
        with row5_1, _lock:
            tall_Height(data, sliderNumber)
        with row5_2, _lock:
            tall_Floors(data, sliderNumber)
    
        row6_spacer1, row6_1, row6_spacer2 = st.beta_columns((.1, 2,.1))       
        with row6_1:
            all_Map(data)
        
    else:
        st.write('')

    if st.sidebar.checkbox('Skyscrapers by City'):
        row2_spacer1, row2_1, row2_spacer2, row2_2 = st.beta_columns((.1, 1,.1, 1.5))       
        with row2_1:
            cityOption = city_List(data)
    
        row3a_spacer1, row3a_1, row3a_spacer2, row3a_2, row3a_spacer3 = st.beta_columns((.1,1,.1,1,.1))
        with row3a_1:
            results, agree = wiki_search(data, cityOption)
        with row3a_2:
            wiki_results(results, agree)
            
        row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((.1,.6,.1,1.2,.1))
        with row3_1, _lock:
            city_Map(data, cityOption)
        with row3_2, _lock:
            city_Table(data, cityOption)
    else:
        st.write('')
        
main()
