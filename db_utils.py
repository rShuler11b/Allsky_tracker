import sqlite3

def init_db():
    conn = sqlite3.connect('satellite_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS satellites (
        id INTEGER PRIMARY KEY,
        name TEXT,
        time_passed TIMESTAMP,
        alt REAL,
        az REAL,
        location TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS meteors (
        id INTEGER PRIMARY KEY,
        time_detected TIMESTAMP,
        alt REAL,
        az REAL,
        location TEXT
    )''')
    conn.commit()
    conn.close()

def add_satellite_data_batch(data):
    conn = sqlite3.connect('satellite_data.db')
    cursor = conn.cursor()
    cursor.executemany('''INSERT INTO satellites (name, time_passed, alt, az, location) VALUES (?, ?, ?, ?, ?)''',
                       data)
    conn.commit()
    conn.close()

def add_meteor_data_batch(data):
    conn = sqlite3.connect('satellite_data.db')
    cursor = conn.cursor()
    cursor.executemany('''INSERT INTO meteors (time_detected, alt, az, location) VALUES (?, ?, ?, ?)''',
                       data)
    conn.commit()
    conn.close()

def count_meteors():
    conn = sqlite3.connect('satellite_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM meteors')
    total_count = cursor.fetchone()[0]
    conn.close()
    return total_count

def count_meteors_last_24():
    conn = sqlite3.connect('satellite_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM meteors WHERE time_detected > datetime("now", "-1 day")')
    last_24_count = cursor.fetchone()[0]
    conn.close()
    return last_24_count

def count_satellites():
    conn = sqlite3.connect('satellite_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM satellites')
    total_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM satellites WHERE time_passed > datetime("now", "-1 day")')
    last_24_hours_count = cursor.fetchone()[0]

    conn.close()
    return total_count, last_24_hours_count