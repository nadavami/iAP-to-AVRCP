'''Simmulates an iPod'''
import time
from payload import Payload, PayloadError
from consts import DEVICE_INFO, MODE, ACK, GENERAL, ADV_REMOTE
from logger import log

# pylint: disable=unused-argument, no-self-use, too-few-public-methods, line-too-long
class IPod:
    '''Simmulates an iPod'''
    def __init__(self, serial, bluetooth):
        self.__serial = serial
        self.__bluetooth = bluetooth
        self.__bluetooth.set_on_change(self.__status_notification)
        self.__notifications_enabled = False
        self.commands = {
            (MODE['GENERAL'], GENERAL['IDENTIFY']): self.__do_nothing,
            (MODE['GENERAL'], GENERAL['ENABLE_ADV_REMOTE']): self.__enable_adv_remote,
            (MODE['ADV_REMOTE'], ADV_REMOTE['GET_IPOD_TYPE']): self.__get_ipod_type,
            (MODE['ADV_REMOTE'], ADV_REMOTE['GET_IPOD_NAME']): self.__get_ipod_name,
            (MODE['ADV_REMOTE'], ADV_REMOTE['GET_SCREEN_SIZE']): self.__get_screen_size,
            (MODE['ADV_REMOTE'], ADV_REMOTE['SET_SHUFFLE']): self.__set_shuffle,
            (MODE['ADV_REMOTE'], ADV_REMOTE['SET_DISPLAY_IMAGE']): self.__set_display_image,
            (MODE['ADV_REMOTE'], ADV_REMOTE['SET_PLAYBACK']): self.__set_playback,
            (MODE['ADV_REMOTE'], ADV_REMOTE['SET_STATUS_NOTIFICATIONS']): self.__set_status_notifications,
            (MODE['ADV_REMOTE'], ADV_REMOTE['GET_TIME_AND_STATUS']): self.__get_time_and_status,
            (MODE['ADV_REMOTE'], ADV_REMOTE['RESET_PLAYLIST_SELECTION']): self.__reset_playlist_selection,
            (MODE['ADV_REMOTE'], ADV_REMOTE['PLAY_QUEUE_SELECTION']): self.__play_queue_selection,
            (MODE['ADV_REMOTE'], ADV_REMOTE['GET_INDEX_OF_PLAYING']): self.__get_index_of_playing,
            (MODE['ADV_REMOTE'], ADV_REMOTE['GET_NUMBER_OF_TRACKS_IN_QUEUE']): self.__get_number_of_tracks_in_queue,
            (MODE['ADV_REMOTE'], ADV_REMOTE['GET_TRACK_TITLE_OF_INDEX']): self.__get_track_title_of_index,
            (MODE['ADV_REMOTE'], ADV_REMOTE['GET_TRACK_ARTIST_OF_INDEX']): self.__get_track_artist_of_index,
            (MODE['ADV_REMOTE'], ADV_REMOTE['GET_TRACK_ALBUM_OF_INDEX']): self.__get_track_album_of_index,
            (MODE['ADV_REMOTE'], ADV_REMOTE['SET_PLAYLIST_TO_TYPE']): self.__set_playlist_to_type,
            (MODE['ADV_REMOTE'], ADV_REMOTE['SET_TRACK_IN_QUEUE_TO_INDEX']): self.__set_track_in_queue_to_index
        }

    def listen(self):
        '''Listens to incomming requests and responds'''
        while True:
            if self.__serial.in_waiting:
                try:
                    payload = Payload.from_serial(self.__serial)
                    self.__respond(payload)
                except PayloadError:
                    pass
            else:
                time.sleep(.2)

    def __respond(self, payload):
        try:
            response = self.__response(payload.command)
            self.commands[(payload.mode, payload.command)](payload, response)
        except KeyError:
            log.debug(
                'Unregistered command %s %s %s',
                Payload.format_bytes(payload.mode),
                Payload.format_bytes(payload.command),
                Payload.format_bytes(payload.parameter)
            )

    def __response(self, command):
        '''Generate response command for a given command'''
        return sum(command, 1).to_bytes(len(command), byteorder="big")

    def __ack(self, mode, command, success=True, timeout_ms=3000):
        if mode == MODE['GENERAL']:
            cmd = GENERAL['ACK']
        elif mode == MODE['ADV_REMOTE']:
            cmd = ADV_REMOTE['ACK']

        if timeout_ms > 0:
            pending_timeout = ACK['PENDING'] + command + Payload.number(timeout_ms)
            Payload(mode, cmd, pending_timeout).to_serial(self.__serial)

        if success:
            Payload(mode, cmd, ACK['SUCCESS']+command).to_serial(self.__serial)
        else:
            Payload(mode, cmd, ACK['COMMAND_FAILED']+command).to_serial(self.__serial)

    def __do_nothing(self, payload, response):
        '''Does nothing, used for commands with no response'''

    def __enable_adv_remote(self, payload, response):
        self.__ack(payload.mode, payload.command)

    def __get_ipod_type(self, payload, response):
        Payload(payload.mode, response, DEVICE_INFO['IPOD_TYPE']).to_serial(self.__serial)

    def __get_ipod_name(self, payload, response):
        name = self.__bluetooth.device_name
        Payload(payload.mode, response, Payload.string(name)).to_serial(self.__serial)

    def __get_screen_size(self, payload, response):
        Payload(payload.mode, response, DEVICE_INFO['SCREEN_SIZE']).to_serial(self.__serial)

    def __set_shuffle(self, payload, response):
        self.__ack(payload.mode, payload.command)
        if payload.parameter == ADV_REMOTE['SHUFFLE']['SONGS']:
            mode = 'alltracks'
        elif payload.parameter == ADV_REMOTE['SHUFFLE']['ALBUMS']:
            mode = 'group'
        else:
            mode = 'off'
        self.__bluetooth.shuffle(mode)

    def __set_repeat(self, payload, response):
        self.__ack(payload.mode, payload.command)
        if payload.parameter == ADV_REMOTE['REPEAT']['SONGS']:
            mode = 'alltracks'
        elif payload.parameter == ADV_REMOTE['REPEAT']['ALL_SONGS']:
            mode = 'group'
        elif payload.parameter == ADV_REMOTE['REPEAT']['DISABLE']:
            mode = 'off'
        self.__bluetooth.repeat(mode)

    def __set_display_image(self, payload, response):
        self.__ack(payload.mode, payload.command, success=True, timeout_ms=0)

    def __set_playback(self, payload, response):
        self.__ack(payload.mode, payload.command)
        if payload.parameter == ADV_REMOTE['PLAYBACK']['PLAY_PAUSE']:
            if self.__bluetooth.current_track['status'] == 'playing':
                self.__bluetooth.pause()
            elif self.__bluetooth.current_track['status'] == 'paused':
                self.__bluetooth.play()
        elif payload.parameter == ADV_REMOTE['PLAYBACK']['STOP']:
            self.__bluetooth.stop()
        elif payload.parameter == ADV_REMOTE['PLAYBACK']['NEXT']:
            self.__bluetooth.next()
        elif payload.parameter == ADV_REMOTE['PLAYBACK']['PREV']:
            self.__bluetooth.previous()

    def __set_status_notifications(self, payload, response):
        self.__ack(payload.mode, payload.command)
        if payload.parameter == ADV_REMOTE['STATUS_NOTIFICATIONS']['ENABLE']:
            self.__notifications_enabled = True
            log.info('Notifications enabled.')
        elif payload.parameter == ADV_REMOTE['STATUS_NOTIFICATIONS']['DISABLE']:
            self.__notifications_enabled = False
            log.debug('Notifications disabled.')

    def __status_notification(self):
        if self.__notifications_enabled:
            track_info = self.__bluetooth.current_track
            position_ms = Payload.number(track_info['position_ms'])
            response = self.__response(ADV_REMOTE['SET_STATUS_NOTIFICATIONS'])
            Payload(MODE['ADV_REMOTE'], response, position_ms).to_serial(self.__serial)

    def __get_time_and_status(self, payload, response):
        track_info = self.__bluetooth.current_track
        duration_ms = Payload.number(track_info['duration_ms'])
        position_ms = Payload.number(track_info['position_ms'])
        if track_info['status'] == 'paused':
            status = ADV_REMOTE['PLAYBACK_STATUS']['PAUSED']
        elif track_info['status'] == 'playing':
            status = ADV_REMOTE['PLAYBACK_STATUS']['PLAYING']
        else:
            status = ADV_REMOTE['PLAYBACK_STATUS']['STOPPED']
        Payload(payload.mode, response, duration_ms+position_ms+status).to_serial(self.__serial)

    def __reset_playlist_selection(self, payload, response):
        log.info('Playlist selection reset.')
        self.__ack(payload.mode, payload.command)

    def __play_queue_selection(self, payload, response):
        log.info('Playing queue selection. Index: %s', Payload.format_bytes(payload.parameter))
        self.__ack(payload.mode, payload.command, success=True, timeout_ms=0)

    def __get_index_of_playing(self, payload, response):
        track_index_in_queue = Payload.number(self.__bluetooth.current_track['track_number'])
        Payload(payload.mode, response, track_index_in_queue).to_serial(self.__serial)

    def __get_number_of_tracks_in_queue(self, payload, response):
        tracks_in_queue = Payload.number(self.__bluetooth.current_track['number_of_tracks'])
        Payload(payload.mode, response, tracks_in_queue).to_serial(self.__serial)

    def __get_track_title_of_index(self, payload, response):
        track_title = Payload.string(self.__bluetooth.current_track['title'])
        Payload(payload.mode, response, track_title).to_serial(self.__serial)

    def __get_track_artist_of_index(self, payload, response):
        track_artist = Payload.string(self.__bluetooth.current_track['artist'])
        Payload(payload.mode, response, track_artist).to_serial(self.__serial)

    def __get_track_album_of_index(self, payload, response):
        track_album = Payload.string(self.__bluetooth.current_track['artist'])
        Payload(payload.mode, response, track_album).to_serial(self.__serial)

    def __set_playlist_to_type(self, payload, response):
        playlist_type = bytes([payload.parameter[0]])
        playlist_index = payload.parameter[1:4]
        if playlist_type == ADV_REMOTE['PLAYLIST_TYPE']['PLAYLIST']:
            log.info('Set playlist to playlist at index %s', Payload.format_bytes(playlist_index))
        elif playlist_type == ADV_REMOTE['PLAYLIST_TYPE']['ARTIST']:
            log.info('Set playlist to artist at index %s', Payload.format_bytes(playlist_index))
        elif playlist_type == ADV_REMOTE['PLAYLIST_TYPE']['ALBUM']:
            log.info('Set playlist to album at index %s', Payload.format_bytes(playlist_index))
        elif playlist_type == ADV_REMOTE['PLAYLIST_TYPE']['GENRE']:
            log.info('Set playlist to genre at index %s', Payload.format_bytes(playlist_index))
        elif playlist_type == ADV_REMOTE['PLAYLIST_TYPE']['TRACK']:
            log.info('Set playlist to track at index %s', Payload.format_bytes(playlist_index))
        elif playlist_type == ADV_REMOTE['PLAYLIST_TYPE']['COMPOSER']:
            log.info('Set playlist to composer at index %s', Payload.format_bytes(playlist_index))

    def __set_track_in_queue_to_index(self, payload, response):
        self.__ack(payload.mode, payload.command)
        next_track_index = int.from_bytes(payload.parameter[0:4], 'big')
        track_info = self.__bluetooth.current_track
        if next_track_index > track_info['track_number']:
            self.__bluetooth.next()
        else:
            self.__bluetooth.previous()
        log.info('Set track to index %s', Payload.format_bytes(next_track_index))
