# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Test the bus_punctuality.py module

import unittest
from unittest.mock import patch
from bus_punctuality import calculate_distance, is_bus_near_stop, is_matching_entry_in_schedule, check_if_ride_time_is_valid


class TestBusPunctuality(unittest.TestCase):

    def test_calculate_distance(self):
        # Test with known values
        distance = calculate_distance(52.2297, 21.0122, 52.4064, 16.9252)
        self.assertAlmostEqual(distance, 278349.458, places=3)

    def test_check_if_ride_time_is_valid(self):
        # Test with a time that should be changed
        time = check_if_ride_time_is_valid('24:30:00')
        self.assertEqual(time, '00:30:00')

        # Test with a time that should not be changed
        time = check_if_ride_time_is_valid('12:30:00')
        self.assertEqual(time, '12:30:00')

    @patch('bus_punctuality.calculate_distance')
    def test_is_bus_near_stop(self, mock_calculate_distance):
        # Mock the calculate_distance function to always return 50
        mock_calculate_distance.return_value = 50

        # Test with a bus that is near a stop
        bus = {'lines': '504', 'latitude': 52.2297, 'longitude': 21.0122}
        bus_stops_data = {'504': [['1', 'A', 'Stop 1', '100', 52.2297, 21.0122, 'N']]}
        is_near, stop = is_bus_near_stop(bus, bus_stops_data)
        self.assertTrue(is_near)
        self.assertEqual(stop, ['1', 'A', 'Stop 1', '100', 52.2297, 21.0122, 'N'])

        # Test with a bus that is not near a stop
        bus = {'lines': '505', 'latitude': 52.2297, 'longitude': 21.0122}
        is_near, stop = is_bus_near_stop(bus, bus_stops_data)
        self.assertFalse(is_near)
        self.assertIsNone(stop)

    def test_is_matching_entry_in_schedule(self):
        # Test with a schedule that has a matching entry
        schedule = MockSchedule([MockRide('12:30:00', '1')])
        is_match, scheduled_time, time_difference = is_matching_entry_in_schedule(schedule, '1', '12:31:00')
        self.assertTrue(is_match)
        self.assertEqual(scheduled_time.time().strftime('%H:%M:%S'), '12:30:00')
        self.assertEqual(time_difference, 1)

        # Test with a schedule that does not have a matching entry
        schedule = MockSchedule([MockRide('12:30:00', '2')])
        is_match, scheduled_time, time_difference = is_matching_entry_in_schedule(schedule, '1', '12:31:00')
        self.assertFalse(is_match)
        self.assertIsNone(scheduled_time)
        self.assertIsNone(time_difference)


class MockSchedule:
    def __init__(self, rides):
        self.rides = rides


class MockRide:
    def __init__(self, time, brigade):
        self.time = time
        self.brigade = brigade


if __name__ == '__main__':
    unittest.main()
