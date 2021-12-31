class CalcHelper(object):
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

    def __init__(self):
        pass

    def datetime(self, data):
        final_value = ''
        # Descarto los dos primeros bytes del mensaje
        # (id del emisor y variable)
        msg_data = data[2:]
        for x in msg_data:
            final_value = final_value + self.hex_to_str(x)
        unit = None
        return final_value, unit

    def analog(self, value_low, value_high):
        final_value = (((value_low * 255) + value_low) / 4096) * 3.3
        unit = 'v'
        return final_value, unit

    def get_data_parts(self, data):
        return data[2:4], data[0:]
        # return data[0:4], data[4:8]

    def hex_arr_to_int(self, arr):
        end_arr = []
        for c in arr:
            end_arr.append(format(int(c, 16), '02X'))

        return int('0x' + ''.join(end_arr), 16)

    def get_value_parts(self, msg_data):
        data_low, data_high = self.get_data_parts(msg_data)
        value_low = self.hex_arr_to_int(data_low)
        value_high = self.hex_arr_to_int(data_high)
        return value_low, value_high

    def calc_value(self, variable, msg_data):
        valor = 0
        valor_final = None
        unidad = None
        data_low, data_high = self.get_data_parts(msg_data)
        value_low, value_high = self.get_value_parts(msg_data)
        sign = ''

        if variable in self.calc_urms:
            valor = 0.01 * (value_low + value_high / 256)
            unidad = 'v'
        elif variable in self.calc_irms:
            valor = 0.001 * (value_low + value_high / 256)
            unidad = 'A'
        elif variable in self.calc_irms_n:
            valor = 0.001 * value_low
            unidad = 'A'
        elif variable in self.calc_p_mean:
            sign, value_low, value_high = self.calc(data_low, data_high)
            valor = value_low + value_high / 256
            unidad = 'W'
        elif variable in self.calc_p_mean_t:
            sign, value_low, value_high = self.calc(data_low, data_high)
            valor = 4 * (value_low + value_high / 256)
            unidad = 'W'
        elif variable in self.calc_q_mean:
            sign, value_low, value_high = self.calc(data_low, data_high)
            valor = value_low + value_high / 256
            unidad = 'VAr'
        elif variable in self.calc_q_mean_t:
            sign, value_low, value_high = self.calc(data_low, data_high)
            valor = 4 * (value_low + value_high / 256)
            unidad = 'VAr'
        elif variable in self.calc_s_mean:
            sign, value_low, value_high = self.calc(data_low, data_high)
            valor = value_low + value_high / 256
            unidad = 'VA'
        elif variable in self.calc_s_mean_t:
            sign, value_low, value_high = self.calc(data_low, data_high)
            valor = 4 * (value_low + value_high / 256)
            unidad = 'VA'
        elif variable in self.calc_pf_mean:
            sign, value_low, value_high = self.calc(data_low, data_high)
            valor = 0.001 * (value_low + value_high / 256)
            unidad = 'W'
        elif variable in self.calc_thdu:
            valor = 0.01 * (value_low)
            unidad = '%'
        elif variable in self.calc_frec:
            valor = value_low / 100
            unidad = 'Hz'
        elif variable in self.calc_temp:
            valor = value_low
            unidad = 'C'
        elif variable in self.calc_datetime:
            valor_final, unidad = self.datetime(msg_data)
        elif variable in self.calc_can_analog:
            valor_final, unidad = self.analog(value_low, value_high)
        else:
            pass
            # print("La función " + str(variable) + " es incorrecta")

        # Redondea el valor a 3 decimales y lo devuelve en formato
        # string junto con su unidad de medida
        if valor:
            valor_final = sign + str(round(valor, 3))

        return valor_final, unidad

    def calc(self, data_low, data_high):
        sign, val = self.twos_complement(data_low + data_high, 32)
        rsl = self.str_to_hex(val)
        val1 = self.hex_arr_to_int(rsl[0:2])
        val2 = self.hex_arr_to_int(rsl[2:4])
        return sign, val1, val2

    def twos_complement(self, value, bits):
        # Se pasa a hexa el valor recibido
        val = self.hex_arr_to_int(value)
        # Cálculo del complemento a 2
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)

        sign = '-' if val < 0 else ''

        return sign, abs(val)

    def str_to_hex(self, value):
        end_arr = []
        # Convierto a hexadecimal y elimino '0x' del string
        val = hex(value)[2:]
        # Agrego ceros a la izquierda para completar los 4 bytes
        filled_value = val.zfill(8)

        for i in range(0, len(filled_value), 2):
            end_arr.append(hex(int(filled_value[i:i + 2], 16)))

        # Devuelve array de valores agrupado de a dos
        return end_arr

    def hex_to_str(self, hex_str):
        return str(int(hex_str, 0))
