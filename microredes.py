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
                    'RTC': '0x0A', 'PARADA': '0x0B', 'SOFT_RESET': '0x0C',
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

	def genMsg(self, function, variable, data = [0, 0, 0, 0, 0, 0]):
		return {
			'function': int(function, 0),
			'origin': self.masterAddr,
			'target': self.addr,
			'variable': int(variable, 0),
			'data': data
		}

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

		dataArray = [pin, int(mode), 0, 0, 0, 0]
		msg = self.genMsg(self.functions['DO'], self.variables['DIGITAL_OUT'], dataArray)

		self.canSend(self.genArray(msg))

	def qryDigitalIn(self):
		"""
			Recupera estado de los pines digitales.
		"""
		msg = self.genMsg(self.functions['QRY'], self.variables['DIGITAL_IN'])

		return self.canSend(self.genArray(msg))

	def qryAnalogIn(self, pin):
		"""
			Recupera valor del pin analógico pasado por parámetro.

			pin: int, PIN [0-7].
		"""
		dataArray = [pin, 0, 0, 0, 0, 0]
		msg = self.genMsg(self.functions['QRY'], self.variables['ANALOG_IN'], dataArray)

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

		dataArray = [pin, 0, 0, 0, 0, 0] # TODO: Pasar a bytes los steps
		msg = self.genMsg(self.functions['DO'], self.variables['ANALOG_OUT'], dataArray)

		self.canSend(self.genArray(msg))

	def setModoFunc(self, mode):
		"""
			Setea el modo de funcionamiento de la placa.

			mode: int, Modo de trabajo de la placa [0-4].
		"""
		if pin < 0 or pin > 4:
			print('ERROR: Los modos disponibles están comprendidos entre el 0 y el 4')
			return

		dataArray = [mode, 0, 0, 0, 0, 0]
		msg = self.genMsg(self.functions['SET'], self.variables['MODO_FUNC'], dataArray)

		self.canSend(self.genArray(msg))

	def setAnalog(self, cantCan):
		"""
			Setea cantidad de canales analógicos.

			cantCan: int, Cantidad de canales analógicos a habilitar [1-8].
		"""
		if pin < 1 or pin > 8:
			print('ERROR: Los modos disponibles están comprendidos entre el 1 y el 8')
			return

		dataArray = [cantCan, 0, 0, 0, 0, 0]
		msg = self.genMsg(self.functions['SET'], self.variables['ANALOG'], dataArray)

		self.canSend(self.genArray(msg))

	def setInAmp(self, cantCan):
		"""
			Setea cantidad de canales in-Amp.

			cantCan: int, Cantidad de canales in-Amp a habilitar [1-4].
		"""
		if pin < 1 or pin > 4:
			print('ERROR: Los modos disponibles están comprendidos entre el 1 y el 4')
			return

		dataArray = [cantCan, 0, 0, 0, 0, 0]
		msg = self.genMsg(self.functions['SET'], self.variables['IN-AMP'], dataArray)

		self.canSend(self.genArray(msg))

	def setAmpInAmp(self, pin, amp):
		"""
			Setea amplificación de canales in-Amp.

			pin: int, Canal in-Amp a amplificar [9-12].
			amp: int, Amplificación [0-3].
		"""
		if pin < 9 or pin > 12:
			print('ERROR: Los canales in-Amp están comprendidos entre el 9 y el 12')
			return

		if amp < 0 or amp > 3:
			print('ERROR: La amplificación es un valor comprendido entre el 0 y el 3')
			return

		dataArray = [pin, amp, 0, 0, 0, 0]
		msg = self.genMsg(self.functions['SET'], self.variables['AMP-INAMP'], dataArray)

		self.canSend(self.genArray(msg))

	def doPwm(self, pin, duty):
		"""
			Habilita salida PWM.

			pin: int, Pin de salida [10-13].
			duty: int, Duty-Cycle [0-255].
		"""
		if pin < 10 or pin > 13:
			print('ERROR: Los pines PWM deben estar comprendidos entre el 10 y el 13')
			return

		if duty < 0 or duty > 255:
			print('ERROR: El duty cycle debe ser un valor entre 0 y 255')
			return

		dataArray = [pin, duty, 0, 0, 0, 0]
		msg = self.genMsg(self.functions['DO'], self.variables['PWM'], dataArray)

		self.canSend(self.genArray(msg))

	def hbEcho(self, char):
		"""
			Devuelve el mismo valor pasado por parámetro. Sirve a modo de heartbeat.

			char: int, Valor [0-127].
		"""
		if char < 0 or char > 255:
			print('ERROR: El valor de estar comprendido entre 0 y 127')
			return

		dataArray = [char, 0, 0, 0, 0, 0]
		msg = self.genMsg(self.functions['HB'], self.variables['ECHO'], dataArray)

		return(self.canSend(self.genArray(msg)))

	def setRTC(self, date, hour): # TODO: Terminar esta función
		"""
			Setea la fecha y hora en el RTC del equipo.

			date: string, Fecha en formato dd/mm/aa.
			hour: string, Hora en formato hh:mm:ss.
		"""
		parsedDate = date.split('/')
		parsedHour = hour.split(':')
		dd, mm, aa = parsedDate
		hh, MM, ss = parsedHour

		if ((len(parsedDate) != 3) or
			(int(dd) > 31 or int(dd) < 1) or
			(int(mm) > 12 or int(mm) < 1)):
			print('ERROR: Formato de fecha incorrecto')
			return

		if ((len(parsedHour) != 3) or
			(int(hh) > 24 or int(hh) < 1) or
			(int(MM) > 60 or int(MM) < 0) or
			(int(ss) > 60 or int(ss) < 0)):
			print('ERROR: Formato de hora incorrecto')
			return

		# Hora
		dataArray = [int(hh[0]), int(hh[1]), int(MM[0]), int(MM[1]), int(ss[0]), int(ss[1])]
		msg = self.genMsg(self.functions['SET'], self.variables['RTC'], dataArray)

		# Fecha
		self.canSend(self.genArray(msg))
		dataArray = [int(dd[0]), int(dd[1]), int(mm[0]), int(mm[1]), int(aa[0]), int(aa[1])]
		msg = self.genMsg(self.functions['SET'], self.variables['RTC'], dataArray)

		self.canSend(self.genArray(msg))

	def qryRTC(self):
		"""
			Recupera fecha y hora del RTC del equipo.
		"""
		msg = self.genMsg(self.functions['QRY'], self.variables['RTC'])

		return(self.canSend(self.genArray(msg)))

	def doParada(self):
		"""
			Detiene todas las interrupciones y lecturas del equipo.
		"""
		msg = self.genMsg(self.functions['DO'], self.variables['PARADA'])

		self.canSend(self.genArray(msg))

	def doSoftReset(self):
		"""
			Reinicia el equipo.
		"""
		msg = self.genMsg(self.functions['DO'], self.variables['SOFT_RESET'])

		self.canSend(self.genArray(msg))