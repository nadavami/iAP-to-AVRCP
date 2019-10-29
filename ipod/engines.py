'''Module for iPod Playback and Database Engines'''
from enum import Enum

class PlayerState(Enum):
    stopped = b'\x00'
    playing = b'\x01'
    paused = b'\x02'
    error = b'\xFF'

class PlaybackEngine():
    '''Class that handles playback'''
    def __init__(self, bluetooth):
        self.bluetooth = bluetooth
        self.states = PlayerState

    @property
    def now_playing(self):
        '''Returns the now playing playlist'''
        return []

    @property
    def current_track(self):
        '''Returns the current playing track info'''
        return self.bluetooth.current_track

class DatabaseCategories(Enum):
    top_level = b'\x00'
    playlist = b'\x01'
    album = b'\x02'
    artist = b'\x03'
    genre = b'\x04'
    track = b'\x05'
    compooser = b'\x06'

class DatabaseEngine():
    '''Class for tracks to be selected without affecting playback'''
    def __init__(self, bluetooth):
        self.bluetooth = bluetooth
        self.selection = []
        self.categories = DatabaseCategories

    def reset(self):
        '''Reset the database selection to empty'''
        self.selection = []

    def select(self, category_name, record_index):
        pass

    def get_number_of_records_for_category(self, category_name):
        '''Returns the number of items in a category'''
        return self.bluetooth

