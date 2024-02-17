# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Parse the data from the JSON file containing bus stops

import json
import pandas as pd
import warsaw_data_api


"""
 * INPUT:
    - "json_filename" - name of the JSON file containing bus stop data
 * FUNCTION: This function reads a JSON file containing bus stop data, extracts the necessary information, and
    transforms it into a pandas DataFrame. Renames the remaining columns for clarity.
 * OUTPUT: Returns a pandas DataFrame containing the bus stop data with columns: "stop_id", "stop_pole", "stop_name",
    "street_id", "latitude", "longitude", "direction".
"""
def extract_bus_stop_data(bus_stop_filename):
    json_file = open(bus_stop_filename, "r")

    # Load the JSON file
    json_dict = json.loads(json_file.read())

    # Extract the list of dictionaries
    dict_list = json_dict['result']

    # Convert each dictionary in the list
    new_dict_list = []
    for d in dict_list:
        new_dict = {item['key']: item['value'] for item in d['values']}
        new_dict_list.append(new_dict)

    # Convert the list of new dictionaries into a DataFrame
    bus_stops_table = pd.DataFrame(new_dict_list)

    # Drop the last column as it contains no useful information for us (route ID)
    last_column = bus_stops_table.columns[-1]
    bus_stops_table = bus_stops_table.drop(last_column, axis=1)

    # Rename the columns
    bus_stops_table.columns = ["stop_id", "stop_pole", "stop_name",
                               "street_id", "latitude", "longitude", "direction"]

    return bus_stops_table


"""
 * INPUT:
    - "bus_stops_info" - a pandas DataFrame containing bus stop data.
    - "ztm" - an instance of the WarsawDataAPI class, used to make API calls to the Warsaw Open Data API.
 * FUNCTION: Iterates over each row in the "bus_stops_info", and for each bus stop, it retrieves the bus lines that stop
    there using the WarsawDataAPI. It then stores this information in a dictionary.
 * OUTPUT: Returns a dictionary where the keys are bus lines and the values are sets of tuples, each tuple representing
    a bus stop and containing the same data as a row in the "bus_stops_info" DataFrame.
"""
def create_dict_matching_bus_stops_to_lines(bus_stops_info, ztm):
    bus_line_stops_dict = {}
    for _, row in bus_stops_info.iterrows():
        stop_id = row['stop_id']
        stop_pole = row['stop_pole']
        stop_info = tuple(row.values)
        bus_lines = ztm.get_lines_for_bus_stop_id(stop_id, stop_pole)

        for bus_line in bus_lines:
            if bus_line not in bus_line_stops_dict:
                bus_line_stops_dict[bus_line] = set()
            bus_line_stops_dict[bus_line].add(stop_info)

    return bus_line_stops_dict


# Example of usage for extract_bus_stop_data():
# _BUS_STOPS_JSON_FILENAME = "bus_stops.json"
# bus_stops_df = extract_bus_stop_data(_BUS_STOPS_JSON_FILENAME)
#
# print(bus_stops_df.head())
# print(bus_stops_df.shape)

# Example of usage for create_dict_matching_bus_stops_to_lines():
# (!) First we have to run the extract_bus_stop_data() function to get the bus_stops_df DataFrame (!)
# _MY_API_KEY = "2620c061-1099-44d9-baab-fdc3a772ab29"  # My api key
# _ZTM = warsaw_data_api.ztm(apikey=_MY_API_KEY)  # Pass api key
# bus_line_stops = create_dict_matching_bus_stops_to_lines(bus_stops_df, _ZTM)
#
# print(bus_line_stops['504'])


