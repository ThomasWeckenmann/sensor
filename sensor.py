import numpy as np
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dateutil.parser import parse
import altair as alt
from dateutil.relativedelta import *

high_value = 30
box_id = "5e92b3e9df8258001bdfc8eb"
osm_url = f"https://api.opensensemap.org/boxes/{box_id}"
osm_url1000 = "https://api.opensensemap.org/boxes/{box_id}/data/{sensor_id}?&download=true&format=json"


rohr_data_osm = requests.get(osm_url).json()
sensors = rohr_data_osm["sensors"]
sensor_date = parse(sensors[0]["lastMeasurement"]["createdAt"]) + timedelta(hours=2)
df = pd.DataFrame()

st.header(rohr_data_osm["name"])
for sensor in sensors:
    st.write(sensor["lastMeasurement"]["value"], sensor["unit"], sensor["title"])
    url1000 = osm_url1000.format(**{"box_id": box_id, "sensor_id": sensor["_id"]})
    sensor_data1000 = requests.get(url1000).json()
    values = []
    dates = []
    if sensor["title"] == "PM10":
        pm10_values_high = {}
    if sensor["title"] == "PM2.5":
        pm25_values_high= {}
    for sensor_data in sensor_data1000:
        value = float(sensor_data["value"])
        values.append(value)
        value_date = parse(sensor_data["createdAt"]) + timedelta(hours=2)
        date = value_date.strftime('%d.%m.%y %H:%M:%S')
        dates.append(date)
        if sensor["title"] == "PM10" and value >= high_value:
            pm10_values_high[date] = value
        if sensor["title"] == "PM2.5" and value >= high_value:
            pm25_values_high[date] = value
    try:
        df[sensor["title"].replace(".", "")] = values
        df["date"] = dates
    except:
        pass
st.write("gemessen um ", sensor_date.strftime('%H:%M:%S'), "Uhr")

pm10 = alt.Chart(df).mark_line().encode(x='date',y='PM10')
pm025 = alt.Chart(df).mark_line().encode(x='date',y='PM25')
st.write("PM2.5 Values over 40:", pm25_values_high)
st.write("PM10 Values over 40:", pm10_values_high)
st.altair_chart(pm10)
st.altair_chart(pm025)
