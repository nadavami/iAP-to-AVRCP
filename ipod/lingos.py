'''Implements the differnet iPod Accessory Protocol Lingos'''
import inspect
from enum import Enum
from engines import PlaybackEngine, DatabaseEngine
from packet import Packet, Utils as utils


class Lingo:
    '''Base class for a lingo and utility functions'''
    lingo_id = None
    def __init__(self, serial=None, bluetooth=None):
        self.commands = Enum()
        self.serial = serial
        self.bluetooth = bluetooth

    @property
    def current_function_name(self):
        '''Returns the name of the current function being called'''
        return inspect.currentframe().f_back.f_code.co_name

    def __call__(self, command):
        return getattr(self, self.commands(command).name)

    def ipod_ack(self, command_id, status):
        '''Acknowledges a command with a given status'''
        status_id = {
            'success': b'\x00',
            'unknown_database_category': b'\x01',
            'command_failed': b'\x02',
            'out_of_resources': b'\x03',
            'bad_parameter': b'\x04',
            'unknown_id': b'\x05',
            'command_pending': b'\x06',
            'directory_not_empty': b'\x0E',
            'opperation_timed_out': b'\x0F',
        }
        payload = status_id[status] + command_id
        Packet(self.lingo_id, command_id, payload).to_serial(self.serial)

    def reply(self, command_id, payload):
        '''Sends a reply to a command received'''
        return_command_id = sum(command_id, 1).to_bytes(len(command_id), byteorder="big")
        Packet(self.lingo_id, return_command_id, payload).to_serial(self.serial)


class GeneralLingoCommands(Enum):
    '''Assosiates General Lingo commands with their IDs'''
    enter_extended_interface_mode = b'\x05'

class GeneralLingo(Lingo):
    '''Deninition for the General iPod Lingo'''
    lingo_id = b'\x00'
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.ipod_ack_id = b'\x02'

    def enter_extended_interface_mode(self):
        '''Puts the iPod into extended interface mode'''
        command_id = GeneralLingoCommands[self.current_function_name].value
        self.ipod_ack(command_id, 'success')

class ExtendedInterfaceModeCommands(Enum):
    '''Assosiates ExtendedInterfaceMode commands with their IDs'''
    reset_db_selection = b'\x00\x16'
    select_db_record = b'\x00\x17'
    get_number_categorized_db_records = b'\x00\x18'
    retrieve_categorized_database_records = b'\x00\x1A'
    get_play_status = b'\x00\x1C'

class ExtendedInterfaceMode(Lingo):
    '''Deninition for the iPod Extended Interface Mode'''
    lingo_id = b'\x04'
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.ipod_ack_id = b'\x00\x01'
        self.commands = ExtendedInterfaceModeCommands
        self.playback_engine = PlaybackEngine(self.bluetooth)
        self.database_engine = DatabaseEngine(self.bluetooth)

    def reset_db_selection(self):
        '''Clears the currently selected DB items'''
        self.database_engine.reset()
        command_id = self.commands[self.current_function_name].value
        self.ipod_ack(command_id, 'success')

    def select_db_record(self, payload):
        '''Selects a DB item by category and index'''
        category_id, record_index = utils.unpack(payload, 'type', 'number')
        category_name = self.database_engine.categories(category_id).name
        self.database_engine.select(category_name, record_index)
        command_id = self.commands[self.current_function_name].value
        self.ipod_ack(command_id, 'success')

    def get_number_categorized_db_records(self, payload):
        '''Returns the number of items in a given category'''
        command_id = self.commands[self.current_function_name].value
        category_name = self.database_engine.categories(payload).name
        number_of_records = self.database_engine.get_number_of_records_for_category(category_name)
        self.reply(command_id, utils.number_to_bytes(number_of_records))

    def retrieve_categorized_database_records(self, payload):
        '''Returns the number of items in a given category'''
        command_id = self.commands[self.current_function_name].value
        category_id, start_index, read_count = utils.unpack(payload, 'type', 'number', 'number')
        category_name = self.database_engine.categories(category_id).name
        #TODO: Send Reply

    def get_play_status(self):
        '''Returns the number of items in a given category'''
        command_id = self.commands[self.current_function_name].value
        current_track = self.playback_engine.current_track
        payload_track_length = utils.number_to_bytes(current_track.duration_ms)
        payload_track_position = utils.number_to_bytes(current_track.position_ms)
        payload_player_state = self.playback_engine.states(current_track.status)
        self.reply(command_id, payload_track_length + payload_track_position + payload_player_state)
