import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



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
print(filtered_daily_data)

############################################ MERGED ######################################

merged_data=pd.merge(filtered_hourly_data, filtered_daily_data, on="Date", how="left")
print(merged_data)

# Convert to numeric, coerce errors to NaN
merged_data["Temp (°C)"] = pd.to_numeric(merged_data["Temp (°C)"], errors="coerce")
merged_data["Total Precip (mm)"] = pd.to_numeric(merged_data["Total Precip (mm)"], errors="coerce")

# Replace NaNs with 0 (or another choice) just for calculation
merged_data["Temp (°C)"] = merged_data["Temp (°C)"].fillna(0)
merged_data["Total Precip (mm)"] = merged_data["Total Precip (mm)"].fillna(0)


merged_data["Hour"] = merged_data["Date/Time (LST)"].dt.hour

def is_good_weather(temp, precip):
    return (15 <= temp <= 25) and (precip == 0)

merged_data["GoodForStudy"] = merged_data.apply(
    lambda row: is_good_weather(row["Temp (°C)"], row["Total Precip (mm)"]),
    axis=1
)

merged_data["GoodForStudyNum"] = merged_data["GoodForStudy"].astype(int)

pivot = merged_data.pivot_table(
    index="Date", 
    columns="Hour", 
    values="GoodForStudyNum", 
    aggfunc="mean"
)


plt.figure(figsize=(12,6))
plt.imshow(pivot, aspect="auto", cmap="RdYlGn")
plt.colorbar(label="Good Weather (1=True, 0=False)")
plt.xticks(range(24), range(24))
plt.yticks(range(len(pivot.index)), pivot.index)
plt.xlabel("Hour of Day")
plt.ylabel("Date")
plt.title("Best Hours for Outdoor Study in Ottawa")
plt.tight_layout()
plt.show()

##print(filtered_daily_data.columns)
##print(url_data.info())
##print(filtered_daily_data.head())