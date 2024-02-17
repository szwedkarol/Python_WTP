# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# Test of the "avg_speed_analysis" module.

import unittest
from avg_speed_analysis import calculate_distance, calculate_avg_coords, calculate_time_diff


class TestAvgSpeedAnalysis(unittest.TestCase):

    def test_calculate_distance(self):
        # Test with known values
        distance = calculate_distance((52.2297, 21.0122), (52.4064, 16.9252))
        self.assertAlmostEqual(distance, 278349.458, places=3)

    def test_calculate_avg_coords(self):
        # Test with known values
        avg_coords = calculate_avg_coords((52.2297, 21.0122), (52.4064, 16.9252))
        self.assertEqual(avg_coords, (52.31805, 18.9687))

    def test_calculate_time_diff(self):
        # Test with known values
        time_diff = calculate_time_diff('12:30:00', '12:31:00')
        self.assertEqual(time_diff, 60)


if __name__ == '__main__':
    unittest.main()
