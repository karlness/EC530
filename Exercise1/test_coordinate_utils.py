import unittest
from io import StringIO
import csv
from unittest.mock import mock_open, patch
from your_script_name import (
    haversine_distance,
    dms_to_decimal,
    parse_coordinate,
    find_closest_points,
    load_coordinates_from_csv
)


class TestCoordinateFunctions(unittest.TestCase):
    
    def test_haversine_distance(self):
        # Test known distance (Paris to London ~343km)
        lat1, lon1 = 48.8566, 2.3522  # Paris
        lat2, lon2 = 51.5074, -0.1278  # London
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        self.assertAlmostEqual(distance, 343, delta=5)

    def test_dms_to_decimal(self):
        self.assertAlmostEqual(dms_to_decimal("45°30'30"""), 45.5083, places=4)
        self.assertAlmostEqual(dms_to_decimal("120°15'0"""), 120.25, places=4)
        self.assertAlmostEqual(dms_to_decimal("0°0'0"""), 0.0, places=4)
        with self.assertRaises(ValueError):
            dms_to_decimal("invalid format")

    def test_parse_coordinate(self):
        self.assertEqual(parse_coordinate("45.6789"), 45.6789)
        self.assertEqual(parse_coordinate("45°30'30"""), 45.5083)
        with self.assertRaises(ValueError):
            parse_coordinate("invalid")
    
    def test_find_closest_points(self):
        array1 = [(40.7128, -74.0060)]  # New York
        array2 = [(34.0522, -118.2437), (41.8781, -87.6298)]  # LA and Chicago
        result = find_closest_points(array1, array2)
        self.assertEqual(result[0][1], (41.8781, -87.6298))  # Closest to Chicago

    @patch("builtins.open", new_callable=mock_open, read_data="40.7128,-74.0060\n34.0522,-118.2437\n")
    def test_load_coordinates_from_csv(self, mock_file):
        result = load_coordinates_from_csv("fake_path.csv")
        self.assertEqual(result, [(40.7128, -74.0060), (34.0522, -118.2437)])
    
    @patch("builtins.open", new_callable=mock_open, read_data="invalid,data\n")
    def test_load_coordinates_from_csv_invalid(self, mock_file):
        result = load_coordinates_from_csv("fake_path.csv")
        self.assertEqual(result, [])  # Should skip invalid row


if __name__ == "__main__":
    unittest.main()