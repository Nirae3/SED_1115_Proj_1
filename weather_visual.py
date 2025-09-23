import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import datetime
import openmeteo_requests
import requests_cache
from retry_requests import retry


st.set_page_config(layout="wide")

####################### DATA EXPERIMENTATION ##############
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

daily_7 = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_7["temperature_2m_mean"] = daily_temperature_2m_mean
daily_7["precipitation_probability_max"] = daily_precipitation_probability_max
daily_7["uv_index_max"] = daily_uv_index_max


daily_7_data = pd.DataFrame(
    data = daily_7,
    columns=["date", "temperature_2m_mean", "precipitation_probability_max", "uv_index_max"]
    )
daily_7_data.set_index("date", inplace=True)


################################################# HOURLY ############################################

## Read data from specific URL (this is hourly data)
url_hour = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=49568&Year=2025&Month=1&Day=31&time=LST&timeframe=1&submit=Download+Data"
url_hour_data=pd.read_csv(url_hour)

## Fetch only needed data (HOURLY)
needed_hourly_info=["Date/Time (LST)",  "Weather", "Temp (°C)"]
filtered_hourly_data=url_hour_data[needed_hourly_info]
filtered_hourly_data=filtered_hourly_data.fillna("N/A")  ## If there are blank values,fill in with N/A

## Convert Date and Time into understandable by computer date and time
filtered_hourly_data["Date/Time (LST)"] = pd.to_datetime(filtered_hourly_data["Date/Time (LST)"])
filtered_hourly_data["Date"] = filtered_hourly_data["Date/Time (LST)"].dt.date  # from the date and time, extract date

#print(filtered_hourly_data)

########################################################### DAILY #########################################
## Read data from specific URL (this is daily data)
url_day="https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=30578&Year=2025&Month=9&Day=1&time=&timeframe=2&submit=Download+Data"
url_day_data=pd.read_csv(url_day)


## Fetch only needed data (DAILY)
needed_daily_info=["Date/Time", "Total Precip (mm)", "Mean Temp (°C)"]

filtered_daily_data=url_day_data[needed_daily_info]
filtered_daily_data=filtered_daily_data.fillna("N/A")  ## If there are blank values,fill in with N/A


filtered_daily_data["Date/Time"]=pd.to_datetime(filtered_daily_data["Date/Time"])
filtered_daily_data["Date"]=filtered_daily_data["Date/Time"].dt.date
#print(filtered_daily_data)

############################################ MERGED ######################################

merged_data=pd.merge(filtered_hourly_data, filtered_daily_data, on="Date", how="left")
#print(merged_data)

# Convert to numeric, coerce errors to NaN
merged_data["Temp (°C)"] = pd.to_numeric(merged_data["Temp (°C)"], errors="coerce")
merged_data["Total Precip (mm)"] = pd.to_numeric(merged_data["Total Precip (mm)"], errors="coerce")

# Replace NaNs with 0 (or another choice) just for calculation
merged_data["Temp (°C)"] = merged_data["Temp (°C)"].fillna(0)
merged_data["Total Precip (mm)"] = merged_data["Total Precip (mm)"].fillna(0)


merged_data["Hour"] = merged_data["Date/Time (LST)"].dt.hour


chart_data=pd.DataFrame(
    data=merged_data, 
    columns=["Date/Time (LST)","Temp (°C)", "Total Precip (mm)", "Mean Temp (°C)"]
    )

chart_data.set_index("Date/Time (LST)", inplace=True)




################### WELCOME PAGE ##################################

# variables:
today=datetime.date.today()

st.write("## Wealcome to Simply Visualize Weather!")


user_goal = st.selectbox(
    "From the Drop Down menu, please choose what I can help you with",
    ("N/A","Is it safe to get out today or next 7 days for a student and/or babiles?", "I'd like to see historical data on weather to keep an eye on climate change")
)

st.divider()

if user_goal=="N/A":
    st.header("This is an experimental project, where I am going to try and see if any of my data insterests you. Let's go!!!")
elif user_goal=="Is it safe to get out today or next 7 days for a student and/or babiles?":
    st.subheader("Showing forecast data for the next 7 days ...")
    st.line_chart(daily_7_data)
    st.divider()
    st.subheader("Data in Table Format")
    st.dataframe(daily_7_data,use_container_width=True)
elif user_goal == "I'd like to see historical data on weather to keep an eye on climate change":
    st.subheader("Choose a research month and year")
    st.line_chart(chart_data)
    st.divider()
    st.subheader("Data in Table Format")
    st.dataframe(merged_data, use_container_width=True)
    st.write(merged_data)



    

st.divider()
st.write("Don't Forget to Rate Your Experience With Us!")
experience_rate = ["one","two", "three", "four", "five"]
selected_stars=st.feedback("stars")
st.divider()



#######################################  Visualizing the Data #################################





#def is_good_weather(temp, precip):
#    return (15 <= temp <= 25) and (precip == 0)

