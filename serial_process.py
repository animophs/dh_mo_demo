import serial
import threading
import struct
import sys
import os
import time
import string
import logging
import queue

def checksum(data, state=0):
    for b in data:
        if type(b) is int:  # python 2/3 compat
            state += b
        else:
            state += ord(b)
        state = state & 0xff
    return state

def decode(port, running_flag, log_fn):
    partial_packet = None
    waiting_header = 0
    packet_len = 0
    len_counter = 0
    device_id = 0
    while True and running_flag is True:
        waiting = port.inWaiting()
        read_bytes = port.read(1 if waiting == 0 else waiting)
        if read_bytes == b'':
            # log_fn.error("Timeout packet")
            yield None
            # return

        for b in read_bytes:
            if type(b) is int:
                b = bytes([b])  # python 2/3 compat

            if waiting_header == 0:
                if b == b'\xaa':
                    partial_packet = b''
                    waiting_header = 1
                    partial_packet += b
                    len_counter += 1
            elif waiting_header == 1:
                device_id = b
                waiting_header = 2
                partial_packet += b
                len_counter += 1
            elif waiting_header == 2: # rec data
                partial_packet += b
                len_counter += 1
                if len_counter == 24:
                    waiting_header = 3
            elif waiting_header == 3:
                if checksum(partial_packet) == int(b[0]):
                    log_fn.info("True checksum")
                    yield partial_packet
                else:
                    log_fn.error("Wrong checksum")
                    time.sleep(10)
                partial_packet = None
                len_counter = 0
                packet_len = 0
                waiting_header = 0

class serial_process():
    sending_queue = queue.Queue(maxsize=32)
    # disconnected_signal = pyqtSignal()
    # connected_signal = pyqtSignal()
    # sensor_data_update = pyqtSignal(int, int, int, int, int, int, int, int, int, int, int)
    # rfid_data_update = pyqtSignal(str, str)
    # version_data_update = pyqtSignal(str, str)
    # control_status_data_update = pyqtSignal(int, int, int)
    # error_signal = pyqtSignal(str)
    # config_data_update = pyqtSignal(int, int, int, int, int, int, int, int, int, int, int)
    # calib_data_update = pyqtSignal(int, int, int)
    # change_tank_waitime = pyqtSignal(int)
    # fw_process = pyqtSignal(int)
    # fw_update_status = pyqtSignal(int)
    # debug_data_update = pyqtSignal(int, int, int)

    """Handle data from COM port"""
    def __init__(self, com_port='COM16', logger = None):
        super().__init__()
        self._port = com_port
        self._running = False
        self._serial = None
        if logger is None:
            self._logger=logging.getLogger()
        else:
            self._logger = logger
        self._work_mode = 0 # 0 normal 1 upload fw
        # self.start()

    def __del__(self):
        self.stop()

    def set_work_mode(self, mode):
        self._work_mode = mode

    def read(self):
        return next(self._protolcol_decode)

    def _getc(self, size, timeout=3):
        return self._serial.read(size)
    def _putc(self, data, timeout=3):
        self._serial.write(data)

    def _run(self):
        # create serial
        self._serial = serial.Serial(port = self._port,
                                baudrate=9600,
                                bytesize=serial.EIGHTBITS,
                                timeout=0.1,
                                stopbits=serial.STOPBITS_ONE,
                                parity=serial.PARITY_NONE)
        send_count = 0

        self._protolcol_decode = decode(self._serial, self._running, self._logger)
        while self._running:
            read_val = self.read()
            if read_val is not None :
                self.sending_queue.put(read_val)
                self._logger.debug(read_val)
            time.sleep(0.05)
        # while loop
        if self._serial.out_waiting > 0:
            self._logger.info("Flush out_waiting data")
            self._serial.flush()

        self._serial.close()
        self._serial = None
        self._logger.debug("Exit thread serial_process")

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target = self._run)
        self._thread.start()

    def stop(self):
        if not self._running:
            return
        self._logger.debug("Stop func is calling")
        self._running = False
        self._thread.join()

# Only for test
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        protocol_obj = serial_process(com_port='COM16')
        while True:
            pass

    except KeyboardInterrupt as e:
        protocol_obj.stop()
        print("Ok ok, quitting")
        sys.exit(1)

