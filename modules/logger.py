import logging
import sys

log = logging.getLogger()
log.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('/var/log/iap-to-avrcp.log')
serial_debug_handler = logging.FileHandler('/var/log/iap-to-avrcp.serial.log')

console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.INFO)
serial_debug_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

serial_formatter = logging.Formatter('%(asctime)s - %(message)s')
serial_debug_handler.setFormatter(serial_formatter)

log.addHandler(console_handler)
log.addHandler(file_handler)
log.addHandler(serial_debug_handler)
