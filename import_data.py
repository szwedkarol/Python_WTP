# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Importing data from Warsaw Open Data API

# API key
# 2620c061-1099-44d9-baab-fdc3a772ab29

import warsaw_data_api
import datetime
import csv
import time

filename = "Buses_location_all.csv"
_MY_API_KEY = "2620c061-1099-44d9-baab-fdc3a772ab29"  # my api key
ztm = warsaw_data_api.ztm(apikey=_MY_API_KEY)  # pass api key

start_time = time.time()

timespan = 3600  # 60 minutes
time_delta_for_buses = 60  # 1 minute
update_interval = 60  # 1 minute

print("Starting the data import at", datetime.datetime.now())
print("Expected to end the data import at", datetime.datetime.now() + datetime.timedelta(seconds=timespan))

with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["lines", "latitude", "longitude", "time", "brigade", "vehicle_number"])  # write header

while True:
    try:
        buses_all = ztm.get_buses_location()
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            for bus in buses_all:
                now = datetime.datetime.now()
                time_diff = now - bus.time
                if time_diff.seconds < time_delta_for_buses:
                    writer.writerow([bus.lines, bus.location.latitude, bus.location.longitude,
                                     bus.time.time(), bus.brigade, bus.vehicle_number])
        time.sleep(update_interval)  # wait for 1 minute
        if time.time() - start_time > timespan:  # if 5 minutes have passed, break the loop
            break
    except Exception:  # if an error occurs, ignore it and try again
        continue
