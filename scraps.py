# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Scraps of code

# API key
# 2620c061-1099-44d9-baab-fdc3a772ab29

import warsaw_data_api
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
import geopy.distance

coords_1 = (52.24194, 21.041805)  # 13:15:22
coords_2 = (52.241966, 21.041813)  # 13:13:14

print(geopy.distance.geodesic(coords_1, coords_2).km)
