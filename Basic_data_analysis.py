# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw

import time
import csv
import datetime
import geopy.distance
from collections import defaultdict


def basic_stats_on_csv_file(filename):
    # Read csv file and print the first 5 rows
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for i in range(5):
            print(next(reader))

    # Count the number of distinct rows in the csv file (disregarding time)
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        # Exclude the time column from each row
        rows_without_time = [(row[0], row[1], row[2], row[4], row[5]) for row in rows]
        print(len(set(rows_without_time)))

    # Count the number of distinct rows in the csv file (including time)
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        print(len(set([tuple(row) for row in rows])))


def calculate_distance(coords_1, coords_2):
    return geopy.distance.geodesic(coords_1, coords_2).meters  # convert to meters


def calculate_time_diff(time_1, time_2):
    time_format = "%H:%M:%S"
    t1 = datetime.datetime.strptime(time_1, time_format)
    t2 = datetime.datetime.strptime(time_2, time_format)
    return (t2 - t1).seconds  # keep as seconds


def calculate_average_speed_basic(filename, bus_line):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        bus_rows = [row for row in rows if row[0] == bus_line]
        vehicle_rows = defaultdict(list)
        for row in bus_rows:
            vehicle_rows[row[-1]].append(row)
        for vehicle, rows in vehicle_rows.items():
            if len(rows) < 3:
                print(f"Not enough data to calculate the average speed of vehicle {vehicle}")
                continue
            total_distance = 0
            total_time = 0
            for i in range(2):
                coords_1 = (float(rows[i][1]), float(rows[i][2]))
                coords_2 = (float(rows[i + 1][1]), float(rows[i + 1][2]))
                total_distance += calculate_distance(coords_1, coords_2)
                total_time += calculate_time_diff(rows[i][3], rows[i + 1][3])
            average_speed = total_distance / total_time  # m/s
            print(
                f"The average speed of vehicle {vehicle} is {average_speed} m/s, time: {total_time} seconds,"
                f"distance: {total_distance} meters"
            )


def get_vehicle_data(filename, vehicle_nr):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        bus_rows = [row for row in rows if row[-1] == vehicle_nr]
        vehicle_rows = defaultdict(list)
        for row in bus_rows:
            vehicle_rows[row[-1]].append(row)
        return vehicle_rows


def get_vehicle_numbers(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        vehicle_numbers = set(row[-1] for row in rows)
        return list(vehicle_numbers)


def get_vehicle_numbers_for_line(filename, bus_line):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        bus_rows = [row for row in rows if row[0] == bus_line]
        vehicle_numbers = set(row[-1] for row in bus_rows)
        return list(vehicle_numbers)


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
    avg_speeds = {}
    for vehicle in vehicle_numbers:
        avg_speeds[vehicle] = calculate_avg_speeds(filename, vehicle)
    return avg_speeds


# Calculate the total distance traveled by a vehicle
def calculate_total_distance(filename, vehicle_nr):
    total_distance = 0
    rows = get_vehicle_data(filename, vehicle_nr)
    if len(rows) < 2:
        return total_distance
    for i in range(len(rows) - 1):
        coords_1 = (float(rows[i][1]), float(rows[i][2]))
        coords_2 = (float(rows[i + 1][1]), float(rows[i + 1][2]))
        distance = calculate_distance(coords_1, coords_2)
        total_distance += distance
    return total_distance


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
    return total_distance / total_time


def calculate_avg_speeds_for_all_vehicles(filename):
    vehicle_numbers = get_vehicle_numbers(filename)
    avg_speeds = {}
    for vehicle in vehicle_numbers:
        avg_speeds[vehicle] = calculate_avg_speed(filename, vehicle)
    return avg_speeds


_BUS_GPS_FILENAME = "Buses_location_afternoon.csv"
# Example of usage:
# avg_speed_line = get_avg_speeds_for_all_vehicles(_BUS_GPS_FILENAME, '317')
# print(avg_speed_line)
#
# _BUS_GPS_FILENAME = "Buses_location_afternoon.csv"
# basic_stats_on_csv_file(_BUS_GPS_FILENAME)
# calculate_average_speed_basic(_BUS_GPS_FILENAME, '317')

