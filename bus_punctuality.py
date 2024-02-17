# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw

import warsaw_data_api
import datetime
import my_pickle_save
import csv
import pandas as pd
import geopy.distance
import matplotlib.pyplot as plt
from heatmap import plot_heatmap_on_map


# Calculate distance between two points, given as coordinates.
def calculate_distance(lat1, lon1, lat2, lon2):
    coords_1 = (lat1, lon1)  # point A
    coords_2 = (lat2, lon2)  # point B
    return geopy.distance.geodesic(coords_1, coords_2).meters  # convert to meters


# Read GPS and bus stops data from their respective files.
def read_data(gps_file, stops_file):
    bus_gps_data = pd.read_csv(gps_file)
    bus_stops_data = my_pickle_save.load_obj_from_pickle_file(stops_file)
    return bus_gps_data, bus_stops_data


# Check if a bus is within "distance_threshold" from any of its bus stops.
def is_bus_near_stop(bus, bus_stops_data, distance_threshold=60):
    bus_line = bus['lines']
    if bus_line in bus_stops_data:
        for stop in bus_stops_data[bus_line]:
            # Pass the bus and stop coordinates to the function;
            # stop[4] and stop[5] are latitude and longitude of the stop.
            distance = calculate_distance(bus['latitude'], bus['longitude'],
                                          stop[4], stop[5])
            if distance <= distance_threshold:
                return True, stop
    return False, None


# Return a schedule for a given bus stop id, stop pole number, and a bus line.
def get_schedule(stop_id, stop_pole, line):
    return _ZTM.get_bus_stop_schedule_by_id(stop_id, stop_pole, line)


# Change hour value in time stamp so that it is in format 'HH:MM:SS'
def check_if_ride_time_is_valid(ride_time):
    # Check if ride.time hour is bigger than 23 and if so, change it to 00
    # (we collected data outside the night)
    hour = int(ride_time.split(':')[0])
    if hour > 23:
        ride_time = '00' + ride_time[2:]
    return ride_time


"""
 * INPUT:
    - "schedule" - a Schedule object containing the bus schedule for a specific stop.
    - "brigade" - a string representing the brigade number of the bus.
    - "bus_time" - a string representing the time the bus was at the stop in the format 'HH:MM:SS'.
    - "time_threshold" - a tuple specifying the minimum and maximum time difference (in minutes) between the actual and
        scheduled arrival times for a match to be considered valid. Default is (-3, 20).
 * FUNCTION: Iterates over each ride in the schedule, checks if the brigade number matches, and if so,
    calculates the delay between the actual and scheduled arrival times. If the time difference is within the specified
    threshold, it considers it a match.
 * OUTPUT: Returns a tuple of three elements. The first element is a boolean indicating whether a match was found.
    The second element is the scheduled time of the matching ride (or None if no match was found).
    The third element is the delay between the actual and scheduled arrival times (or None if no match was found).
"""
def is_matching_entry_in_schedule(schedule, brigade, bus_time, time_threshold=(-3, 20)):
    bus_time = datetime.datetime.strptime(bus_time, '%H:%M:%S')
    for ride in schedule.rides:
        ride.time = check_if_ride_time_is_valid(ride.time)
        scheduled_time = datetime.datetime.strptime(ride.time, '%H:%M:%S')
        time_difference = (bus_time - scheduled_time).total_seconds() / 60  # in minutes

        if time_threshold[0] <= time_difference <= time_threshold[1] and ride.brigade == brigade:
            return True, scheduled_time, time_difference
    return False, None, None


"""
 * INPUT:
    - "results_filename" - a string representing the name of the CSV file where the results will be written.
 * FUNCTION: Reads bus GPS data and bus stops data, iterates over each bus in the GPS data, checks if the
    bus is near a stop, and if so, checks if there is a matching entry in the schedule for the bus. If there is a match,
    it calculates the time difference between the actual and scheduled arrival times, adds this information to the
    bus data, and writes the updated bus data to the results file. Thus bus arrival data is created.
 * OUTPUT: Returns a pandas DataFrame containing the updated bus data with additional columns for the scheduled time,
    time difference, and stop information. Also, as a side effect, it writes the updated bus data to a CSV file.
    This way updates are online and in case of a crash, the data is saved.
"""
def calculate_time_difference(results_filename):
    bus_gps_data, bus_stops_data = read_data(_BUS_GPS_FILENAME, _BUS_STOPS_FILENAME)
    result = pd.DataFrame(columns=bus_gps_data.columns.tolist() + ['scheduled_time', 'time_difference',
                                                                   'stop_id', 'stop_pole', 'stop_name'])

    file = open(results_filename, 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(result.columns.tolist())  # write header
    count_rows = 0
    for index, bus in bus_gps_data.iterrows():
        is_near, stop = is_bus_near_stop(bus, bus_stops_data)
        if is_near:
            # If bus stop ID is not in base 10, continue to the next iteration
            if not stop[0].isdigit():
                continue

            # Pass the stop_id, stop_pole and bus line number to the function
            schedule = get_schedule(stop[0], stop[1], bus['lines'])

            is_match, scheduled_time, time_difference = (
                is_matching_entry_in_schedule(schedule, bus['brigade'], bus['time'])
            )

            if is_match:
                bus['scheduled_time'] = scheduled_time.time().strftime('%H:%M:%S')
                bus['time_difference'] = time_difference
                bus['stop_id'] = stop[0]  # stop['stop_id']
                bus['stop_pole'] = stop[1]  # stop['stop_pole']
                bus['stop_name'] = stop[2]  # stop['stop_name']

                # DEBUG
                # Print every 5th bus
                if count_rows % 5 == 0:
                    print(bus)

                count_rows += 1  # DEBUG

                result.loc[len(result)] = bus
                writer.writerow(bus.tolist())  # Write results row to CSV file
    file.close()
    return result


# Example of usage:
_MY_API_KEY = "2620c061-1099-44d9-baab-fdc3a772ab29"  # my api key
_ZTM = warsaw_data_api.ztm(apikey=_MY_API_KEY)  # pass api key
_BUS_GPS_FILENAME = "Buses_location_afternoon.csv"
_BUS_STOPS_FILENAME = "bus_line_stops.pkl"
# _BUS_PUNCTUALITY_RESULTS_FILENAME = "bus_punctuality_results.csv"
# bus_punctuality_df = calculate_time_difference(_BUS_PUNCTUALITY_RESULTS_FILENAME)
# print(bus_punctuality_df.head())
# print(bus_punctuality_df.shape)

# Load from a csv file
_BUS_PUNCTUALITY_RUSH_RESULTS_FILENAME = "bus_punctuality_rush_results.csv"
_BUS_PUNCTUALITY_RESULTS_FILENAME = "bus_punctuality_results.csv"

pd.set_option('display.max_columns', None)  # Display all columns

bus_punctuality_df = pd.read_csv(_BUS_PUNCTUALITY_RESULTS_FILENAME)
print(bus_punctuality_df.shape)
# print(bus_punctuality_df.head())

bus_punctuality_rush_df = pd.read_csv(_BUS_PUNCTUALITY_RUSH_RESULTS_FILENAME)
print(bus_punctuality_rush_df.shape)
# print(bus_punctuality_rush_df.head())

# Calculate the average time difference for all buses
avg_time_difference = bus_punctuality_df['time_difference'].mean()
print("Average time difference for buses:", avg_time_difference)

# Second dataset
avg_time_difference_rush = bus_punctuality_rush_df['time_difference'].mean()
print("Average time difference for rush hours:", avg_time_difference_rush)

# Calculate the average time difference for each bus line
avg_time_difference_per_line = bus_punctuality_df.groupby('lines')['time_difference'].mean()
print("Average time difference for each bus line:")
print(avg_time_difference_per_line.sort_values(ascending=False))

# Second dataset
avg_time_difference_per_line_rush = bus_punctuality_rush_df.groupby('lines')['time_difference'].mean()
print("Average time difference for each bus line during rush hours:")
print(avg_time_difference_per_line_rush.sort_values(ascending=False))


"""
 * INPUT:
    - "time_diff_per_line" - a pandas Series where the index is the bus line and the value is the average delay for
        that line.
 * FUNCTION: This function sorts the input Series in descending order, creates a new figure, and plots the average delay
    for each bus line.
 * OUTPUT: None. As a side effect, it displays a line plot of the average delay for each bus line.
"""
def plot_avg_time_difference_per_line(time_diff_per_line):
    time_diff_per_line = time_diff_per_line.sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    plt.plot(time_diff_per_line.index.tolist(), time_diff_per_line.values.tolist())
    plt.ylabel('time_difference (in mins)')
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)  # hide x-axis labels

    # Add horizontal lines
    for y in range(0, int(time_diff_per_line.max()) + 1, 1):  # change the step size to your preference
        plt.axhline(y, color='gray', linewidth=0.5)

    plt.show()


# Example of usage
# Plot the average time difference for each bus line
# plot_avg_time_difference_per_line(avg_time_difference_per_line)
# plot_avg_time_difference_per_line(avg_time_difference_per_line_rush)

# Example of usage:
warsaw_map_img = "WAW_MAP.png"
latitude_span = (52.1289, 52.3473)
longitude_span = (20.7992, 21.2386)
hotness = 'time_difference'

# Plot as heat map time difference for each record in the dataset on real world map
plot_heatmap_on_map(bus_punctuality_df, warsaw_map_img, latitude_span, longitude_span, hotness)
