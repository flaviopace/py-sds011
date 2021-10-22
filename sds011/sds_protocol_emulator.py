"""This module provides an abstraction for the SDS011 air partuclate densiry sensor.
"""
import struct
import serial
import time
import random

#TODO: Commands against the sensor should read the reply and return success status.

class SDS011(object):
    """Provides method to read from a SDS011 air particlate density sensor
    using UART.
    """

    HEAD = b'\xaa'
    TAIL = b'\xab'
    CMD_ID = b'\xc0'

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

    ID_1 = b"\x01"
    ID_2 = b"\x01"

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

    def _execute(self, cmd_bytes):
        """Writes a byte sequence to the serial.
        """
        self.ser.write(cmd_bytes)

    def _get_reply(self):
        """Read reply from device."""
        raw = self.ser.read(size=10)
        data = raw[2:8]
        if len(data) == 0:
            return None
        if (sum(d for d in data) & 255) != raw[8]:
            return None  #TODO: also check cmd id
        return raw

    def cmd_begin(self):
        """Get command header and command ID bytes.
        @rtype: list
        """
        return self.HEAD + self.CMD_ID

    def send_data(self, read=False, active=False):
        """Get sleep command. Does not contain checksum and tail.
        @rtype: list
        """
        cmd = self.cmd_begin()
        cmd += (b"\x01" + b"\x01" + b"\x01" + b"\x01")
        cmd = self._finish_cmd(cmd)
        print("sending: {}".format(cmd))
        self._execute(cmd)

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
    sds011 = SDS011("/dev/ttys005", use_query_mode=True)
    # Turn-on sensor
    while (True):
        # Check if incoming bytes are waiting to be read from the serial input
        # buffer.
        # NB: for PySerial v3.0 or later, use property `in_waiting` instead of
        # function `inWaiting()` below!
        if (sds011.ser.inWaiting() > 0):
            # read the bytes and convert from binary array to ASCII
            data = sds011.ser.read(19)
            # print the incoming string without putting a new-line
            # ('\n') automatically after every print()
            print(data)
            sds011.send_data()
            # Put the rest of your code you want here

        # Optional, but recommended: sleep 10 ms (0.01 sec) once per loop to let
        # other threads on your PC run during this time.
        time.sleep(0.01)
