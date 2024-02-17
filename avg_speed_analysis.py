# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw


import csv
import datetime
import geopy.distance
from collections import defaultdict
import pandas as pd
import my_pickle_save
import matplotlib.pyplot as plt
from heatmap import plot_heatmap_on_map


_BUS_GPS_FILENAME = "Buses_location_afternoon.csv"


# Return distance between two coordinates
def calculate_distance(coords_1, coords_2):
    return geopy.distance.geodesic(coords_1, coords_2).meters  # convert to meters


# Return middle point between two coordinates
def calculate_avg_coords(coords_1, coords_2):
    return (coords_1[0] + coords_2[0]) / 2, (coords_1[1] + coords_2[1]) / 2


# Calculate time difference between two times. Return time difference in seconds
def calculate_time_diff(time_1, time_2):
    time_format = "%H:%M:%S"
    t1 = datetime.datetime.strptime(time_1, time_format)
    t2 = datetime.datetime.strptime(time_2, time_format)
    return (t2 - t1).seconds  # Keep as seconds


# Returns all rows from a given CSV file that contain passed as parameter "vehicle_nr"
def get_vehicle_data(filename, vehicle_nr):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        bus_rows = [row for row in rows if row[-1] == vehicle_nr]
        vehicle_rows = defaultdict(list)
        for row in bus_rows:
            vehicle_rows[row[-1]].append(row)
        return vehicle_rows


# Returns a list of unique vehicle numbers present in the dataset
def get_vehicle_numbers(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        vehicle_numbers = set(row[-1] for row in rows)
        return list(vehicle_numbers)


# Returns a list of vehicle numbers for a given bus line
def get_vehicle_numbers_for_line(filename, bus_line):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        bus_rows = [row for row in rows if row[0] == bus_line]
        vehicle_numbers = set(row[-1] for row in bus_rows)
        return list(vehicle_numbers)


# Returns a list of tuples with average speed information (across all consecutive GPS points)
def calculate_avg_speeds(filename, vehicle):
    vehicle_rows = get_vehicle_data(filename, vehicle)
    rows = vehicle_rows[vehicle]
    if len(rows) < 2:
        # Not enough GPS points to calculate average speed
        return None
    speeds = []
    for i in range(len(rows) - 1):
        coords_1 = (float(rows[i][1]), float(rows[i][2]))
        coords_2 = (float(rows[i + 1][1]), float(rows[i + 1][2]))
        distance = calculate_distance(coords_1, coords_2)
        time_diff = calculate_time_diff(rows[i][3], rows[i + 1][3])
        avg_speed = distance / time_diff  # m/s
        speeds.append((avg_speed, rows[i][3], rows[i + 1][3]))
    return speeds


def get_avg_speeds_for_vehicles_for_line(filename, bus_line):
    vehicle_numbers = get_vehicle_numbers_for_line(filename, bus_line)
    avg_speeds_for_line = {}
    for vehicle in vehicle_numbers:
        avg_speeds_for_line[vehicle] = calculate_avg_speeds(filename, vehicle)
    return avg_speeds_for_line


# Calculate the total distance traveled by a vehicle
def calculate_total_distance(filename, vehicle_nr):
    total_dist = 0
    rows = get_vehicle_data(filename, vehicle_nr)
    if len(rows) < 2:
        return total_dist
    for i in range(len(rows) - 1):
        coords_1 = (float(rows[i][1]), float(rows[i][2]))
        coords_2 = (float(rows[i + 1][1]), float(rows[i + 1][2]))
        distance = calculate_distance(coords_1, coords_2)
        total_dist += distance
    return total_dist


# Calculate total time traveled by a vehicle
def calculate_total_time(filename, vehicle_nr):
    total_time = 0
    rows = get_vehicle_data(filename, vehicle_nr)
    if len(rows) < 2:
        return total_time
    for i in range(len(rows) - 1):
        time_diff = calculate_time_diff(rows[i][3], rows[i + 1][3])
        total_time += time_diff
    return total_time


# Calculate the average speed of a vehicle
def calculate_avg_speed(filename, vehicle_nr):
    total_distance = calculate_total_distance(filename, vehicle_nr)
    total_time = calculate_total_time(filename, vehicle_nr)

    if total_time == 0:
        return 0

    return total_distance / total_time


# Example of usage:
# avg_speed_line = get_avg_speeds_for_all_vehicles(_BUS_GPS_FILENAME, '317')
# print(avg_speed_line)
#
# _BUS_GPS_FILENAME = "Buses_location_afternoon.csv"
# basic_stats_on_csv_file(_BUS_GPS_FILENAME)
# calculate_average_speed_basic(_BUS_GPS_FILENAME, '317')

# Calculate the average speed of all vehicles
# avg_speeds = calculate_avg_speeds_for_all_vehicles(_BUS_GPS_FILENAME)
# my_pickle_save.save_obj_as_pickle_file("avg_speeds.pkl", avg_speeds)


# How many buses at some point were driving above 50 km/h?

# Create a new DataFrame, with average speed for each consecutive pair of GPS points for a given vehicle


def granular_avg_speeds_for_vehicle(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        rows = list(reader)
        vehicle_data_dict = defaultdict(list)
        for row in rows:
            bus_line = row[0]
            vehicle_nr = row[-1]
            coords = (float(row[1]), float(row[2]))
            new_time = row[3]

            if vehicle_data_dict[vehicle_nr]:
                last_latitude = vehicle_data_dict[vehicle_nr][-1][4]
                last_longitude = vehicle_data_dict[vehicle_nr][-1][5]
                last_time = vehicle_data_dict[vehicle_nr][-1][3]
                last_coords = (last_latitude, last_longitude)
                distance = calculate_distance(last_coords, coords)
                time_diff = calculate_time_diff(last_time, new_time)
                avg_speed = distance / time_diff if time_diff != 0 else 0  # m/s
                avg_coords = calculate_avg_coords(last_coords, coords)
                vehicle_data_dict[vehicle_nr].append(
                    (bus_line, distance, last_time, new_time, avg_coords[0], avg_coords[1], avg_speed))
            else:
                vehicle_data_dict[vehicle_nr].append((bus_line, 0, new_time, new_time, coords[0], coords[1], 0))

        # Flatten the dictionary into a list of lists
        vehicle_data_list = [[vehicle_nr] + list(data) for vehicle_nr, data_list in vehicle_data_dict.items() for data
                             in data_list]

        # Create a DataFrame from the list of lists
        vehicle_data_df = pd.DataFrame(vehicle_data_list, columns=['vehicle_nr', 'bus_line', 'distance_meters',
                                                                   'time_start', 'time_end', 'latitude', 'longitude',
                                                                   'avg_speed_mps'])

        return vehicle_data_df


granular_speeds = granular_avg_speeds_for_vehicle(_BUS_GPS_FILENAME)
print(granular_speeds)
print(granular_speeds.max())

# Count the number of times each vehicle exceeded 25 m/s (90 km/h)
num_speeding = granular_speeds[granular_speeds['avg_speed_mps'] > 25].groupby('vehicle_nr').size()
print(num_speeding)

# Remove rows where the average speed is above 25 m/s (90 km/h)
granular_speeds = granular_speeds[granular_speeds['avg_speed_mps'] <= 25]

# Plot on heatmap the average speed of each vehicle
warsaw_map_img = "WAW_MAP.png"
latitude_span = (52.1289, 52.3473)
longitude_span = (20.7992, 21.2386)

hotness = 'avg_speed_mps'
plot_heatmap_on_map(granular_speeds, warsaw_map_img, latitude_span, longitude_span, hotness)


"""
 * INPUT:
    - "filename" - a string representing the name of the CSV file containing bus GPS data.
 * FUNCTION: Reads the bus GPS data from the CSV file, calculates the total distance traveled and total time spent by
    each vehicle, and calculates the average speed of each vehicle.
 * OUTPUT: Returns a pandas DataFrame with the vehicle number as the index and columns for the bus line, total distance
    (in meters), and total time (in minutes). The DataFrame is sorted by the total distance in descending order.
"""
def calculate_avg_speeds_for_all_vehicles(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        rows = list(reader)
        vehicle_data = {}
        for row in rows:
            bus_line = row[0]
            vehicle_nr = row[-1]
            coords = (float(row[1]), float(row[2]))

            if vehicle_nr not in vehicle_data:
                vehicle_data[vehicle_nr] = [bus_line, 0, 0, (coords, row[3])]  # total_distance, total_time, last_row
            else:
                last_coords, last_time = vehicle_data[vehicle_nr][3]
                distance = calculate_distance(last_coords, coords)
                time_diff = calculate_time_diff(last_time, row[3])
                vehicle_data[vehicle_nr][1] += distance
                vehicle_data[vehicle_nr][2] += time_diff
                vehicle_data[vehicle_nr][3] = (coords, row[3])

        # Convert the vehicle_data dictionary to a list of dictionaries
        vehicle_data_list = [
            {'vehicle_nr': vehicle_nr, 'bus_line': data[0], 'total_distance_meters': round(data[1]),
             'total_time_mins': round(data[2] / 60, 1)}
            for vehicle_nr, data in vehicle_data.items()]

        # Create a DataFrame from the list of dictionaries
        vehicle_data_df = pd.DataFrame(vehicle_data_list)
        vehicle_data_df = vehicle_data_df.set_index('vehicle_nr')

        return vehicle_data_df


# Example of usage:
# Total distance traveled by all vehicles
# avg_speeds = my_pickle_save.load_obj_from_pickle_file("avg_speeds.pkl")
#
# avg_speeds_rush = my_pickle_save.load_obj_from_pickle_file("avg_speeds_rush.pkl")
#
# avg_speeds = avg_speeds.sort_values(by='total_distance_meters', ascending=False)
# avg_speeds_rush = avg_speeds_rush.sort_values(by='total_distance_meters', ascending=False)
#
# print(avg_speeds)
# print(avg_speeds_rush)
#
# # Calculate total distance traveled for all buses
# total_distance = avg_speeds['total_distance_meters'].sum()
# print(total_distance)
#
# # Second dataset
# total_distance_rush = avg_speeds_rush['total_distance_meters'].sum()
# print(total_distance_rush)

# Plot
# Line plot of the average speed of each bus line


"""
 * INPUT:
    - "avg_speeds_per_vehicle" - a DataFrame containing the total distance traveled and total time spent by each vehicle.
 * FUNCTION: Groups the DataFrame by the 'bus_line' column, calculates the total distance and total time for each
    bus line, and then calculates the average speed for each bus line.
 * OUTPUT: Returns a DataFrame with the bus line as the index and columns for the total distance (in meters),
    total time (in minutes), and average speed (in km/h).
"""
def calculate_avg_speeds_per_line(avg_speeds_per_vehicle):
    # Group by 'bus_line' and calculate the total distance and total time for each bus line
    line_data = avg_speeds_per_vehicle.groupby('bus_line').agg({'total_distance_meters': 'sum',
                                                                'total_time_mins': 'sum'})

    # Calculate the average speed for each bus line in kilometers per hour (km/h)
    line_data['avg_speed_kph'] = (line_data['total_distance_meters'] / 1000) / (line_data['total_time_mins'] / 60)

    return line_data


"""
 * INPUT:
    - "speeds_per_line" - a DataFrame with the bus line as the index and a column for the average speed (in km/h).
 * FUNCTION: Plots the average speed for each bus line.
 * OUTPUT: None. It creates a line plot of the average speed for each bus line, sorted in descending order by the
    average speed. The y-axis label is set to 'Average Speed (in km/h)', and the x-axis labels are hidden.
"""
def plot_avg_speed_per_line(speeds_per_line):
    speeds_per_line = speeds_per_line.sort_values(by='avg_speed_kph', ascending=False)
    plt.figure(figsize=(10, 6))
    plt.plot(speeds_per_line.index.tolist(), speeds_per_line['avg_speed_kph'].values.tolist())
    plt.ylabel('Average Speed (in km/h)')
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)  # hide x-axis labels

    # Add horizontal lines
    for y in range(0, int(speeds_per_line['avg_speed_kph'].max()) + 1, 1):  # change the step size to your preference
        plt.axhline(y, color='gray', linewidth=0.5)

    plt.show()

# Example of usage:
# avg_speeds_per_line = calculate_avg_speeds_per_line(avg_speeds)
# plot_avg_speed_per_line(avg_speeds_per_line)
