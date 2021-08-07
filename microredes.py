import connection as conn
from constants import masterAddr, functions, variables

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

	def genArray(self, msg):
		arr = [msg['function'], msg['origin'], msg['target'], msg['variable']] + msg['data']
		return arr

	def genMsg(self, function, variable, data = [0, 0, 0, 0, 0, 0]):
		return {
			'function': int(function, 0),
			'origin': masterAddr,
			'target': self.addr,
			'variable': int(variable, 0),
			'data': data
		}

	def canSend(self, arr, interval):
		arbitrationId = (arr[0] << 5) | arr[1]

		dataLow = arr[2:6][::-1]
		dataHigh = arr[6:10][::-1]
		envio = dataLow + dataHigh

		if interval > 0:
			self.conn.sendPeriodic(arbitrationId, envio, interval)
		else:
			self.conn.sendCmd(arbitrationId, envio)

	def canRead(self):
		return self.conn.readFromBus()

	def execQuery(self, msg, interval=0):
		queryArray = self.genArray(msg)
		self.canSend(queryArray, interval)

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
		msg = self.genMsg(functions['DO'], variables['DIGITAL_OUT'], dataArray)

		self.execQuery(msg)

	def qryDigitalIn(self, interval=0):
		"""
			Recupera estado de los pines digitales.
		"""
		msg = self.genMsg(functions['QRY'], variables['DIGITAL_IN'])

		self.execQuery(msg, interval)

	def qryAnalogIn(self, pin, interval=0):
		"""
			Recupera valor del pin analógico pasado por parámetro.

			pin: int, PIN [0-7].
		"""
		dataArray = [pin, 0, 0, 0, 0, 0]
		msg = self.genMsg(functions['QRY'], variables['ANALOG_IN'], dataArray)

		self.execQuery(msg, interval)

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
		msg = self.genMsg(functions['DO'], variables['ANALOG_OUT'], dataArray)

		self.execQuery(msg)

	def setModoFunc(self, mode):
		"""
			Setea el modo de funcionamiento de la placa.

			mode: int, Modo de trabajo de la placa [0-4].
		"""
		if pin < 0 or pin > 4:
			print('ERROR: Los modos disponibles están comprendidos entre el 0 y el 4')
			return

		dataArray = [mode, 0, 0, 0, 0, 0]
		msg = self.genMsg(functions['SET'], variables['MODO_FUNC'], dataArray)

		self.execQuery(msg)

	def setAnalog(self, cantCan):
		"""
			Setea cantidad de canales analógicos.

			cantCan: int, Cantidad de canales analógicos a habilitar [1-8].
		"""
		if pin < 1 or pin > 8:
			print('ERROR: Los modos disponibles están comprendidos entre el 1 y el 8')
			return

		dataArray = [cantCan, 0, 0, 0, 0, 0]
		msg = self.genMsg(functions['SET'], variables['ANALOG'], dataArray)

		self.execQuery(msg)

	def setInAmp(self, cantCan):
		"""
			Setea cantidad de canales in-Amp.

			cantCan: int, Cantidad de canales in-Amp a habilitar [1-4].
		"""
		if pin < 1 or pin > 4:
			print('ERROR: Los modos disponibles están comprendidos entre el 1 y el 4')
			return

		dataArray = [cantCan, 0, 0, 0, 0, 0]
		msg = self.genMsg(functions['SET'], variables['IN-AMP'], dataArray)

		self.execQuery(msg)

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
		msg = self.genMsg(functions['SET'], variables['AMP-INAMP'], dataArray)

		self.execQuery(msg)

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
		msg = self.genMsg(functions['DO'], variables['PWM'], dataArray)

		self.execQuery(msg)

	def hbEcho(self, char):
		"""
			Devuelve el mismo valor pasado por parámetro. Sirve a modo de heartbeat.

			char: int, Valor [0-127].
		"""
		if char < 0 or char > 255:
			print('ERROR: El valor de estar comprendido entre 0 y 127')
			return

		dataArray = [char, 0, 0, 0, 0, 0]
		msg = self.genMsg(functions['HB'], variables['ECHO'], dataArray)

		return self.execQuery(msg)

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
		msg = self.genMsg(functions['SET'], variables['RTC'], dataArray)

		# Fecha
		self.execQuery(msg)
		dataArray = [int(dd[0]), int(dd[1]), int(mm[0]), int(mm[1]), int(aa[0]), int(aa[1])]
		msg = self.genMsg(functions['SET'], variables['RTC'], dataArray)

		self.execQuery(msg)

	def qryRTC(self, interval=0):
		"""
			Recupera fecha y hora del RTC del equipo.
		"""
		msg = self.genMsg(functions['QRY'], variables['RTC'])

		self.execQuery(msg, interval)

	def doParada(self):
		"""
			Detiene todas las interrupciones y lecturas del equipo.
		"""
		msg = self.genMsg(functions['DO'], variables['PARADA'])

		self.execQuery(msg)

	def doSoftReset(self):
		"""
			Reinicia el equipo.
		"""
		msg = self.genMsg(functions['DO'], variables['SOFT_RESET'])

		self.execQuery(msg)