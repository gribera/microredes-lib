import can, queue, serial.tools.list_ports, threading, time

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
	thread = None
	connected = False
	timeout = 0.01

	def __init__(self):
		pass

	def connect(self, port, baudrate, bitrate=250000):
		self.bus = can.interface.Bus(bustype='robotell', channel=port, ttyBaudrate=baudrate, bitrate=bitrate)
		self.connected = True
		self.canListener = can.BufferedReader()
		self.notifier = can.Notifier(self.bus, [self.canListener])

	def isConnected(self):
		return self.connected

	def setTimeout(self, timeout):
		self.timeout = timeout

	def closePort(self):
		self.connected = False
		self.bus.close()

	def getPorts(self):
		ports = []
		for x in serial.tools.list_ports.comports():
			ports.append(x.device)

		return ports

	def sendCmd(self, id, query):
		msg = can.Message(arbitration_id=id, data=query, is_extended_id=False)
		self.bus.send(msg)

	def sendPeriodic(self, id, query, interval):
		msg = can.Message(arbitration_id=id, data=query, is_extended_id=False)
		self.bus.send_periodic(msg, interval)

	def readFromBus(self):
		arrData = []
		timeout = time.time() + self.timeout
		while time.time() < timeout:
		    m = self.canListener.get_message(self.timeout)

		    if m is None:
		    	break

		    arrData.append(m.data)

		return arrData

	def getPorts(self):
		ports = []
		for x in serial.tools.list_ports.comports():
		    ports.append(x.device)

		return ports