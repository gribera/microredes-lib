import can
import serial.tools.list_ports
import time


def singleton(cls):
    instances = dict()

    def wrap(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)

        return instances[cls]

    return wrap


@singleton
class Connection(object):
    bus = None
    can_listener = None
    notifier = None
    connected = False
    buffer = list()
    timeout = 0.01

    def __init__(self):
        pass

    def connect(self, port, baudrate, bitrate):
        self.bus = can.interface.Bus(bustype='robotell',
                                     channel=port,
                                     ttyBaudrate=baudrate,
                                     bitrate=bitrate)
        self.connected = True
        self.init_can_listener()

    def is_connected(self):
        return self.connected

    def set_timeout(self, timeout):
        self.timeout = timeout

    def close_port(self):
        self.connected = False
        self.bus.close()

    def init_can_listener(self):
        self.can_listener = can.BufferedReader()
        self.notifier = can.Notifier(self.bus, [self.can_listener])

    def stop_can_listener(self):
        self.can_listener.stop()
        self.notifier.stop()

    def get_ports(self):
        ports = []
        for x in serial.tools.list_ports.comports():
            ports.append(x.device)

        return ports

    def send_cmd(self, id, query, interval=0):
        msg = can.Message(arbitration_id=id, data=query, is_extended_id=False)
        if interval > 0:
            return self.bus.send_periodic(msg, interval)
        else:
            return self.bus.send(msg)

    def read_from_bus(self, eq_id):
        timeout = time.time() + self.timeout
        while time.time() < timeout:
            msg = self.can_listener.get_message(self.timeout)

            if msg is None:
                break

            self.buffer.append(msg)

        filtered_buffer = self.buffer_filter(eq_id)

        return filtered_buffer

    def buffer_filter(self, eq_id):
        arr = []
        # Busca los mensajes en el buffer que corresponden al id del equipo
        for x in self.buffer:
            msg_id = x.arbitration_id & 0x1F
            if msg_id == eq_id:
                arr.append(x)

        # Borra los mensajes del buffer
        for x in arr:
            self.buffer.pop(self.buffer.index(x))

        return arr
