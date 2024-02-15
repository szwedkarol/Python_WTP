# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Parse the data from the JSON file

import json
import pandas as pd

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
df = pd.DataFrame(new_dict_list)

# Drop the last column
last_column = df.columns[-1]
df = df.drop(last_column, axis=1)

# Rename the columns
df.columns = ["stop_id", "stop_pole", "stop_name", "street_id", "latitude", "longitude", "direction"]

print(df.head())
print(df.shape)


