import can, queue, serial.tools.list_ports, threading
import serial # Sacar esta línea cuando se use USB-CAN

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

	def __init__(self, port, baudrate, bitrate=250000):
		# self.bus = can.interface.Bus(bustype='robotell', channel=port, ttyBaudrate=baudrate, bitrate=bitrate)
		self.bus = serial.Serial(port=port, baudrate=baudrate, timeout=1)
		self.connected = True
		self.initQueue()

		# Inicia thread para recibir datos por el puerto serial
		self.thread = threading.Thread(name='listen', target=self.readFromBus)
		self.thread.start()

	def initQueue(self):
		self.q = queue.Queue()

	def isConnected(self):
		return self.connected

	def closePort(self):
		self.connected = False
		self.thread.join()
		self.thread1.join()

	def getPorts(self):
		ports = []
		for x in serial.tools.list_ports.comports():
			ports.append(x.device)

		return ports

	def sendCmd(self, id, comando):
		self.bus.write(id)
		self.bus.write(comando)
		# msg = can.Message(arbitration_id=id, data=comando, is_extended_id=False)
		# self.bus.send(msg)

	def getQueueEmpty(self):
		return self.q.empty()

	def getQueue(self):
		return self.q.get()

	def readFromBus(self):
		while self.connected:
			self.q.put(self.bus.readline().decode()) # Esta es para serial, vuela con CAN-BUS
			# msg = self.bus.recv()
			# if msg is not None:
			# 	self.q.put(msg)


	def getPorts(self):
		ports = []
		for x in serial.tools.list_ports.comports():
		    ports.append(x.device)

		return ports
