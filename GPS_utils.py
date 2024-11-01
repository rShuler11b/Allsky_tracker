import gps

def get_location():
    try:
        session = gps.gps()
        session.stream(gps.WATCH_ENABLE)
        report = session.next()

        if report['class'] == 'TPV':
            latitude = report.lat
            longitude = report.lon
            return latitude, longitude
    except Exception as e:
        print(f"Error getting GPS location: {e}")

    return None, None
