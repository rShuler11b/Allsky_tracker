from skyfield.api import load, Topos

def load_tle_data():
    print("Loading TLE data...")
    satellites = load.tle_file('http://celestrak.com/NORAD/elements/stations.txt')
    return {sat.name: sat for sat in satellites}

def identify_satellite(track_position, timestamp, location, satellite_by_name, ts):
    t = ts.utc(*timestamp.timetuple()[:6])
    camera_location = Topos(latitude_degrees=location[0], longitude_degrees=location[1])

    for name, satellite in satellite_by_name.items():
        difference = satellite - camera_location
        topocentric = difference.at(t)
        alt, az, _ = topocentric.altaz()

        if within_threshold(track_position, (alt.degrees, az.degrees)):
            return name, alt.degrees, az.degrees

    return "Unknown Satellite", None, None

def within_threshold(track_position, observed_position, altitude_threshold=10.0, azimuth_threshold=10.0):
    track_alt, track_az = track_position
    observed_alt, observed_az = observed_position
    alt_diff = abs(track_alt - observed_alt)
    az_diff = abs(track_az - observed_az)
    return alt_diff <= altitude_threshold and az_diff <= azimuth_threshold
