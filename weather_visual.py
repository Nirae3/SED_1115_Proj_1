import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import datetime
import openmeteo_requests
import requests_cache
from retry_requests import retry
import urllib.request




st.set_page_config(layout="wide")

####################### DATA EXPERIMENTATION as per website ##############
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 45.4112,
	"longitude": -75.6981,
	"daily": ["temperature_2m_mean", "precipitation_probability_max", "uv_index_max"],
	"timezone": "America/New_York",
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(1).ValuesAsNumpy()
daily_uv_index_max = daily.Variables(2).ValuesAsNumpy()

# set the range and the interval
daily_7 = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}


# Add the daily weather variables (temperature, precipitation probability, UV index)
# to the dictionary 'daily_7', 

daily_7["temperature_2m_mean"] = daily_temperature_2m_mean
daily_7["precipitation_probability_max"] = daily_precipitation_probability_max
daily_7["uv_index_max"] = daily_uv_index_max

# then convert it into a pandas DataFrame with specified column order. 
# Set the 'date' column as the DataFrame index for easier plotting and analysis.
daily_7_data = pd.DataFrame(
    data = daily_7,
    columns=["date", "temperature_2m_mean", "precipitation_probability_max", "uv_index_max"]
    )
daily_7_data.set_index("date", inplace=True)


################# IMPROVED ############# DATA URLS ###############

# 2014
# collect data URLS 
old_month_urls = {
    "jan_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=1&Day=21&time=LST&timeframe=1&submit=Download+Data",
    "feb_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=2&Day=21&time=LST&timeframe=1&submit=Download+Data",
    "mar_2014":"https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=3&Day=21&time=LST&timeframe=1&submit=Download+Data",
    "apr_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=4&Day=30&time=LST&timeframe=1&submit=Download+Data",
    "may_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=5&Day=30&time=LST&timeframe=1&submit=Download+Data",
    "jun_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=6&Day=30&time=LST&timeframe=1&submit=Download+Data",
    "jul_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=7&Day=30&time=LST&timeframe=1&submit=Download+Data",
    "aug_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=8&Day=30&time=LST&timeframe=1&submit=Download+Data",
    "sep_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=9&Day=30&time=LST&timeframe=1&submit=Download+Data",
    "oct_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=10&Day=30&time=LST&timeframe=1&submit=Download+Data",
    "nov_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=11&Day=30&time=LST&timeframe=1&submit=Download+Data",
    "dec_2014": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2014&Month=12&Day=30&time=LST&timeframe=1&submit=Download+Data"
}



#2024

new_month_urls={
    "jan_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=1&Day=30&time=LST&timeframe=1&submit=Download+Data",
    "feb_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=2&Day=1&time=LST&timeframe=1&submit=Download+Data",
    "mar_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=3&Day=31&time=LST&timeframe=1&submit=Download+Data",
    "apr_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=4&Day=1&time=LST&timeframe=1&submit=Download+Data",
    "may_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=5&Day=1&time=LST&timeframe=1&submit=Download+Data",
    "jun_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=6&Day=1&time=LST&timeframe=1&submit=Download+Data",
    "jul_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=7&Day=1&time=LST&timeframe=1&submit=Download+Data",
    "aug_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=8&Day=1&time=LST&timeframe=1&submit=Download+Data",
    "sep_2024":"https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=9&Day=1&time=LST&timeframe=1&submit=Download+Data",
    "oct_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=10&Day=1&time=LST&timeframe=1&submit=Download+Data",
    "nov_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=11&Day=1&time=LST&timeframe=1&submit=Download+Data",
    "dec_2024": "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2024&Month=12&Day=1&time=LST&timeframe=1&submit=Download+Data"


}



### handling errors:   Code written by ChatGPT 
def safe_read_csv(url):
    try:
        # Some servers block automated requests, so we add a User-Agent
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        df = pd.read_csv(req)
        return df
    except Exception as e:
        # Catch any exception and print a message instead of crashing
        print(f"Failed to download {url}: {e}")
        return None  # or pd.DataFrame() if you want an empty dataframe


################### WELCOME PAGE ##################################

# variables:
today=datetime.date.today()

st.write("## Wealcome to Simply Visualize Weather!")

question_1="Is it safe for students and young children to go outside or study outside today or during the next 7 days?"
question_2="Compare current month weather with weather form 10 years ago"


# user chooses what they want to see
user_goal = st.selectbox(
    "From the Drop Down menu, please choose what I can help you with",
    ("N/A", question_1, question_2)
)

st.divider() 


# If user chose nothing, show nothing
if user_goal=="N/A":
    st.header("Welcome! This is an experimental project where I explore weather data—let’s see if it sparks your interest! Let's go!!!")
#if user chose forecast for next 7 days, show forecast. 
elif user_goal==question_1:
    good_weather = daily_7_data[
        (daily_7_data["temperature_2m_mean"]>=10) &
        (daily_7_data["temperature_2m_mean"]<=25)&
        (daily_7_data["uv_index_max"]<=3) &
        (daily_7_data["precipitation_probability_max"]==0)
    ]

    if not good_weather.empty:
        st.subheader("Today is a wonderful day to go outside!")
    else:
        st.subheader("Maybe the young should stay at home/schools")

    st.subheader("Showing forecast data for the next 7 days ...")
    st.line_chart(daily_7_data)
    st.divider()
    st.subheader("Data in Table Format")
    st.dataframe(daily_7_data,use_container_width=True)

    #create a list of acceptable measurements that define what it means to have a good weather
   


elif user_goal == question_2:
    st.subheader("Choose a research month and year")

    # user selects what data they wanna compare. 
    #page gets divided into two columns
    col1, col2 = st.columns(2)
    with col1: 
        user_2024_choice=st.selectbox("pick a month", list(new_month_urls.keys()))
    with col2:
        user_2014_choice=st.selectbox("pick a 2014 month you'd like to compare with", list(old_month_urls.keys()))


    # read the data and store in month_20*4 data
    month_2024_data=pd.read_csv(new_month_urls[user_2024_choice])
    month_2014_data=pd.read_csv(old_month_urls[user_2014_choice])

    # collect only necessary columns
    needed_old_data_info=["Date/Time (LST)","Temp (°C)", "Precip. Amount (mm)"]
    needed_new_data_info=["Date/Time (LST)","Temp (°C)", "Precip. Amount (mm)"]

    # folter the data
    filtered_old_data=month_2014_data[needed_old_data_info]
    filtered_new_data=month_2024_data[needed_new_data_info]

    # get rid of null values
    filtered_old_data=filtered_old_data.fillna("N/A")
    filtered_new_data=filtered_new_data.fillna("N/A")

    # convert "date/time (LST)" to date
    filtered_old_data["Date/Time (LST)"] = pd.to_datetime(filtered_old_data["Date/Time (LST)"])
    #filtered_old_data["Date"] = filtered_old_data["Date/Time (LST)"].dt.date  # from the date and time, extract date
    filtered_new_data["Date/Time (LST)"] = pd.to_datetime(filtered_new_data["Date/Time (LST)"])
    #filtered_new_data["Date"] = filtered_new_data["Date/Time (LST)"].dt.date  # from the date and time, extract date

    # convert temperature and precipitation to numeric values
    filtered_old_data["Temp (°C)"] = pd.to_numeric(filtered_old_data["Temp (°C)"], errors="coerce")
    filtered_old_data["Precip. Amount (mm)"] = pd.to_numeric(filtered_old_data["Precip. Amount (mm)"], errors="coerce")

    filtered_new_data["Temp (°C)"] = pd.to_numeric(filtered_new_data["Temp (°C)"], errors="coerce")
    filtered_new_data["Precip. Amount (mm)"] = pd.to_numeric(filtered_new_data["Precip. Amount (mm)"], errors="coerce")

    filtered_old_data["Date/Time (LST)"]=pd.to_datetime(filtered_old_data["Date/Time (LST)"])
    filtered_new_data["Date/Time (LST)"]=pd.to_datetime(filtered_new_data["Date/Time (LST)"])

    # old data decide on what columns to use
    draw_old_data=pd.DataFrame(
        data=filtered_old_data, 
        columns=["Date/Time (LST)","Temp (°C)", "Precip. Amount (mm)"]
        )

    # identify each column as per date and time
    draw_old_data.set_index("Date/Time (LST)", inplace=True)

    #create dataframe with filtered data
    draw_new_data=pd.DataFrame(
        data=filtered_new_data, 
        columns=["Date/Time (LST)","Temp (°C)", "Precip. Amount (mm)"]
        )
    # identify each column as per date and time
    draw_new_data.set_index("Date/Time (LST)", inplace=True)

    #create tow columns to compare diagram side by side.
    new_col1, old_col2 = st.columns(2)
    with new_col1:
        st.subheader(f"2024 Weather data for {user_2024_choice}")
        st.line_chart(draw_new_data)
        with st.expander(f"View SHOWN data in table for month {user_2024_choice}"): #makes the data expandable to avoid clustering
            st.write("Here is the selected data table")
            st.dataframe(filtered_new_data, use_container_width=True)
            st.write(filtered_new_data)
        with st.expander ("click to see all of 2024 weather month data"): #makes the data expandable to avoid clustering
            st.write("Here is the data table")
            st.write("2024 Data", month_2024_data)
        
    with old_col2:
        st.subheader(f"2014 Weather data for {user_2014_choice}")
        st.line_chart(draw_old_data)
        with st.expander(f"View SHOWN data in table format for month {user_2014_choice}"): #makes the data expandable to avoid clustering
            st.write("Here is the selected data table")
            st.dataframe(filtered_old_data, use_container_width=True)
            st.write(filtered_old_data)

        with st.expander("click to see all of 2024 weather month data"): #makes the data expandable to avoid clustering
            st.write("Here is the data table")
            st.write("2014 data", month_2024_data)


# Rates the experience the user had with the app. 
st.divider()
st.write("Don't Forget to Rate Your Experience With Us!")
experience_rate = ["one","two", "three", "four", "five"]
selected_stars=st.feedback("stars")
st.divider()




