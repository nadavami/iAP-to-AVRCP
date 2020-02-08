#!/usr/bin/python3
import threading
import serial
from gi.repository import GLib
from modules.bluetooth import Bluetooth
from modules.ipod import IPod
from modules.logger import log

# Car name shown via bluetooth
CAR_NAME = 'Carputer'
SERIAL_PORT = '/dev/ttyS1'

log.info('Starting iAP to AVRCP with name %s on serial port %s', CAR_NAME, SERIAL_PORT)

serial_connection = serial.Serial(SERIAL_PORT, 38400)
bluetooth = Bluetooth(CAR_NAME)

ipod = IPod(serial_connection, bluetooth)

bluetooth.start_discovery()
thread = threading.Thread(target=ipod.listen)

thread.start()
loop = GLib.MainLoop()
loop.run()
