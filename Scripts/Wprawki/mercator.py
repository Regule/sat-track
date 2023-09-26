import math

def mercator_projection(longitude, latitude):
    # Define the Mercator projection bounds
    max_longitude = 180.0
    min_longitude = -180.0
    max_latitude = 85.051129
    min_latitude = -85.051129

    # Clamp the longitude and latitude within the bounds
    longitude = max(min(longitude, max_longitude), min_longitude)
    latitude = max(min(latitude, max_latitude), min_latitude)

    # Convert latitude and longitude to radians
    lat_rad = math.radians(latitude)

    # Perform the Mercator projection
    x = (longitude + 180.0) / 360.0
    y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0

    return x, y

# Test the function
longitude = 0.0
latitude = 0.0
x, y = mercator_projection(longitude, latitude)
print(f"Longitude: {longitude}, Latitude: {latitude} -> X: {x}, Y: {y}")

longitude = 180.0
latitude = 85.051129
x, y = mercator_projection(longitude, latitude)
print(f"Longitude: {longitude}, Latitude: {latitude} -> X: {x}, Y: {y}")

longitude = -180.0
latitude = -85.051129
x, y = mercator_projection(longitude, latitude)
print(f"Longitude: {longitude}, Latitude: {latitude} -> X: {x}, Y: {y}")

