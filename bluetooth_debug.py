from pydbus import SystemBus

BLUEZ_SERVICE = 'org.bluez'

bus = SystemBus()

root = bus.get(BLUEZ_SERVICE, '/')
hci = bus.get(BLUEZ_SERVICE, 'hci0')

adapter = hci[BLUEZ_SERVICE+'.Adapter1']
adapter.Alias = 'Carputer'
adapter.StartDiscovery()
adapter.Discoverable = True
adapter.DiscoverableTimeout = 90
adapter.Pairable = True
adapter.PairableTimeout = 90


def get_connected_device():
    object_manager = root['org.freedesktop.DBus.ObjectManager']
    objects = object_manager.GetManagedObjects()
    for item in objects:
        if BLUEZ_SERVICE+'.Device1' in objects[item]:
            if objects[item][BLUEZ_SERVICE+'.Device1']['Connected']:
                return item

connected_device_path = get_connected_device()
player = bus.get(BLUEZ_SERVICE, connected_device_path+'/player0')

media_player = player[BLUEZ_SERVICE+'.MediaPlayer1']
media_player.Play()
print(media_player.Track)
