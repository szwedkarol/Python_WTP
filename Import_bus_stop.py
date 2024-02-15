# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Parse the data from the JSON file

import json
import pandas as pd
import warsaw_data_api
import csv

bus_gps_file = "Buses_location_afternoon.csv"
file_json = open("bus_stops.json", "r")
json_dict = json.loads(file_json.read())

# Extract the list of dictionaries
dict_list = json_dict['result']

# Convert each dictionary in the list
new_dict_list = []
for d in dict_list:
    new_dict = {item['key']: item['value'] for item in d['values']}
    new_dict_list.append(new_dict)

# Convert the list of new dictionaries into a DataFrame
bus_stops_table = pd.DataFrame(new_dict_list)

# Drop the last column
last_column = bus_stops_table.columns[-1]
bus_stops_table = bus_stops_table.drop(last_column, axis=1)

# Rename the columns
bus_stops_table.columns = ["stop_id", "stop_pole", "stop_name",
                           "street_id", "latitude", "longitude", "direction"]

print(bus_stops_table.head())
print(bus_stops_table.shape)

# TASK: Create a dictionary matching bus lines to bus stops

_MY_API_KEY = "2620c061-1099-44d9-baab-fdc3a772ab29"  # my api key
ztm = warsaw_data_api.ztm(apikey=_MY_API_KEY)  # pass api key

#schedule = ztm.get_lines_for_bus_stop_id("7009", "01")
#print(schedule)

bus_line_stops = {}
for index, row in bus_stops_table.iterrows():
    stop_id = row['stop_id']
    stop_pole = row['stop_pole']
    stop_info = tuple(row.values)
    bus_lines = ztm.get_lines_for_bus_stop_id(stop_id, stop_pole)

    # DEBUG
    print(stop_info)
    print(bus_lines)

    for bus_line in bus_lines:
        if bus_line not in bus_line_stops:
            bus_line_stops[bus_line] = set()
        bus_line_stops[bus_line].add(stop_info)

print(bus_line_stops['504'])


