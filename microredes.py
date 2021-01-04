import connection as conn

class Microredes(object):
	def __init__(self, addr, equipo):
		self.addr = addr
		self.equipo = equipo
		self.conn = conn.Connection()

	def __getattribute__(self, name):
		attr = object.__getattribute__(self, name)
		if hasattr(attr, '__call__'):
			def newfunc(*args, **kwargs):
				if not self.conn.isConnected() and attr.__name__ != 'connect':
					raise ConnectionError('No está conectado')

				result = attr(*args, **kwargs)
				return result
			return newfunc
		else:
			return attr

	def connect(self, port, baudrate):
		self.conn.connect(port, baudrate)

