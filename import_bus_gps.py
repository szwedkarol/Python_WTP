# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Imports bus GPS data from Warsaw Open Data API

import warsaw_data_api
import datetime
import csv
import time

"""
 * INPUT:
     - "filename" - string with name of the csv file where data will be written to;
     - "_MY_API_KEY" - string with my API key needed for API calls;
     - "timespan" - integer representing amount of seconds for how long the data will be collected;
     - "time_delta_for_buses" - maximum age (in seconds) of the bus GPS data to be considered valid;
     - "update_interval" - time (in seconds) between each data import from the Warsaw Open Data API.
 * FUNCTION: Gather live bus GPS data using API calls and save it to csv file (with header).
 * OUTPUT: None; function has side effect of creating csv file with bus GPS data.
"""
def import_bus_gps_data(filename, _MY_API_KEY, timespan, time_delta_for_buses, update_interval):
    ztm = warsaw_data_api.ztm(apikey=_MY_API_KEY)  # Pass API key
    start_time = time.time()

    print("Starting the data import at", datetime.datetime.now())
    print("Expected to end the data import at", datetime.datetime.now() + datetime.timedelta(seconds=timespan))

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["lines", "latitude", "longitude", "time", "brigade", "vehicle_number"])  # Write header

    while True:
        try:
            buses_all = ztm.get_buses_location()
            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                for bus in buses_all:
                    now = datetime.datetime.now()
                    time_diff = now - bus.time

                    # We want to gather data that is current, so we only collect location data
                    # that is at most 1 min old
                    if time_diff.seconds < time_delta_for_buses:
                        writer.writerow([bus.lines, bus.location.latitude, bus.location.longitude,
                                         bus.time.time(), bus.brigade, bus.vehicle_number])
            time.sleep(update_interval)  # Wait for 1 minute between updates
            if time.time() - start_time > timespan:  # If timespan have passed, break the loop
                break
        except Exception:  # If an error occurs, ignore it and try again
            continue


# Example of usage:
# _BUS_GPS_DATA_FILENAME = "Buses_location_afternoon.csv"  # Where GPS data is saved
# _MY_API_KEY = "2620c061-1099-44d9-baab-fdc3a772ab29"  # My API key
#
# timespan = 3600  # 60 minutes
# time_delta_for_buses = 60  # 1 minute
# update_interval = 60  # 1 minute
#
# import_bus_gps_data(_BUS_GPS_DATA_FILENAME, _MY_API_KEY, timespan, time_delta_for_buses, update_interval)
