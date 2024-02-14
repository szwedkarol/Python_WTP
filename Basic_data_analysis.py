# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw

import datetime
import csv
import time

filename = "Buses_location_all.csv"

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


import csv
import datetime
import geopy.distance
from collections import defaultdict

def calculate_distance(coords_1, coords_2):
    return geopy.distance.geodesic(coords_1, coords_2).meters  # convert to meters

def calculate_time_diff(time_1, time_2):
    time_format = "%H:%M:%S"
    t1 = datetime.datetime.strptime(time_1, time_format)
    t2 = datetime.datetime.strptime(time_2, time_format)
    return (t2 - t1).seconds  # keep as seconds

def calculate_average_speed(filename, bus_line='189'):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        bus_189_rows = [row for row in rows if row[0] == bus_line]
        vehicle_rows = defaultdict(list)
        for row in bus_189_rows:
            vehicle_rows[row[-1]].append(row)
        for vehicle, rows in vehicle_rows.items():
            if len(rows) < 3:
                print(f"Not enough data to calculate the average speed of vehicle {vehicle}")
                continue
            total_distance = 0
            total_time = 0
            for i in range(2):
                coords_1 = (float(rows[i][1]), float(rows[i][2]))
                coords_2 = (float(rows[i+1][1]), float(rows[i+1][2]))
                total_distance += calculate_distance(coords_1, coords_2)
                total_time += calculate_time_diff(rows[i][3], rows[i+1][3])
            average_speed = total_distance / total_time  # m/s
            print(f"The average speed of vehicle {vehicle} is {average_speed} m/s, time: {total_time} seconds, distance: {total_distance} meters")

calculate_average_speed('Buses_location_all.csv', bus_line='317')
