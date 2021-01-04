import can, queue, serial.tools.list_ports, threading
import serial # Sacar esta línea cuando se use USB-CAN
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
	thread = None
	connected = False
	timeout = 100

	def __init__(self):
		pass

	def connect(self, port, baudrate, bitrate=250000):
		# self.bus = can.interface.Bus(bustype='robotell', channel=port, ttyBaudrate=baudrate, bitrate=bitrate)
		self.bus = serial.Serial(port=port, baudrate=baudrate, timeout=1)
		self.connected = True

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

	def sendCmd(self, id, comando):
		# msg = can.Message(arbitration_id=id, data=comando, is_extended_id=False)
		# self.bus.send(msg)

		self.bus.write(comando.encode())
		return self.readFromBus()

	def readFromBus(self):
		# self.q.put(var) # Esta es para serial, vuela con CAN-BUS
		# msg = self.bus.recv()
		# if msg is not None:
		# 	self.q.put(msg)

		timeout = time.time() + self.timeout / 1000

		rsp = ""
		while True:
			msg = self.bus.readline().decode()
			if msg:
				rsp += msg

			# Salida por timeout
			if time.time() > timeout:
				break

		return rsp

	def getPorts(self):
		ports = []
		for x in serial.tools.list_ports.comports():
		    ports.append(x.device)

		return ports
