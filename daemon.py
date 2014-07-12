from packet import Packet, DataPacket, ControlPacket
from serial import Serial
from event import X10Event

class Daemon:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.observers = []

    def subscribe(self, observer):
        """Subscribes an observer callback of the form f(X10Event)"""
        self.listeners.append(observer)

    def unsubscribe(self, observer):
        """Unsubscribes an observer from events"""
        self.observers.remove(observer)

    def report(self, event):
        for f in self.observers:
            f(event)

    def on(self, house, unit=None):
        """Sends an on command to the specified house and unit, or entire house if unit is None"""
        if unit:
            return self.raw(DataPacket(house, unit, DataPacket.COMMAND_ON))
        else:
            return self.raw(DataPacket(house, 0, DataPacket.COMMAND_ALL_UNITS_ON))

    def off(self, house, unit=None):
        """Sends an off command to the specified house and unit, or entire house if unit is None"""
        if unit:
            return self.raw(DataPacket(house, unit, DataPacket.COMMAND_OFF))
        else:
            return self.raw(DataPacket(house, 0, DataPacket.COMMAND_ALL_UNITS_OFF))

    def dim(self, house, unit, level):
        return self.raw(DataPacket(house, unit, DataPacket.COMMAND_DIM, repetitions=16-level))

    def raw(self, packet):
        """Sends a raw packet. Be careful!"""
        if self.dispatcher.dispatch(packet):
            event = X10Event(packet)
            self.report(event)
            return True
        return False

    def listen(self):
        """Blocks for events from the dispatcher, forever."""
        while True:
            self.report(self.dispatcher.next_event())

class SerialDispatcher:
    def __init__(self, serial):
        self.serial = serial

    def dispatch(self, packet):
        return self.serial.write(packet.encode()) == Packet.PACKET_LENGTH

    def has_event(self):
        return self.serial.inWaiting() >= Packet.PACKET_LENGTH

    def next_event(self):
        raw_bytes = self.serial.read(Packet.PACKET_LENGTH)
        packet = Packet.decode(raw_bytes)
        return packet and X10Event(packet)
