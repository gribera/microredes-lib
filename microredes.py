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

		return self.conn.sendCmd(arbitrationId, envio)

	def doDigitalOut(self, pin, mode):
		"""
			Enciende/Apaga salida digital indicada.

			pin: int, PIN [2-9].
			mode: boolean, True enciende, False apaga.
		"""

		if pin < 2 or pin > 9:
			print('ERROR: Los pines digitales están comprendidos entre el 2 y el 9')
			return

		msg = {
			'function': int(self.functions['DO'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['DIGITAL_OUT'], 0),
			'data': [pin, int(mode), 0, 0, 0, 0]
		}

		self.canSend(self.genArray(msg))

	def qryDigitalIn(self):
		"""
			Recupera estado de los pines digitales.
		"""
		msg = {
			'function': int(self.functions['QRY'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['DIGITAL_IN'], 0),
			'data': [0, 0, 0, 0, 0, 0]
		}
		return self.canSend(self.genArray(msg))

	def doAnalogOut(self, pin, steps):
		"""
			Setea salida del DAC.

			pin: int, PIN [0-1].
			steps: int, Valor a setear como salida del DAC [0-4095].
		"""
		if pin < 0 or pin > 1:
			print('ERROR: Los pines del DAC sólo pueden ser 0 o 1')
			return

		if steps < 0 or steps > 4095:
			print('ERROR: El valor no puede ser mayor a 4095')
			return

		msg = {
			'function': int(self.functions['DO'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['ANALOG_OUT'], 0),
			'data': [pin, 0, 0, 0, 0, 0] # TODO: Pasar a bytes los steps
		}

		self.canSend(self.genArray(msg))

	def qryDigitalOut(self, pin):
		"""
			Recupera valor del pin analógico pasado por parámetro.

			pin: int, Pin a consultar el valor.
		"""
		if pin < 0 or pin > 7:
			print('ERROR: Los pines analógicos están comprendidos entre el 0 y el 7')
			return

		msg = {
			'function': int(self.functions['QRY'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['DIGITAL_OUT'], 0),
			'data': [pin, 0, 0, 0, 0, 0]
		}
		return self.canSend(self.genArray(msg))

	def setModoFunc(self, mode):
		"""
			Setea el modo de funcionamiento de la placa.

			mode: int, Modo de trabajo de la placa.
		"""
		if pin < 0 or pin > 4:
			print('ERROR: Los modos disponibles están comprendidos entre el 0 y el 4')
			return

		msg = {
			'function': int(self.functions['SET'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['MODO_FUNC'], 0),
			'data': [mode, 0, 0, 0, 0, 0]
		}
		self.canSend(self.genArray(msg))

	def setAnalog(self, cantCan):
		"""
			Setea cantidad de canales analógicos.

			cantCan: int, Cantidad de canales analógicos a habilitar [1-8].
		"""
		if pin < 1 or pin > 8:
			print('ERROR: Los modos disponibles están comprendidos entre el 1 y el 8')
			return

		msg = {
			'function': int(self.functions['SET'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['ANALOG'], 0),
			'data': [cantCan, 0, 0, 0, 0, 0]
		}
		self.canSend(self.genArray(msg))

	def setInAmp(self, cantCan):
		"""
			Setea cantidad de canales in-Amp.

			cantCan: int, Cantidad de canales in-Amp a habilitar [1-4].
		"""
		if pin < 1 or pin > 4:
			print('ERROR: Los modos disponibles están comprendidos entre el 1 y el 4')
			return

		msg = {
			'function': int(self.functions['SET'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['IN-AMP'], 0),
			'data': [cantCan, 0, 0, 0, 0, 0]
		}
		self.canSend(self.genArray(msg))

	def setAmpInAmp(self, pin, amplification):
		"""
			Setea amplificación de canales in-Amp.

			pin: int, Canal in-Amp a amplificar [9-12].
			amplification: int, Amplificación [0-3].
		"""
		if pin < 9 or pin > 12:
			print('ERROR: Los canales in-Amp están comprendidos entre el 9 y el 12')
			return

		if amplification < 0 or amplification > 3:
			print('ERROR: La amplificación es un valor comprendido entre el 0 y el 3')
			return

		msg = {
			'function': int(self.functions['SET'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['AMP-INAMP'], 0),
			'data': [pin, amplification, 0, 0, 0, 0]
		}
		self.canSend(self.genArray(msg))

	def doPwm(self, pin, duty):
		"""
			Habilita salida PWM.

			pin: int, Canal in-Amp a amplificar [10-13].
			duty: int, Duty-Cycle [0-255].
		"""
		if pin < 10 or pin > 13:
			print('ERROR: Los pines PWM deben estar comprendidos entre el 10 y el 13')
			return

		if duty < 0 or duty > 255:
			print('ERROR: El duty cycle debe ser un valor entre 0 y 255')
			return

		msg = {
			'function': int(self.functions['DO'], 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(self.variables['PWM'], 0),
			'data': [pin, duty, 0, 0, 0, 0]
		}
		self.canSend(self.genArray(msg))


