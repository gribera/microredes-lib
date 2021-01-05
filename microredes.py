import connection as conn

class Microredes(object):
	masterAddr = 1

	functions = {'ERR': '0x01', 'DO': '0x04', 'SET': '0x08',
				 'QRY': '0x0c', 'ACK': '0x10', 'POST': '0x14',
				 'HB': '0x18'}

	variables = {'DIGITAL_OUT': '0x00', 'DIGITAL_IN': '0x01',
                    'ANALOG_OUT': '0x02', 'ANALOG_IN': '0x03',
                    'MODO_FUNC': '0x04', 'ANALOG': '0x05', 'IN-AMP': '0x06',
                    'AMP-INAMP': '0x07','PWM': '0x08', 'ECHO': '0x09',
                    'RTC1': '0x0A', 'PARADA': '0x0B', 'SOFT_RESET': '0x0C',
                    'U_A': '0x10', 'U_B': '0x11', 'U_C': '0x12',
                    'I_A': '0x13', 'I_B': '0x14', 'I_C': '0x15', 'I_N1': '0x16',
                    'PA_A': '0x17', 'PA_B': '0x18', 'PA_C': '0x19', 'PA_TOT': '0x1A',
                    'PR_A': '0x1B', 'PR_B': '0x1C', 'PR_C': '0x1D', 'PR_TOT': '0x1E',
                    'PS_A': '0x1F', 'PS_B': '0x20', 'PS_C': '0x21', 'PS_TOT': '0x22',
                    'FP_A': '0x23', 'FP_B': '0x24', 'FP_C': '0x25', 'FP_TOT': '0x26',
                    'THDU_A': '0x27', 'THDU_B': '0x28', 'THDU_C': '0x29',
                    'THDI_A': '0x2A', 'THDI_B': '0x2B', 'THDI_C': '0x2C',
                    'FREC': '0x2D', 'TEMP': '0x2E'}


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

	def genArray(self, msg):
		arr = [msg['function'], msg['origin'], msg['target'], msg['variable']] + msg['data']
		return arr

	def canSend(self, arr):
		arbitrationId = (arr[0] << 5) | arr[1]

		dataLow = arr[2:6][::-1]
		dataHigh = arr[6:10][::-1]
		envio = dataLow + dataHigh

		self.conn.sendCmd(arbitrationId, envio)

	def doDigitalOut(self, pin, mode):
		"""
			Enciende/Apaga salida digital indicada.

			pin: int, PIN [2-9]
			mode: boolean, True enciende, False apaga
		"""

		if pin < 2 or pin > 9:
			print('ERROR: Los pines digitales están comprendidos entre el 2-9')
			return

		msg = {
			'function': int(self.functions['DO'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['DIGITAL_OUT'], 0),
			'data': [pin, int(mode), 0, 0, 0, 0]
		}
		self.canSend(self.genArray(msg))
		# print(self.conn.sendCmd(msg)
