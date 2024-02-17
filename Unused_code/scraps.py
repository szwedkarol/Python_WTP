# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Scraps of code

# API key
# 2620c061-1099-44d9-baab-fdc3a772ab29

import warsaw_data_api
import csv
import datetime

_MY_API_KEY = "2620c061-1099-44d9-baab-fdc3a772ab29"  # my api key
ztm = warsaw_data_api.ztm(apikey=_MY_API_KEY)  # pass api key

# lines = ztm.get_lines_for_bus_stop_id("7009", "01")
# print(lines)

# buses_single = ztm.get_buses_location(line="182")
# buses_all = ztm.get_buses_location()

# for bus in buses:
#     now = datetime.datetime.now()
#     time_diff = now - bus.time
#     if time_diff.seconds < 60:
#         print(bus)

# for bus in buses_single:
#     now = datetime.datetime.now()
#     time_diff = now - bus.time
#     if time_diff.seconds < 60:
#         print(bus, bus.time, bus.brigade, bus.vehicle_number)
#
# schedule = ztm.get_bus_stop_schedule_by_name("Marszałkowska", "01", "182")
# for ride in schedule.rides:
#     print(ride)

# Calculate distance between two points with given coordinates
# import geopy.distance
#
# coords_1 = (52.24194, 21.041805)  # 13:15:22
# coords_2 = (52.241966, 21.041813)  # 13:13:14
#
# print(geopy.distance.geodesic(coords_1, coords_2).km)
#
#
# bus_gps_file = "Buses_location_afternoon.csv"
# def get_distinct_sorted_bus_lines(filename):
#     with open(filename, 'r') as file:
#         reader = csv.reader(file)
#         next(reader)  # Skip the header row
#         bus_lines = set(row[0] for row in reader)  # Extract bus lines and remove duplicates
#     return sorted(list(bus_lines))  # Convert to list and sort
#
#
# bus_lines = get_distinct_sorted_bus_lines(bus_gps_file)


_BUS_GPS_FILENAME = "../Buses_location_afternoon.csv"

# Find timestamps that have hour equal to 24
with open(_BUS_GPS_FILENAME, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        timestamp = row[3]  # assuming the timestamp is at index 3
        hour = timestamp.split(':')[0]  # get the hour part of the timestamp
        if hour == '24':
            print(row)


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



def plot_heatmap_on_map(bus_arrival, map_image_path, lat_bounds, lon_bounds):
    # Load the map image
    map_img = mpimg.imread(map_image_path)

    # Filter out points that do not fit on the map
    bus_arrival = bus_arrival[(bus_arrival['latitude'] >= lat_bounds[0]) & (bus_arrival['latitude'] <= lat_bounds[1]) &
                              (bus_arrival['longitude'] >= lon_bounds[0]) & (bus_arrival['longitude'] <= lon_bounds[1])]

    # Normalize the time difference values to a range suitable for color mapping
    norm = Normalize(vmin=bus_arrival['time_difference'].min(), vmax=bus_arrival['time_difference'].max())

    # Estimate the density of points
    xy = np.vstack([bus_arrival['longitude'], bus_arrival['latitude']])
    z = gaussian_kde(xy)(xy)

    # Create a grid of points covering the map
    xi, yi = np.mgrid[lon_bounds[0]:lon_bounds[1]:100j, lat_bounds[0]:lat_bounds[1]:100j]
    zi = gaussian_kde(xy)(np.vstack([xi.flatten(), yi.flatten()]))

    # Create a new figure
    plt.figure(figsize=(15, 10))

    # Display the map image
    plt.imshow(map_img, extent=[lon_bounds[0], lon_bounds[1], lat_bounds[0], lat_bounds[1]])

    # Plot the density as a heatmap
    plt.imshow(zi.reshape(xi.shape), origin='lower', aspect='auto',
               extent=[lon_bounds[0], lon_bounds[1], lat_bounds[0], lat_bounds[1]],
               cmap='hot', alpha=0.5)

    # Plot the points
    plt.scatter(bus_arrival['longitude'], bus_arrival['latitude'], c=z, cmap='hot', norm=norm, alpha=0.5, s=2)

    # Add a color bar
    plt.colorbar(label='time_difference (in mins)')

    # Show the plot
    plt.show()


"""
 * INPUT:
    - "bus_arrival" - a pandas DataFrame containing bus arrival data.
    - "map_image_path" - a string representing the path to the map image file.
    - "lat_bounds" - a tuple specifying the minimum and maximum latitude values of the map image.
    - "lon_bounds" - a tuple specifying the minimum and maximum longitude values of the map image.
    - "z_value" - a string representing the column name in the DataFrame that contains the values to be plotted.
 * FUNCTION: Filters out points that do not fit on the map, normalizes the time difference values to a
    range suitable for color mapping, estimates the density of points, creates a grid of points covering the map, and
    plots the density as a heatmap. It also plots the points on the map with their color representing the delay.
 * OUTPUT: None. As a side effect displays a heatmap of bus arrival times on a map image. The color on the map
    represents the time difference of the bus arrival, with 'hot' areas indicating longer delays.
"""
def plot_heatmap_on_map(df, map_image_path, lat_bounds, lon_bounds, z_value):
    # Load the map image
    map_img = mpimg.imread(map_image_path)

    # Filter out points that do not fit on the map
    df = df[(df['latitude'] >= lat_bounds[0]) & (df['latitude'] <= lat_bounds[1]) &
            (df['longitude'] >= lon_bounds[0]) & (df['longitude'] <= lon_bounds[1])]

    # Normalize the z_value values to a range suitable for color mapping
    norm = Normalize(vmin=df[z_value].min(), vmax=df[z_value].max())

    # Create a grid of points covering the map
    xi, yi = np.mgrid[lon_bounds[0]:lon_bounds[1]:100j, lat_bounds[0]:lat_bounds[1]:100j]
    zi = gaussian_kde(np.vstack([df['longitude'], df['latitude']]))(np.vstack([xi.flatten(), yi.flatten()]))

    # Create a new figure
    plt.figure(figsize=(15, 10))

    # Display the map image
    plt.imshow(map_img, extent=[lon_bounds[0], lon_bounds[1], lat_bounds[0], lat_bounds[1]])

    # Plot the density as a heatmap
    plt.imshow(zi.reshape(xi.shape), origin='lower', aspect='auto',
               extent=[lon_bounds[0], lon_bounds[1], lat_bounds[0], lat_bounds[1]],
               cmap='hot', alpha=0.5)

    # Plot the points with color corresponding to their average speed
    plt.scatter(df['longitude'], df['latitude'], c=df[z_value], cmap='hot', norm=norm, alpha=0.5, s=4)

    # Add a color bar
    plt.colorbar(label=f'{z_value}')

    # Show the plot
    plt.show()