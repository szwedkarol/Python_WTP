# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Importing bus schedules data from Warsaw Open Data API

# API key
# 2620c061-1099-44d9-baab-fdc3a772ab29

import warsaw_data_api
import datetime
import csv
import time

filename = "Buses_location_afternoon.csv"
_MY_API_KEY = "2620c061-1099-44d9-baab-fdc3a772ab29"  # my api key
ztm = warsaw_data_api.ztm(apikey=_MY_API_KEY)  # pass api key

schedule = ztm.get_bus_stop_schedule_by_id("7040", "06", "108")

ztm.get_bus_stop_schedule_by_name("Banacha-Szpital", "01", "504")

for ride in schedule.rides:
    print(ride.brigade, ride.time)
