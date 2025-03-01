"""This module provides an abstraction for the SDS011 air partuclate densiry sensor.
"""
import struct
import serial
import aqi
import time
import json
import os
import sys
from db_connection import mydb
from thingspeak import Thingspeak
from aqiUpload import Aqicn
#TODO: Commands against the sensor should read the reply and return success status.

JSON_FILE = 'config.json'

class SDS011(object):
    """Provides method to read from a SDS011 air particlate density sensor
    using UART.
    """

    HEAD = b'\xaa'
    TAIL = b'\xab'
    CMD_ID = b'\xb4'

    # The sent command is a read or a write
    READ = b"\x00"
    WRITE = b"\x01"

    REPORT_MODE_CMD = b"\x02"
    ACTIVE = b"\x00"
    PASSIVE = b"\x01"

    QUERY_CMD = b"\x04"

    # The sleep command ID
    SLEEP_CMD = b"\x06"
    # Sleep and work byte
    SLEEP = b"\x00"
    WORK = b"\x01"

    # The work period command ID
    WORK_PERIOD_CMD = b'\x08'

    def __init__(self, serial_port, baudrate=9600, timeout=2,
                 use_query_mode=True):
        """Initialise and open serial port.
        """
        self.ser = serial.Serial(port=serial_port,
                                 baudrate=baudrate,
                                 timeout=timeout)
        self.ser.flush()
        self.set_report_mode(active=not use_query_mode)

    def _execute(self, cmd_bytes):
        """Writes a byte sequence to the serial.
        """
        self.ser.write(cmd_bytes)

    def _get_reply(self):
        """Read reply from device."""
        raw = self.ser.read(size=10)
        print("Received {}".format(raw))
        data = raw[2:8]
        if len(data) == 0:
            print("Empty answer!")
            return None
        checksum = sum(d for d in data) & 255
        if (checksum != raw[8]):
            print("CRC not good! received {} expected {}".format(checksum,raw[8]))
            return None  #TODO: also check cmd id
        return raw

    def cmd_begin(self):
        """Get command header and command ID bytes.
        @rtype: list
        """
        return self.HEAD + self.CMD_ID

    def set_report_mode(self, read=False, active=False):
        """Get sleep command. Does not contain checksum and tail.
        @rtype: list
        """
        cmd = self.cmd_begin()
        cmd += (self.REPORT_MODE_CMD
                + (self.READ if read else self.WRITE)
                + (self.ACTIVE if active else self.PASSIVE)
                + b"\x00" * 10)
        cmd = self._finish_cmd(cmd)
        self._execute(cmd)
        self._get_reply()

    def query(self):
        """Query the device and read the data.

        @return: Air particulate density in micrograms per cubic meter.
        @rtype: tuple(float, float) -> (PM2.5, PM10)
        """
        cmd = self.cmd_begin()
        cmd += (self.QUERY_CMD
                + b"\x00" * 12)
        cmd = self._finish_cmd(cmd)
        self._execute(cmd)

        raw = self._get_reply()
        if raw is None:
            return None  #TODO:
        data = struct.unpack('<HH', raw[2:6])
        pm25 = data[0] / 10.0
        pm10 = data[1] / 10.0
        return (pm25, pm10)

    def sleep(self, read=False, sleep=True):
        """Sleep/Wake up the sensor.

        @param sleep: Whether the device should sleep or work.
        @type sleep: bool
        """
        cmd = self.cmd_begin()
        cmd += (self.SLEEP_CMD
                + (self.READ if read else self.WRITE)
                + (self.SLEEP if sleep else self.WORK)
                + b"\x00" * 10)
        cmd = self._finish_cmd(cmd)
        self._execute(cmd)
        self._get_reply()

    def set_work_period(self, read=False, work_time=0):
        """Get work period command. Does not contain checksum and tail.
        @rtype: list
        """
        assert work_time >= 0 and work_time <= 30
        cmd = self.cmd_begin()
        cmd += (self.WORK_PERIOD_CMD
                + (self.READ if read else self.WRITE)
                + bytes([work_time])
                + b"\x00" * 10)
        cmd = self._finish_cmd(cmd)
        self._execute(cmd)
        self._get_reply()

    def _finish_cmd(self, cmd, id1=b"\xff", id2=b"\xff"):
        """Add device ID, checksum and tail bytes.
        @rtype: list
        """
        cmd += id1 + id2
        checksum = sum(d for d in cmd[2:]) % 256
        cmd += bytes([checksum]) + self.TAIL
        return cmd

    def _process_frame(self, data):
        """Process a SDS011 data frame.

        Byte positions:
            0 - Header
            1 - Command No.
            2,3 - PM2.5 low/high byte
            4,5 - PM10 low/high
            6,7 - ID bytes
            8 - Checksum - sum of bytes 2-7
            9 - Tail
        """
        raw = struct.unpack('<HHxxBBB', data[2:])
        checksum = sum(v for v in data[2:8]) % 256
        if checksum != data[8]:
            return None
        pm25 = raw[0] / 10.0
        pm10 = raw[1] / 10.0
        return (pm25, pm10)

    def read(self):
        """Read sensor data.

        @return: PM2.5 and PM10 concetration in micrograms per cude meter.
        @rtype: tuple(float, float) - first is PM2.5.
        """
        byte = 0
        while byte != self.HEAD:
            byte = self.ser.read(size=1)
            d = self.ser.read(size=10)
            if d[0:1] == b"\xc0":
                data = self._process_frame(byte + d)
                return data


if __name__ == "__main__":
    # Init sensor
    sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)
    # Turn-on sensor
    sensor.sleep(sleep=False)
    # Sleep 15 seconds
    time.sleep(15)
    # load Config
    with open(os.path.join(sys.path[0], JSON_FILE), 'r') as in_file:
        conf = json.load(in_file)
    # Init DB
    db = mydb(host=conf['db_config']['host'], name=conf['db_config']['name'], port=conf['db_config']['port'],\
              user=conf['db_config']['user'], password=conf['db_config']['password'])
    ts = Thingspeak(write_api_key=conf['ts_config']['wr_key'], channel_id=conf['ts_config']['ch_id'])
    myaqi = Aqicn(token=conf['aqi_config']['webtoken'])
    for iter in range(1):
        # Query Sensor
        pm2_5, pm10 = sensor.query()
        aqi_pm2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pm2_5))
        aqi_pm10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pm10))
        print("PM2_5: {} - AQI {}\nPM10: {} - AQI {}".format(pm2_5, aqi_pm2_5, pm10, aqi_pm10))
        val_str = '"{}", "{}", "{}", "{}", "{}"'.format(pm2_5, aqi_pm2_5, pm10, aqi_pm10, conf['db_config']['geohash'])
        print("values: {}".format(val_str))
        db.tableInsert(values=val_str)
        ts.post_cloud(value1=pm2_5, value2=pm10, value3=aqi_pm2_5, value4=aqi_pm10)
        myaqi.post_cloud(pm2_5=pm2_5, pm10=pm10)
        # Sleep 2 seconds before next measure
        time.sleep(2)

    # Turn-off sensor
    sensor.sleep(sleep=True)
    #db.showTableContent()
    db.close()