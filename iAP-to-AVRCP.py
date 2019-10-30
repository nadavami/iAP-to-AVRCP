#!/usr/bin/python3
import threading
import serial
from gi.repository import GLib
from bluetooth import Bluetooth
from ipod import IPod
from logger import log

# Car name shown via bluetooth
CAR_NAME = 'Carputer'
SERIAL_PORT = '/dev/ttyUSB0'


serial_connection = serial.Serial(SERIAL_PORT, 38400)
bluetooth = Bluetooth(CAR_NAME)

ipod = IPod(serial_connection, bluetooth)

bluetooth.start_discovery()
thread = threading.Thread(target=ipod.listen)

thread.start()
loop = GLib.MainLoop()
loop.run()
