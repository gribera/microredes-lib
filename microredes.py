import connection as conn
from constants import master_address, functions, variables

class Microredes(object):
	def __init__(self, addr, equipo):
		self.addr = addr
		self.equipo = equipo
		self.conn = conn.Connection()

	def __getattribute__(self, name):
		attr = object.__getattribute__(self, name)
		if hasattr(attr, '__call__'):
			def newfunc(*args, **kwargs):
				if not self.conn.is_connected() and attr.__name__ != 'connect':
					raise ConnectionError('No está conectado')

				result = attr(*args, **kwargs)
				return result
			return newfunc
		else:
			return attr

	def connect(self, port, baudrate):
		self.conn.connect(port, baudrate)

	def init_buffer(self):
		self.conn.init_can_listener()

	def stop_buffer(self):
		self.conn.stop_can_listener()

	def gen_array(self, msg):
		arr = [msg['function'], msg['origin'], msg['target'], msg['variable']] + msg['data']
		return arr

	def gen_msg(self, function, variable, data = [0, 0, 0, 0, 0, 0]):
		return {
			'function': int(function, 0),
			'origin': master_address,
			'target': self.addr,
			'variable': int(variable, 0),
			'data': data
		}

	def can_send(self, arr, interval):
		arbitration_id = (arr[0] << 5) | arr[1]

		data_low = arr[2:6][::-1]
		data_high = arr[6:10][::-1]
		envio = data_low + data_high

		self.conn.send_cmd(arbitration_id, envio, interval)

	def can_read(self):
		return self.conn.read_from_bus()

	def exec_query(self, msg, interval=0):
		query_array = self.gen_array(msg)
		self.can_send(query_array, interval)

	def do_digital_out(self, pin, mode):
		"""
			Enciende/Apaga salida digital indicada.

			pin: int, PIN [2-9].
			mode: boolean, True enciende, False apaga.
		"""
		if pin < 2 or pin > 9:
			print('ERROR: Los pines digitales están comprendidos entre el 2 y el 9')
			return

		data_array = [pin, int(mode), 0, 0, 0, 0]
		msg = self.gen_msg(functions['DO'], variables['DIGITAL_OUT'], data_array)

		self.exec_query(msg)

	def qry_digital_in(self, interval=0):
		"""
			Recupera estado de los pines digitales.
		"""
		msg = self.gen_msg(functions['QRY'], variables['DIGITAL_IN'])

		self.exec_query(msg, interval)

	def qry_analog_in(self, pin, interval=0):
		"""
			Recupera valor del pin analógico pasado por parámetro.

			pin: int, PIN [0-7].
		"""
		data_array = [pin, 0, 0, 0, 0, 0]
		msg = self.gen_msg(functions['QRY'], variables['ANALOG_IN'], data_array)

		self.exec_query(msg, interval)

	def do_analog_out(self, pin, steps):
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

		data_array = [pin, 0, 0, 0, 0, 0] # TODO: Pasar a bytes los steps
		msg = self.gen_msg(functions['DO'], variables['ANALOG_OUT'], data_array)

		self.exec_query(msg)

	def set_modo_func(self, mode):
		"""
			Setea el modo de funcionamiento de la placa.

			mode: int, Modo de trabajo de la placa [0-4].
		"""
		if pin < 0 or pin > 4:
			print('ERROR: Los modos disponibles están comprendidos entre el 0 y el 4')
			return

		data_array = [mode, 0, 0, 0, 0, 0]
		msg = self.gen_msg(functions['SET'], variables['MODO_FUNC'], data_array)

		self.exec_query(msg)

	def set_analog(self, cantCan):
		"""
			Setea cantidad de canales analógicos.

			cantCan: int, Cantidad de canales analógicos a habilitar [1-8].
		"""
		if pin < 1 or pin > 8:
			print('ERROR: Los modos disponibles están comprendidos entre el 1 y el 8')
			return

		data_array = [cantCan, 0, 0, 0, 0, 0]
		msg = self.gen_msg(functions['SET'], variables['ANALOG'], data_array)

		self.exec_query(msg)

	def set_in_amp(self, cantCan):
		"""
			Setea cantidad de canales in-Amp.

			cantCan: int, Cantidad de canales in-Amp a habilitar [1-4].
		"""
		if pin < 1 or pin > 4:
			print('ERROR: Los modos disponibles están comprendidos entre el 1 y el 4')
			return

		data_array = [cantCan, 0, 0, 0, 0, 0]
		msg = self.gen_msg(functions['SET'], variables['IN-AMP'], data_array)

		self.exec_query(msg)

	def set_amp_in_amp(self, pin, amp):
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

		data_array = [pin, amp, 0, 0, 0, 0]
		msg = self.gen_msg(functions['SET'], variables['AMP-INAMP'], data_array)

		self.exec_query(msg)

	def do_pwm(self, pin, duty):
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

		data_array = [pin, duty, 0, 0, 0, 0]
		msg = self.gen_msg(functions['DO'], variables['PWM'], data_array)

		self.exec_query(msg)

	def hb_echo(self, char):
		"""
			Devuelve el mismo valor pasado por parámetro. Sirve a modo de heartbeat.

			char: int, Valor [0-127].
		"""
		if char < 0 or char > 255:
			print('ERROR: El valor de estar comprendido entre 0 y 127')
			return

		data_array = [char, 0, 0, 0, 0, 0]
		msg = self.gen_msg(functions['HB'], variables['ECHO'], data_array)

		return self.exec_query(msg)

	def set_rtc(self, date, hour): # TODO: Terminar esta función
		"""
			Setea la fecha y hora en el RTC del equipo.

			date: string, Fecha en formato dd/mm/aa.
			hour: string, Hora en formato hh:mm:ss.
		"""
		parsed_date = date.split('/')
		parsed_hour = hour.split(':')
		dd, mm, aa = parsed_date
		hh, MM, ss = parsed_hour

		if ((len(parsed_date) != 3) or
			(int(dd) > 31 or int(dd) < 1) or
			(int(mm) > 12 or int(mm) < 1)):
			print('ERROR: Formato de fecha incorrecto')
			return

		if ((len(parsed_hour) != 3) or
			(int(hh) > 24 or int(hh) < 1) or
			(int(MM) > 60 or int(MM) < 0) or
			(int(ss) > 60 or int(ss) < 0)):
			print('ERROR: Formato de hora incorrecto')
			return

		# Hora
		data_array = [int(hh[0]), int(hh[1]), int(MM[0]), int(MM[1]), int(ss[0]), int(ss[1])]
		msg = self.gen_msg(functions['SET'], variables['RTC'], data_array)

		# Fecha
		self.exec_query(msg)
		data_array = [int(dd[0]), int(dd[1]), int(mm[0]), int(mm[1]), int(aa[0]), int(aa[1])]
		msg = self.gen_msg(functions['SET'], variables['RTC'], data_array)

		self.exec_query(msg)

	def qry_rtc(self, interval=0):
		"""
			Recupera fecha y hora del RTC del equipo.
		"""
		msg = self.gen_msg(functions['QRY'], variables['RTC'])

		self.exec_query(msg, interval)

	def do_parada(self):
		"""
			Detiene todas las interrupciones y lecturas del equipo.
		"""
		msg = self.gen_msg(functions['DO'], variables['PARADA'])

		self.exec_query(msg)

	def do_soft_reset(self):
		"""
			Reinicia el equipo.
		"""
		msg = self.gen_msg(functions['DO'], variables['SOFT_RESET'])

		self.exec_query(msg)