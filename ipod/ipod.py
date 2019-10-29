'''iPod Module'''
from enum import Enum
from lingos import GeneralLingo, ExtendedInterfaceMode
from packet import Packet, PacketError

class Lingos(Enum):
    '''Assosiates iPod Accessory Protocol lingos with their IDs'''
    general_lingo = GeneralLingo.lingo_id
    extended_interface_mode = ExtendedInterfaceMode.lingo_id

class iPod: # pylint: disable=invalid-name,locally-disabled
    '''iPod that can be interacted with via UART'''
    def __init__(self, serial=None, bluetooth=None):
        self.general_lingo = GeneralLingo(serial=serial)
        self.extended_interface_mode = ExtendedInterfaceMode(serial=serial, bluetooth=bluetooth)

    def get_lingo_by_id(self, lingo_id):
        '''Retruns a lingo selected by it's ID'''
        return getattr(self, Lingos(lingo_id).name)

    def listen(self, serial):
        '''Listens to incomming requests and dispatches the command'''
        while True:
            try:
                packet = Packet.from_serial(serial)
                self.get_lingo_by_id(packet.lingo_id)(packet.command_id)(packet.payload)
            except PacketError:
                pass
