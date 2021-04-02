'''Handles construction of payloads'''
from modules.consts import HEADER
from modules.logger import log

class Payload:
    '''Handles construction of payloads'''
    def __init__(self, mode, command, parameter=b''):
        self.mode = mode
        self.command = command
        self.parameter = parameter
        self.is_long = False

    @staticmethod
    def number(num):
        '''Converts an integer into a 4-byte number'''
        return (num).to_bytes(4, byteorder='big')

    @staticmethod
    def range(start, end):
        '''Converts two integers into two number(4)s'''
        return Payload.number(start) + Payload.number(end)

    @staticmethod
    def string(string):
        '''Converts a string into a null terminated string of bytes'''
        return string.encode('UTF-8') + b'\x00'

    @staticmethod
    def format_bytes(bytes_to_print):
        '''Returns the hex bytes in seperated by spaces'''
        if isinstance(bytes_to_print, int):
            return hex(bytes_to_print)
        return ' '.join(['{:02x}'.format(x) for x in bytes_to_print])

    @staticmethod
    def from_serial(serial):
        '''Creates a payload from the serial port'''
        header = serial.read(2)
        if header != HEADER:
            raise PayloadError('Invalid payload, bad header.')

        length = int.from_bytes(serial.read(1), byteorder='big')

        if length == 0:
            length = int.from_bytes(serial.read(2), byteorder='big')

        body = serial.read(length)
        checksum = serial.read(1)
        if body[0] == 0x04:
            payload = Payload(bytes([body[0]]), body[1:3], body[3:])
        else:
            payload = Payload(bytes([body[0]]), body[1:2], body[2:])
        log.debug('[RECEIVED] - %s %s', Payload.format_bytes(body), Payload.format_bytes(checksum))

        # pylint: disable=W0212
        if checksum != payload.__checksum():
            raise PayloadError('Invalid payload, bad checksum.')
        return payload

    def to_serial(self, serial):
        '''Writes a payload to the serial port'''
        if not self.is_long:
            payload_bytes = self.__encode()
            log.debug('[SENT] - %s', self.format_bytes(payload_bytes))
            serial.write(payload_bytes)
        else:
            log.debug('[DROPPED LONG PAYLOAD]')
        return self

    def __length(self):
        '''Calculates the length field'''
        length = len(self.mode) + len(self.command) + len(self.parameter)
        if length > 252:
            self.is_long = True
            return (length).to_bytes(3, byteorder='big')
        return bytes([length])

    def __checksum(self):
        '''Calculates the checksum field'''
        sum_of_payload = sum(self.__length() + self.mode + self.command + self.parameter)
        checksum = 0x100 - (sum_of_payload & 0xFF)
        return bytes([checksum])

    def __encode(self):
        '''Assembles the payload so it can be transmitted'''
        payload = HEADER
        payload += self.__length()
        payload += self.mode
        payload += self.command
        payload += self.parameter
        payload += self.__checksum()
        return payload

class PayloadError(Exception):
    '''Exception raised for errors in the payload.'''
