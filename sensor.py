import numpy as np
import requests
import streamlit as st
from dateutil.parser import parse
from dateutil.relativedelta import *

osm_url = "https://api.opensensemap.org/boxes/5e92b3e9df8258001bdfc8eb"
rohr_data_osm = requests.get(osm_url).json()
sensors = rohr_data_osm["sensors"]
sensor_date = parse(sensors[0]["lastMeasurement"]["createdAt"]) + relativedelta(hour=2)
required_date = sensor_date.strftime("%a %d %b %Y, %H:%M:%S GMT")


st.header(rohr_data_osm["name"])
for sensor in sensors:
    st.write(sensor["lastMeasurement"]["value"], sensor["unit"], sensor["title"])
    
st.write(sensor_date)