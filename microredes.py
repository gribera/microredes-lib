import connection as conn

class Microredes():
	conn = None

	def __init__(self, addr, equipo):
		self.addr = addr
		self.equipo = equipo

	def connect(port, baudrate):
		self.conn = conn.Connection(port, baudrate)
