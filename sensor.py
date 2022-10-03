import numpy as np
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dateutil.parser import parse
import altair as alt
from dateutil.relativedelta import *

box_id = "5e92b3e9df8258001bdfc8eb"
osm_url = f"https://api.opensensemap.org/boxes/{box_id}"
osm_url1000 = "https://api.opensensemap.org/boxes/{box_id}/data/{sensor_id}?&download=true&format=json"


rohr_data_osm = requests.get(osm_url).json()
sensors = rohr_data_osm["sensors"]
sensor_date = parse(sensors[0]["lastMeasurement"]["createdAt"]) + timedelta(hours=2)
df = pd.DataFrame()

sensor_data1000 = "s"
st.header(rohr_data_osm["name"])
for sensor in sensors:
    st.write(sensor["lastMeasurement"]["value"], sensor["unit"], sensor["title"])
    url1000 = osm_url1000.format(**{"box_id": box_id, "sensor_id": sensor["_id"]})
    sensor_data1000 = requests.get(url1000).json()
    values = []
    dates = []
    for sensor_data in sensor_data1000:
        values.append(float(sensor_data["value"]))
        value_date = parse(sensor_data["createdAt"]) + timedelta(hours=2)
        dates.append(value_date.strftime('%d.%m.%y %H:%M:%S'))
    try:
        df[sensor["title"].replace(".", "")] = values
        df["date"] = dates
    except:
        pass
st.write("gemessen um ", sensor_date.strftime('%H:%M:%S'), "Uhr")

pm10 = alt.Chart(df).mark_line().encode(x='date',y='PM10')
pm025 = alt.Chart(df).mark_line().encode(x='date',y='PM25')
st.altair_chart(pm10)
st.altair_chart(pm025)
