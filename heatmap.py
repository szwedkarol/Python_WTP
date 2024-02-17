# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Drawing a heatmap on a real world map.


import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.colors import Normalize
import numpy as np
from scipy.stats import gaussian_kde


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
