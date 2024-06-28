# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Test the import_bus_stop.py module.

import unittest
import pandas as pd
from import_bus_stop import extract_bus_stop_data, create_dict_matching_bus_stops_to_lines
import warsaw_data_api


class TestImportBusStop(unittest.TestCase):

    def test_extract_bus_stop_data(self):
        # Use a sample JSON file for testing
        bus_stops_df = extract_bus_stop_data('sample_bus_stops.json')

        # Check the DataFrame's shape and columns
        self.assertEqual(bus_stops_df.shape, (5, 7))  # Assuming the sample file has 5 rows and 7 columns
        self.assertEqual(list(bus_stops_df.columns),
                         ["stop_id", "stop_pole", "stop_name", "street_id", "latitude", "longitude", "direction"])

    def test_create_dict_matching_bus_stops_to_lines(self):
        # Use a sample DataFrame for testing
        bus_stops_df = pd.DataFrame({
            'stop_id': ['1', '2'],
            'stop_pole': ['A', 'B'],
            'stop_name': ['Stop 1', 'Stop 2'],
            'street_id': ['100', '200'],
            'latitude': ['52.2297', '52.4064'],
            'longitude': ['21.0122', '16.9252'],
            'direction': ['N', 'S']
        })

        _MY_API_KEY = "REPLACE"  # My api key
        _ZTM = warsaw_data_api.ztm(apikey=_MY_API_KEY)  # Pass api key

        bus_line_stops = create_dict_matching_bus_stops_to_lines(bus_stops_df, _ZTM)

        # Check the keys and values in the dictionary
        self.assertEqual(set(bus_line_stops.keys()), {'504'})  # Assuming the API returns only '504' for the sample data
        self.assertEqual(len(bus_line_stops['504']), 2)  # There should be 2 stops for '504'


if __name__ == '__main__':
    unittest.main()
