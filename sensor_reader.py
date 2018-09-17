import inspect
import random
import threading
import time

import serial

from measurementdao import Measurement


class BaseReader(object):
    def __init__(self, queue):
        self.queue = queue
        self.thread = None

    def __read(self):
        while True:
            measurement = Measurement.from_string(self.__read_data())
            self.queue.put(measurement)

    def start(self):
        t = threading.Thread(target=self.__read)
        t.setDaemon(True)
        t.start()
        self.thread = t

    def __read_data(self):
        return getattr(self, "_" + self.__class__.__name__ + (inspect.stack()[0][3]))()


class SensorReader(BaseReader):

    def __init__(self, device, queue):
        BaseReader.__init__(self, queue)
        self.ser = serial.Serial(device, 9600)

    def __read_data(self):
        return self.ser.readline()


class TestSensorReader(BaseReader):

    def __read_data(self):
        sensor = random.randint(0, 4)
        temp = random.randint(1, 99) / float(random.randint(1, 99))
        time.sleep(1)
        return str(sensor) + "::" + str(temp)
