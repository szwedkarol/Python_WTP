# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw

import warsaw_data_api
import datetime
import my_pickle_save
import pandas as pd
import geopy.distance

_MY_API_KEY = "2620c061-1099-44d9-baab-fdc3a772ab29"  # my api key
_ZTM = warsaw_data_api.ztm(apikey=_MY_API_KEY)  # pass api key
_BUS_GPS_FILENAME = "Buses_location_afternoon.csv"
_BUS_STOPS_FILENAME = "bus_line_stops.pkl"


def calculate_distance(lat1, lon1, lat2, lon2):
    coords_1 = (lat1, lon1)  # point A
    coords_2 = (lat2, lon2)  # point B
    return geopy.distance.geodesic(coords_1, coords_2).meters  # convert to meters


def read_data(gps_file, stops_file):
    bus_gps_data = pd.read_csv(gps_file)
    bus_stops_data = my_pickle_save.load_obj_from_pickle_file(stops_file)
    return bus_gps_data, bus_stops_data


def is_bus_near_stop(bus, bus_stops, distance_threshold=60):
    for _, stop in bus_stops.iterrows():
        distance = calculate_distance(bus['latitude'], bus['longitude'],
                                      stop['latitude'], stop['longitude'])
        if distance <= distance_threshold:
            return True, stop
    return False, None


def get_schedule(stop_id, stop_pole, line):
    return _ZTM.get_bus_stop_schedule_by_id(stop_id, stop_pole, line)


def is_matching_entry_in_schedule(schedule, brigade, bus_time, time_threshold=(-3, 20)):
    bus_time = datetime.datetime.strptime(bus_time, '%H:%M:%S')
    for ride in schedule.rides:
        scheduled_time = datetime.datetime.strptime(ride.time, '%H:%M:%S')
        time_difference = (scheduled_time - bus_time).total_seconds() / 60  # in minutes
        if time_threshold[0] <= time_difference <= time_threshold[1] and ride.brigade == brigade:
            return True, scheduled_time, time_difference
    return False, None, None


# TODO: Check if works and change "result" dataframe to have more columns (include bus stop data)
def calculate_time_difference():
    bus_gps_data, bus_stops_data = read_data(_BUS_GPS_FILENAME, _BUS_STOPS_FILENAME)
    result = pd.DataFrame()
    for _, bus in bus_gps_data.iterrows():
        is_near, stop = is_bus_near_stop(bus, bus_stops_data)
        if is_near:
            schedule = get_schedule(stop['stop_id'], stop['stop_pole'], bus['lines'])
            is_match, scheduled_time, time_difference = is_matching_entry_in_schedule(schedule, bus['brigade'], bus['time'])
            if is_match:
                bus['scheduled_time'] = scheduled_time.time().strftime('%H:%M:%S')
                bus['time_difference'] = time_difference
                result = result.append(bus)
    return result
