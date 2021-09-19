import connection as conn
from constants import master_address, functions, variables
from datetime import datetime

class Microredes(object):
    def __init__(self, port, baudrate, bitrate=250000):
        self.conn = conn.Connection()
        self.conn.connect(port, baudrate, bitrate)

    def can_send(self, arr, interval):
        arbitration_id = (arr[0] << 5) | arr[1]

        data_low = arr[2:6][::-1]
        data_high = arr[6:10][::-1]
        envio = data_low + data_high

        self.conn.send_cmd(arbitration_id, envio, interval)

    def gen_array(self, msg):
        arr = [msg['function'], msg['origin'], msg['target'], msg['variable']] + msg['data']
        return arr

    def gen_msg(self, function, variable, data = [0, 0, 0, 0, 0, 0]):
        return {
            'function': int(function, 0),
            'origin': master_address,
            'target': self.target,
            'variable': int(variable, 0),
            'data': data
        }

    def exec_query(self, msg, interval=0):
        query_array = self.gen_array(msg)
        self.can_send(query_array, interval)

    def set_target(self, target: int) -> None:
        """
            Setea la dirección del equipo de destino.
        """
        self.target = target

    def can_read(self):
        return self.msg_parse(self.conn.read_from_bus(self.target))
        # return self.conn.read_from_bus(self.target)

    def parse_msg(self, msg):
        origen = hex(msg.arbitration_id & 0x1F)
        funcion = msg.arbitration_id >> 5
        lst_data = [hex(x) for x in msg.data]
        data_low = lst_data[0:4][::-1]
        data_high = lst_data[4:8][::-1]
        str_data = data_low + data_high
        str_funcion = list(functions.keys())[list(functions.values()).index(hex(funcion))]
        timestamp = datetime.fromtimestamp(msg.timestamp).strftime('%H:%M:%S')
        variable = msg.data[2]
        valor = self.calcular_valor(variable, data_low, data_high)
        return origen, str_funcion, str_data, timestamp, variable, valor

    def msg_parse(self, msgs):
        ret = []
        multiple = True if len(msgs) > 1 else False
        data = [] if multiple else None
        timestamp = None
        origen = None
        valor_final = ''

        if len(msgs) > 0:
            if multiple:
                ret.append({
                    'origen': '',
                    'data': [],
                    'valor': ''
                    })
                for msg in msgs:
                    origen, str_funcion, str_data, timestamp, variable, valor = self.parse_msg(msg)

                    ret[0]['origen'] = origen
                    ret[0]['data'].append(str_data)
                    ret[0]['valor'] = ret[0]['valor'] + valor + ' '
            else:
                origen, str_funcion, str_data, timestamp, variable, valor = self.parse_msg(msgs[0])
                ret.append({
                    'origen': origen,
                    'data': str_data,
                    'valor': valor
                })

        return ret


    def do_digital_out(self, pin: int, mode: bool) -> None:
        """
            Enciende/Apaga salida digital indicada.

            pin : int, PIN [2-9].
            mode : boolean, True enciende, False apaga.
        """
        if pin < 2 or pin > 9:
            print('ERROR: Los pines digitales están comprendidos entre el 2 y el 9')
            return

        data_array = [pin, int(mode), 0, 0, 0, 0]
        msg = self.gen_msg(functions['DO'], variables['DIGITAL_OUT'], data_array)

        self.exec_query(msg)

    def qry_digital_in(self, interval: int = 0):
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

    def set_modo_func(self, mode: int) -> None:
        """
            Setea el modo de funcionamiento de la placa.

            mode: int, Modo de trabajo de la placa [1-5].
        """
        if mode < 1 or mode > 4:
            print('ERROR: Los modos disponibles están comprendidos entre el 1 y el 5')
            return

        data_array = [mode, 0, 0, 0, 0, 0]
        msg = self.gen_msg(functions['SET'], variables['MODO_FUNC'], data_array)

        self.exec_query(msg)

    def set_analog(self, cant_can: int) -> None:
        """
            Setea cantidad de canales analógicos.

            cant_can: int, Cantidad de canales analógicos a habilitar [1-8].
        """
        if cant_can < 1 or cant_can > 8:
            print('ERROR: La cantidad de canales analógicos es entre 1 y 8')
            return

        data_array = [cant_can, 0, 0, 0, 0, 0]
        msg = self.gen_msg(functions['SET'], variables['ANALOG'], data_array)

        self.exec_query(msg)

    def set_in_amp(self, cant_can):
        """
            Setea cantidad de canales in-Amp.

            cant_can: int, Cantidad de canales in-Amp a habilitar [1-4].
        """
        if cant_can < 1 or cant_can > 4:
            print('ERROR: La cantidad de canales in-Amp es entre 1 y 4')
            return

        data_array = [cant_can, 0, 0, 0, 0, 0]
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

    def set_rtc(self, date, hour):
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

    def calcular_valor(self, variable, data_low, data_high):
        calc_datetime = [0x0a]
        calc_can_analog = [0x03]
        calc_urms = [0x10, 0x11, 0x12]
        calc_irms = [0x13, 0x14, 0x15]
        calc_irms_n = [0x16]
        calc_p_mean = [0x17, 0x18, 0x19]
        calc_p_mean_t = [0x1a]
        calc_q_mean = [0x1b, 0x1c, 0x1d]
        calc_q_mean_t = [0x1e]
        calc_s_mean = [0x1f, 0x20, 0x21]
        calc_s_mean_t = [0x22]
        calc_pf_mean = [0x23, 0x24, 0x25, 0x26]
        calc_thdu = [0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c]
        calc_frec = [0x2d]
        calc_temp = [0x2e]

        valor = 0
        valor_final = None
        value_low = int('0x' + ''.join([format(int(c, 16), '02X') for c in data_low[2:4]]), 16)
        value_high = int('0x' + ''.join([format(int(c, 16), '02X') for c in data_high[0:1]]), 16)

        sign = ''

        if variable in calc_urms:
            valor = 0.01*(value_low+value_high/256)
            unidad = 'v'
        elif variable in calc_irms:
            valor = 0.001*(value_low+value_high/256)
            unidad = 'A'
        elif variable in calc_irms_n:
            valor = 0.001*value_low
            unidad = 'A'
        elif variable in calc_p_mean:
            sign, value_low, value_high = self.calc(data_low[2:4], data_high[0:1])
            valor = value_low + value_high / 256
            unidad = 'W'
        elif variable in calc_p_mean_t:
            sign, value_low, value_high = self.calc(data_low[2:4], data_high[0:1])
            valor = 4*(value_low + value_high / 256)
            unidad = 'W'
        elif variable in calc_q_mean:
            sign, value_low, value_high = self.calc(data_low[2:4], data_high[0:1])
            valor = value_low + value_high / 256
            unidad = 'VAr'
        elif variable in calc_q_mean_t:
            sign, value_low, value_high = self.calc(data_low[2:4], data_high[0:1])
            valor = 4*(value_low + value_high / 256)
            unidad = 'VAr'
        elif variable in calc_s_mean:
            sign, value_low, value_high = self.calc(data_low[2:4], data_high[0:1])
            valor = value_low + value_high / 256
            unidad = 'VA'
        elif variable in calc_s_mean_t:
            sign, value_low, value_high = self.calc(data_low[2:4], data_high[0:1])
            valor = 4*(value_low + value_high / 256)
            unidad = 'VA'
        elif variable in calc_pf_mean:
            sign, value_low, value_high = self.calc(data_low[2:4], data_high[0:1])
            valor = 0.001*(value_low + value_high / 256)
            unidad = 'W'
        elif variable in calc_thdu:
            valor = 0.01*(value_low)
            unidad = '%'
        elif variable in calc_frec:
            valor = value_low/100
            unidad = 'Hz'
        elif variable in calc_temp:
            valor = value_low
            unidad = 'C'
        elif variable in calc_datetime:
            valor_final = self.hex_to_str(data_low[2]) + self.hex_to_str(data_low[3]) + self.hex_to_str(data_high[0]) + self.hex_to_str(data_high[1]) + self.hex_to_str(data_high[2]) + self.hex_to_str(data_high[3])
        elif variable in calc_can_analog:
            # value_low = int('0x' + ''.join([format(int(c, 16), '02X') for c in data_low[2:4]]), 16)
            # value_high = int('0x' + ''.join([format(int(c, 16), '02X') for c in data_high[0:1]]), 16)

            val1 = int('0x' + ''.join([format(int(c, 16), '02X') for c in data_low[2:4]]), 16)
            val2 = int('0x' + ''.join([format(int(c, 16), '02X') for c in data_low[2:4]]), 16)
            valor_final = (((val1*255) + val2) / 4096) * 3.3
            # val = val1 << 8
            # print(valor_final)
        else:
            pass
            # print("La función " + str(variable) + " es incorrecta")

        # Redondea el valor a 3 decimales y lo devuelve en formato string junto con su unidad de medida
        if valor:
            valor_final = sign + str(round(valor, 3)) + ' ' + unidad

        return valor_final

    def calc(self, data_low, data_high):
        sign, val = self.twos_complement(data_low + data_high, 32)
        rsl = self.str_to_hex(val)
        val1 = int('0x' + ''.join([format(int(c, 16), '02X') for c in rsl[0:2]]), 16)
        val2 = int('0x' + ''.join([format(int(c, 16), '02X') for c in rsl[2:4]]), 16)
        return sign, val1, val2

    def twos_complement(self, value, bits):
        # Se pasa a hexa el valor recibido
        val = int('0x' + ''.join([format(int(c, 16), '02X') for c in value]), 16)
        # Cálculo del complemento a 2
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)

        sign = '-' if val < 0 else ''

        return sign, abs(val)

    def str_to_hex(self, value):
        # Convierto a hexadecimal y elimino '0x' del string
        val = hex(value)[2:]
        # Agrego ceros a la izquierda para completar los 4 bytes
        filled_value = val.zfill(8)
        # Devuelve array de valores agrupado de a dos
        return [hex(int(filled_value[i:i+2], 16)) for i in range(0, len(filled_value), 2)]

    def hex_to_str(self, hex_str):
        return str(int(hex_str, 0))