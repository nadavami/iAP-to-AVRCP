import serial
from logger import log
from ipod import IPod

def main():
    connection = serial.Serial('/dev/tty.SLAB_USBtoUART', 38400)
    ipod = IPod('Carputer', connection)
    log.info('Starting...')
    ipod.listen()

if __name__ == "__main__":
    main()
