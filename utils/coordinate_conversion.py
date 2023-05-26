import math

def CHtoWGS84(easting, northing, height = None):
    # constants
    a = 6378137
    f = 1 / 298.257223563  # WGS84
    e2 = 2 * f - f**2
    e = math.sqrt(e2)
    R = a * (1 - e2) / ((1 - e2 * math.sin(math.radians(46.95240555555556))**2)**(3 / 2))  # mean Earth radius at given latitude
    R_lon = R / math.cos(math.radians(46.95240555555556))

    # transforming to ellipsoidal coordinates (lat, lon)
    x_norm = (easting - 2600000) / 1000000
    y_norm = (northing - 1200000) / 1000000

    lon = 2.6779094 + 4.728982 * x_norm + 0.791484 * x_norm * y_norm + 0.1306 * x_norm * y_norm**2 - 0.0436 * x_norm**3
    lat = 16.9023892 + 3.238272 * y_norm - 0.270978 * x_norm**2 - 0.002528 * y_norm**2 - 0.0447 * x_norm**2 * y_norm - 0.0140 * y_norm**3
    lon = lon * 100 / 36
    lat = lat * 100 / 36

    # convert to degrees
    lon_deg = math.degrees(lon)
    lat_deg = math.degrees(lat)

    

    return [lat_deg, lon_deg] if height is None else [lat_deg, lon_deg, height]
