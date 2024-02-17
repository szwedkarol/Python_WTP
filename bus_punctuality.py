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


def calculate_distance(lat1, lon1, lat2, lon2):
    coords_1 = (lat1, lon1)  # point A
    coords_2 = (lat2, lon2)  # point B
    return geopy.distance.geodesic(coords_1, coords_2).meters  # convert to meters


def read_data(gps_file, stops_file):
    bus_gps_data = pd.read_csv(gps_file)
    bus_stops_data = my_pickle_save.load_obj_from_pickle_file(stops_file)
    return bus_gps_data, bus_stops_data


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


def get_schedule(stop_id, stop_pole, line):
    return _ZTM.get_bus_stop_schedule_by_id(stop_id, stop_pole, line)


def check_if_ride_time_is_valid(ride_time):
    # Check if ride.time hour is bigger than 23 and if so, change it to 00
    # (we collected data outside the night)
    hour = int(ride_time.split(':')[0])
    if hour > 23:
        ride_time = '00' + ride_time[2:]
    return ride_time


# Added "bus", "stop" argument for debugging purposes
def is_matching_entry_in_schedule(schedule, brigade, bus_time, time_threshold=(-3, 20)):
    bus_time = datetime.datetime.strptime(bus_time, '%H:%M:%S')
    for ride in schedule.rides:
        ride.time = check_if_ride_time_is_valid(ride.time)
        scheduled_time = datetime.datetime.strptime(ride.time, '%H:%M:%S')
        time_difference = (bus_time - scheduled_time).total_seconds() / 60  # in minutes

        if time_threshold[0] <= time_difference <= time_threshold[1] and ride.brigade == brigade:
            return True, scheduled_time, time_difference
    return False, None, None


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


# Plot
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


# Plot the average time difference for each bus line
plot_avg_time_difference_per_line(avg_time_difference_per_line)
plot_avg_time_difference_per_line(avg_time_difference_per_line_rush)
