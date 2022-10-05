import numpy as np
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import *
from geopy.geocoders import Nominatim

box_ids = [
    "5e92b3e9df8258001bdfc8eb", 
    "5c377effc4c2f3001942a946", 
    "5d9ef41e25683a001ad916c3",
    "5b37aae81fef04001b41961f",
    "5e941c07df8258001b663b40"
]

class Box(object):
    def __init__(self, box_id):
        self.id = box_id
        self.box_data = None
        self.location = None
        self.address_string = ""
        self.df = pd.DataFrame()

        self._set_box_data()
        self._set_address()

    def _set_box_data(self):
        osm_url = f"https://api.opensensemap.org/boxes/{self.id}"
        self.box_data = requests.get(osm_url).json()

    def _set_address(self):
        long = str(self.box_data["currentLocation"]["coordinates"][0])
        lat = str(self.box_data["currentLocation"]["coordinates"][1])
        geolocator = Nominatim(user_agent="geoapiExercises")
        self.location = geolocator.reverse(lat+","+long)
        address = self.location.raw['address']
        suburb = address.get('suburb', '')
        if 'city' in address.keys():
            city = address.get('city', '')
        else:
            city = address.get('town', '')
        self.address_string = f" ({city} {suburb})"

    def get_sensor_data1000(self, sensor_id):
        sensor_dict = {"box_id": self.id, "sensor_id": sensor_id}
        osm_url1000 = "https://api.opensensemap.org/boxes/{box_id}/data/{sensor_id}?&download=true&format=json"
        url = osm_url1000.format(**sensor_dict)
        return requests.get(url).json()

    def add_past_sensor_measurements(self, sensor):
        values, dates = [], []
        for sensor_data in self.get_sensor_data1000(sensor["_id"]):
            values.append(float(sensor_data["value"]))
            dates.append(parse(sensor_data["createdAt"]) + timedelta(hours=2))
        try:
            if "date" not in self.df:
                self.df["date"] = dates
            self.df[sensor["title"].replace(".", "")] = values
        except:
            pass


def user_box_id_selection():
    
    box_id_dict = {}
    for box_id in box_ids:
        box = Box(box_id)
        combo_key = box.box_data["name"] + box.address_string
        box_id_dict[combo_key] = box_id
    combo_id_combo = st.sidebar.selectbox('Select a Box:',(box_id_dict))
    box_manual_input = st.sidebar.text_input("Or paste a Box ID:", "")
    if box_manual_input:
        box_id = box_manual_input
    else:
        box_id = box_id_dict[combo_id_combo]
    return box_id


def show_high_pm_values(box):
    high_value = st.slider('Show PM Values over (last 1000 measurements)', 10, 100, 40)
    df_high_10 = box.df[box.df["PM10"] > high_value]
    df_high_25 = box.df[box.df["PM25"] > high_value]
    merged_df_high = pd.concat([df_high_10, df_high_25], ignore_index = True, sort = False)
    merged_df_high['date'] = merged_df_high["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.write("PM Values over ", high_value, "(last 1000 measurements)", merged_df_high)
    

def show_pm_graphs(box):
    st.line_chart(box.df, x='date',y=['PM10', "PM25"], width=200, height=400)


def run(box_id):
    box = Box(box_id)
    sensors = box.box_data["sensors"]
    sensor_date = parse(sensors[0]["lastMeasurement"]["createdAt"]) + timedelta(hours=2)
    st.header(f"{box.box_data['name']} {box.address_string}")

    for sensor in sensors:
        st.write(sensor["lastMeasurement"]["value"], sensor["unit"], sensor["title"])
        if "PM" in sensor["title"]:
            box.add_past_sensor_measurements(sensor)
            
    st.write("Measurement from: ", sensor_date.strftime('%H:%M:%S %y-%m-%d'), "")
    show_high_pm_values(box)
    show_pm_graphs(box)
    

if __name__ == "__main__":
    run(user_box_id_selection())

