import Queue

import measurementdao
import sensor_reader
import server
from serial.tools.list_ports import grep as grep_for_serial

queue = Queue.Queue(maxsize=1000)
# consuming_thread = threading.Thread(target=consume_from_queue)

# serial_device = grep_for_serial("usbmodem").next().device

# sensors = sensor_reader.TestSensorReader(queue=queue)
# sensors = sensor_reader.SensorReader(device=serial_device, queue=queue)
# sensors.start()
measurement_dao = measurementdao.MeasurementDao('example.db')

server = server.MeasurementServer(measurement_dao)
server.gogo()


def consume_from_queue():
    while True:
        measurement = queue.get()
        measurement_dao.persist_measurement(measurement)


consume_from_queue()
