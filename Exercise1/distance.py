
import math
import csv
import re


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def dms_to_decimal(dms):
    """Convert DMS (degrees, minutes, seconds) to decimal degrees."""
    pattern = r"(\d+)[°]?\s*(\d+)?['′]?\s*(\d+)?[\"″]?"
    match = re.match(pattern, dms)
    if match:
        degrees = int(match.group(1))
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return degrees + minutes / 60 + seconds / 3600
    raise ValueError(f"Invalid DMS format: {dms}")


def parse_coordinate(coord):
    """Parse a coordinate in either decimal or DMS format."""
    try:
        if isinstance(coord, str) and ('°' in coord or '\'' in coord or '"' in coord):
            return dms_to_decimal(coord)
        return float(coord)
    except ValueError as e:
        raise ValueError(f"Invalid coordinate input: {coord}") from e


def find_closest_points(array1, array2):
    return [
        (point1, min(array2, key=lambda point2: haversine_distance(*point1, *point2)))
        for point1 in array1
    ]


def load_coordinates_from_csv(file_path):
    coordinates = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                lat = parse_coordinate(row[0])
                lon = parse_coordinate(row[1])
                coordinates.append((lat, lon))
            except ValueError as e:
                print(f"Skipping invalid row {row}: {e}")
    return coordinates


def main():
    print("Choose an option for inputting coordinates:")
    print("1. Enter coordinates manually")
    print("2. Load coordinates from CSV files")
    choice = input("Enter your choice (1/2): ")

    if choice == '1':
        array1 = []
        array2 = []

        print("Enter coordinates for the first array (format: lat, lon):")
        while True:
            coord = input("Enter coordinate (or 'done' to finish): ")
            if coord.lower() == 'done':
                break
            try:
                lat, lon = map(parse_coordinate, coord.split(','))
                array1.append((lat, lon))
            except ValueError as e:
                print(f"Invalid input: {e}")

        print("Enter coordinates for the second array (format: lat, lon):")
        while True:
            coord = input("Enter coordinate (or 'done' to finish): ")
            if coord.lower() == 'done':
                break
            try:
                lat, lon = map(parse_coordinate, coord.split(','))
                array2.append((lat, lon))
            except ValueError as e:
                print(f"Invalid input: {e}")

    elif choice == '2':
        file1 = input("Enter the path to the first CSV file: ")
        file2 = input("Enter the path to the second CSV file: ")

        try:
            array1 = load_coordinates_from_csv(file1)
            array2 = load_coordinates_from_csv(file2)
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return
        except ValueError as e:
            print(f"Error reading CSV: {e}")
            return

    else:
        print("Invalid choice!")
        return

    matches = find_closest_points(array1, array2)
    for point1, closest_point in matches:
        print(f"{point1} is closest to {closest_point}")


if __name__ == "__main__":
    main()




#Reference
#https://en.wikipedia.org/wiki/Haversine_formula