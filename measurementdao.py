import sqlite3
import threading

connection_storage = "connection"

SENSOR_MAP = {
    '2801AF191B1301B2': 'Canopy',
    '28AA0B801313028F': 'Above Light',
    '28AAD480131302BE': 'Canopy W/ Shield',
}


def nearest_n(to_round_time, floor_increment):
    int_floor = int(floor_increment)
    try:
        nearest_five_minutes = int(int_floor * round(float(to_round_time[-5:-3]) / int_floor)) % 60
        time_with_nearest_5 = to_round_time[:-5] + str(nearest_five_minutes).zfill(2) + ":00"
        return time_with_nearest_5
    except Exception as e:
        print e
    return to_round_time


def get_sensor_name(address):
    if address in SENSOR_MAP:
        return SENSOR_MAP[address]
    else:
        return address


class Measurement(object):
    def __init__(self, sensor, temp, timestamp=None):
        self.sensor = sensor
        self.temp = temp
        self.timestamp = timestamp

    @staticmethod
    def from_string(string):
        s = str(string)
        (sensor, temp) = s.split("::")
        return Measurement(str(sensor), float(temp))

    def __str__(self):
        return "{ sensor: " + str(self.sensor) + ", temp: " + str(self.temp) + " }"


class MeasurementDao:

    def get_connection(self):
        local = threading.local()
        if not getattr(local, connection_storage, None):
            local.connection_storage = sqlite3.connect(self.db_name)
            local.connection_storage.create_function("nearest_n", 2, nearest_n)
        return local.connection_storage

    def __init__(self, db_name):
        self.db_name = db_name
        connection = self.get_connection()
        cursor = connection.cursor()
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
            temp REAL,
            sensor_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS timestamp_idx ON measurements (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS sensor_idx ON measurements (sensor_id)")
        connection.commit()

    def persist_measurement(self, measurement):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO measurements VALUES (?,?, datetime('now'))",
                       (measurement.temp, measurement.sensor))
        connection.commit()

    def get_measurements(self, window=1, limit=60):
        window_minutes = int(window)
        number_of_windows = int(limit)
        lists_of_measurements = map(
            lambda sensor_id: self.get_measurements_for_sensor_id(sensor_id, window_minutes, number_of_windows),
            SENSOR_MAP.keys())
        return [measurement for measurements in lists_of_measurements for measurement in measurements]

    def get_as_of(self):
        connection = self.get_connection()
        c = connection.cursor()
        c.execute("SELECT MAX(timestamp) FROM measurements")
        return c.fetchall()[0][0]

    def get_measurements_for_sensor_id(self, sensor_id, window_minutes, limit):
        max_min_ago = window_minutes * limit
        connection = self.get_connection()
        c = connection.cursor()
        c.arraysize = limit
        c.execute('''
            SELECT sensor_id, ROUND(AVG(temp),2), nearest_n(timestamp, ?) as timestamp2 FROM measurements 
            WHERE timestamp BETWEEN 
            datetime((SELECT MAX(timestamp) from measurements), '{} minutes') 
            AND datetime((SELECT MAX(timestamp) from measurements)) 
            AND sensor_id = ?
            GROUP BY sensor_id, timestamp2
        '''.format(max_min_ago * -1), [window_minutes, sensor_id])
        return map(lambda row: Measurement(get_sensor_name(row[0]), row[1], row[2]), c.fetchall())
