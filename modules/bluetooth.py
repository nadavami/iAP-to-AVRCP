from pydbus import SystemBus
from gi.repository import GLib
from modules.logger import log

BLUEZ_SERVICE = 'org.bluez'
INTERFACE = {
    'ADAPTER': BLUEZ_SERVICE+'.Adapter1',
    'DEVICE': BLUEZ_SERVICE+'.Device1',
    'MEDIA_CONTROL': BLUEZ_SERVICE+'.MediaControl1',
    'MEDIA_PLAYER': BLUEZ_SERVICE+'.MediaPlayer1'
}

class Bluetooth:
    def __init__(self, name):
        self.__bus = SystemBus()
        self.__adapter = self.__bus.get(BLUEZ_SERVICE, 'hci0')[INTERFACE['ADAPTER']]
        self.__set_alias(name)
        self.__player = None
        self.__change_callback = None

        self.__bus.subscribe(sender=BLUEZ_SERVICE, signal='PropertiesChanged', arg0=INTERFACE['ADAPTER'], signal_fired=self.__adapter_handler)
        self.__bus.subscribe(sender=BLUEZ_SERVICE, signal='PropertiesChanged', arg0=INTERFACE['MEDIA_CONTROL'], signal_fired=self.__mediacontrol_handler)
        self.__bus.subscribe(sender=BLUEZ_SERVICE, signal='PropertiesChanged', arg0=INTERFACE['MEDIA_PLAYER'], signal_fired=self.__mediaplayer_handler)

    def start_discovery(self):
        self.__powered()
        self.__pairable()
        self.__discoverable()
        return self.__adapter.StartDiscovery()

    def set_on_change(self, callback):
        self.__change_callback = callback

    @property
    def device_name(self):
        device_object = self.__bus.get(BLUEZ_SERVICE, self.__player[INTERFACE['MEDIA_PLAYER']].Device)
        device = device_object[INTERFACE['DEVICE']]
        return device.Alias

    @property
    def current_track(self):
        player = self.__player[INTERFACE['MEDIA_PLAYER']]
        return {
            'title': player.Track.get('Title', ''),
            'album': player.Track.get('Album', ''),
            'artist': player.Track.get('Artist', ''),
            'genre': player.Track.get('Genre', ''),
            'track_number': player.Track.get('TrackNumber', 0),
            'number_of_tracks': player.Track.get('NumberOfTracks', 0),
            'duration_ms': player.Track.get('Duration', 0),
            'position_ms': player.Position,
            'status': player.Status.lower()
        }


    def play(self):
        try:
            self.__player[INTERFACE['MEDIA_PLAYER']].Play()
        except GLib.Error:
            log.warning('Can\'t play track, player not ready.')

    def pause(self):
        try:
            self.__player[INTERFACE['MEDIA_PLAYER']].Pause()
        except GLib.Error:
            log.warning('Can\'t pause track, player not ready.')

    def next(self):
        try:
            self.__player[INTERFACE['MEDIA_PLAYER']].Next()
        except GLib.Error:
            log.warning('Can\'t go to next track, player not ready.')

    def previous(self):
        try:
            self.__player[INTERFACE['MEDIA_PLAYER']].Previous()
        except GLib.Error:
            log.warning('Can\'t go to previous track, player not ready.')

    def shuffle(self, setting):
        shuffle_settings = ['off', 'alltracks', 'group']
        if setting not in shuffle_settings:
            return
        try:
            self.__player[INTERFACE['MEDIA_PLAYER']].Shuffle = setting
        except GLib.Error:
            log.warning('Can\'t set shuffle mode to %s, player not ready.', setting)

    def repeat(self, setting):
        repeat_settings = ['off', 'singletrack', 'alltracks', 'group']
        if setting not in repeat_settings:
            return
        try:
            self.__player[INTERFACE['MEDIA_PLAYER']].Repeat = setting
        except GLib.Error:
            log.warning('Can\'t set repeat mode to %s, player not ready.', setting)

    def __get_managed_objects(self):
        object_manager = self.__bus.get(BLUEZ_SERVICE, '/')['org.freedesktop.DBus.ObjectManager']
        return object_manager.GetManagedObjects()

    def __set_alias(self, alias):
        self.__adapter.Alias = alias

    def __powered(self):
        self.__adapter.Powered = True

    def __discoverable(self, timeout=90):
        self.__adapter.Discoverable = True
        self.__adapter.DiscoverableTimeout = timeout

    def __pairable(self, timeout=90):
        self.__adapter.Pairable = True
        self.__adapter.PairableTimeout = timeout

    def __get_devices(self):
        objects = self.__get_managed_objects()
        devices_filter = lambda item: INTERFACE['DEVICE'] in item[1]
        return dict(filter(devices_filter, objects.items()))

    def __get_paired_media_devices(self):
        devices = self.__get_devices()
        paired_media_filter = lambda item: item[1][INTERFACE['DEVICE']]['Paired'] and INTERFACE['MEDIA_CONTROL'] in item[1]
        return dict(filter(paired_media_filter, devices.items()))

    def __connect_to_paired_media_device(self):
        devices = self.__get_paired_media_devices()
        device_path = list(devices.keys())[0]
        device_object = self.__bus.get(BLUEZ_SERVICE, device_path)
        device = device_object[INTERFACE['DEVICE']]
        if device.Connected:
            log.info('Connected to device %s.', device.Name)
            player_path = device_object[INTERFACE['MEDIA_CONTROL']].Player
            self.__init_player(player_path)
        else:
            try:
                device.Connect()
            except GLib.GError as err:
                log.warning('Can\'t connect to device %s.', device.Alias)

    def __init_player(self, player_path):
        self.__player = self.__bus.get(BLUEZ_SERVICE, player_path)

    def __adapter_handler(self, sender, path, interface, signal, parameters):
        interface, properties, optional = parameters
        if 'Discovering' in properties:
            log.info('Discovering active. Looking for devices.')
        try:
            self.__connect_to_paired_media_device()
        except:
            log.info('No paired devices found.')

    def __mediacontrol_handler(self, sender, path, interface, signal, parameters):
        interface, properties, optional = parameters
        if properties['Connected']:
            if 'Player' in properties:
                self.__init_player(properties['Player'])

    def __mediaplayer_handler(self, sender, path, interface, signal, parameters):
        self.__change_callback()
