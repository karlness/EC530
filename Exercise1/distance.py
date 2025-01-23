import math

def haversine_distance(lat1, lon1, lat2, lon2):
    
    R = 6371.0  # Earth's radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    # Apply the Haversine formula to calculate the square the half of the chord length
    # between two points on the sphere.
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    # Calculate the central angle and the distance
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))



def find_closest_points(array1, array2):
    
    return [
        (point1, min(array2, key=lambda point2: haversine_distance(*point1, *point2)))
        for point1 in array1
    ]




if __name__ == "__main__":
    # testing examples 
    
    array1 = [(52.5200, 13.4050), (48.8566, 2.3522)] # Munich and paris
    array2 = [(51.5074, -0.1278), (40.7128, -74.0060)]  # London and New York
    matches = find_closest_points(array1, array2)
    
    for point1, closest_point in matches:
        print(f"{point1} is closest to {closest_point}")



#Reference
#https://en.wikipedia.org/wiki/Haversine_formula