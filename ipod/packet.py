'''Handles construction of payloads'''
import struct
from functools import reduce
from logger import log

PACKET_START = b'\xFF\x55'





class Utils:
    '''Utilities for parsing packets'''
    @staticmethod
    def hex_string(bytes_to_print):
        '''Returns the hex bytes in seperated by spaces'''
        if isinstance(bytes_to_print, int):
            bytes_to_print = bytes([bytes_to_print])
        return ' '.join(['{:02x}'.format(x) for x in bytes_to_print])

    @staticmethod
    def bytes_to_number(num):
        '''Converts byte number to an integer'''
        return int.from_bytes(num, byteorder='big')

    @staticmethod
    def number_to_bytes(num):
        '''Converts an integer into a 4-byte number'''
        return (num).to_bytes(4, byteorder='big')

    @staticmethod
    def string_to_bytes(string):
        '''Converts a string into a null terminated string of bytes'''
        return string.encode('UTF-8') + b'\x00'

    @staticmethod
    def unpack(payload, *args):
        '''Parse a payload based on a given structure'''
        format_string = reduce(Utils.__parser_format_string, args)
        return struct.unpack('>'+format_string, payload)

    @staticmethod
    def __parser_format_string(string, arg):
        if arg == 'number':
            string += 'I'
        elif arg == 'type':
            string += 'c'
        return string

class Packet:
    '''Handles construction of payloads'''
    def __init__(self, lingo_id, command_id, payload):
        self.lingo_id = lingo_id
        self.command_id = command_id
        self.payload = payload

    @staticmethod
    def from_serial(serial):
        '''Creates a payload from the serial port'''
        header = serial.read(2)
        if header != PACKET_START:
            log.warning('Invalid payload, bad header: %s', header)
            raise PacketError('Invalid payload, bad header.')

        length = int.from_bytes(serial.read(1), byteorder='big')

        if length == 0:
            length = int.from_bytes(serial.read(2), byteorder='big')

        body = serial.read(length)
        checksum = serial.read(1)
        log.info('Received: %s %s %s %s %s %s',
                 Utils.hex_string(header),
                 Utils.hex_string(length),
                 Utils.hex_string(body[0]),
                 Utils.hex_string(body[1:3]),
                 Utils.hex_string(body[3:]),
                 Utils.hex_string(checksum))

        payload = Packet(bytes([body[0]]), body[1:3], body[3:])

        if checksum != payload.checksum:
            log.error('Invalid payload, bad checksum: %s', header)
            raise PacketError('Invalid payload, bad checksum.')
        return payload

    def to_serial(self, serial):
        '''Writes a payload to the serial port'''
        payload_bytes = self.__encode()
        log.info('Sent: %s', Utils.hex_string(payload_bytes))
        serial.write(payload_bytes)
        return self

    @property
    def checksum(self):
        '''Calculates the checksum field'''
        sum_of_payload = sum(self.length + self.lingo_id + self.command_id + self.payload)
        checksum = 0x100 - (sum_of_payload & 0xFF)
        return bytes([checksum])

    @property
    def length(self):
        '''Calculates the length field'''
        length = len(self.lingo_id) + len(self.command_id) + len(self.payload)
        if length > 252:
            return (length).to_bytes(3, byteorder='big')
        return bytes([length])

    def __encode(self):
        '''Assembles the payload so it can be transmitted'''
        payload = PACKET_START
        payload += self.length
        payload += self.lingo_id
        payload += self.command_id
        payload += self.payload
        payload += self.checksum
        return payload

class PacketError(Exception):
    '''Exception raised for errors in the payload.'''
