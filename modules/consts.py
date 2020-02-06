"""
Constants used in the serial Apple Accessory Protocol (AAP)
"""

HEADER = b'\xff\x55'
DEVICE_INFO = {
    'IPOD_TYPE': b'\x01\x09',
    'SCREEN_SIZE': b'\x01\x36\x00\xa8\x01'
}
MODE = {
    'GENERAL': b'\x00',
    'ADV_REMOTE': b'\x04'
}
ACK = {
    'SUCCESS': b'\x00',
    'UNKNOWN_CATEGORY': b'\x01',
    'COMMAND_FAILED': b'\x02',
    'OUT_OF_RESOURCES': b'\x03',
    'BAD_PARAMETER': b'\x04',
    'UNKNOWN_ID': b'\x05',
    'PENDING': b'\x06',
}

GENERAL = {
    'ACK': b'\x02',
    'IDENTIFY': b'\x01\x04',
    'ENABLE_ADV_REMOTE': b'\x05'
}
ADV_REMOTE = {
    'PLAYLIST_TYPE': {
        'PLAYLIST': b'\x01',
        'ARTIST': b'\x02',
        'ALBUM': b'\x03',
        'GENRE': b'\x04',
        'TRACK': b'\x05',
        'COMPOSER': b'\x06'
    },
    'STATUS_NOTIFICATIONS': {
        'ENABLE': b'\x01',
        'DISABLE': b'\x00'
    },
    'SHUFFLE': {
        'SONGS': b'\x01',
        'ALBUMS': b'\x02',
        'DISABLE': b'\x00'
    },
    'REPEAT': {
        'SONG': b'\x01',
        'ALL_SONGS': b'\x02',
        'DISABLE': b'\x00',
    },
    'PLAYBACK': {
        'PLAY_PAUSE': b'\x01',
        'STOP': b'\x02',
        'NEXT': b'\x03',
        'PREV': b'\x04',
        'FAST_FORWARD': b'\x05',
        'FAST_REWIND': b'\x06',
        'STOP_FAST_X': b'\x07',
    },
    'PLAYBACK_STATUS': {
        'STOPPED': b'\x00',
        'PLAYING': b'\x01',
        'PAUSED': b'\x02',
        'ERROR': b'\xFF',
    },
    'ACK': b'\x00\x01',
    'GET_IPOD_TYPE': b'\x00\x12',
    'GET_IPOD_NAME': b'\x00\x14',
    'SET_DISPLAY_IMAGE': b'\x00\x32',
    'RESET_PLAYLIST_SELECTION': b'\x00\x16',
    'SET_PLAYLIST_TO_TYPE': b'\x00\x17',
    'GET_TYPE_COUNT': b'\x00\x18',
    'GET_NAMES_FOR_RANGE': b'\x00\x1A',
    'GET_TIME_AND_STATUS': b'\x00\x1C',
    'GET_TRACK_TITLE_OF_INDEX': b'\x00\x20',
    'GET_TRACK_ARTIST_OF_INDEX': b'\x00\x22',
    'GET_TRACK_ALBUM_OF_INDEX': b'\x00\x24',
    'SET_STATUS_NOTIFICATIONS': b'\x00\x26',
    'SET_PLAYBACK': b'\x00\x29',
    'GET_SHUFFLE': b'\x00\x2C',
    'SET_SHUFFLE': b'\x00\x2E',
    'GET_REPEAT': b'\x00\x2F',
    'SET_REPEAT': b'\x00\x31',
    'GET_SCREEN_SIZE': b'\x00\x33',
    'PLAY_QUEUE_SELECTION': b'\x00\x28',
    'GET_INDEX_OF_PLAYING': b'\x00\x1E',
    'GET_NUMBER_OF_TRACKS_IN_QUEUE': b'\x00\x35',
    'SET_TRACK_IN_QUEUE_TO_INDEX': b'\x00\x37',
}
