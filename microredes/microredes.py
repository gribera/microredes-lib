import microredes.connection as conn
import microredes.calc_helper as cal
from microredes.constants import master_address, functions, variables
from datetime import datetime
import uuid


class Microredes(object):
    listeners = dict()

    def __init__(self, port, baudrate, bitrate=250000):
        self.conn = conn.Connection()
        self.conn.connect(port, baudrate, bitrate)

    # def can_send(self, arr: list, interval: int):
    def can_send(self, arr, interval):
        """
            Envia la consulta al BUS CAN.

            arr: list, Array con los datos de la consulta a enviar.
            interval: int, Intervalo de repetición de la consulta,
                           en caso de ser 0 ejecuta una sola.
        """
        listener_id = ''
        arbitration_id = (arr[0] << 5) | arr[1]

        # Da vuelta los valores low y high para el envío
        data_low = arr[2:6][::-1]
        data_high = arr[6:10][::-1]
        envio = data_low + data_high

        listener = self.conn.send_cmd(arbitration_id, envio, interval)

        if listener:
            listener_id = str(uuid.uuid1().hex)
            self.listeners.update({listener_id: listener})

        return listener_id

    def get_listeners(self):
        return self.listeners

    def stop_listener(self, listener_id):
        self.listeners[listener_id].stop()

    def gen_array(self, msg):
        """
            Genera array para la consulta CAN.

            msg: dict, Objeto con los datos de la consulta.
        """
        arr = [msg['function'],
               msg['origin'],
               msg['target'],
               msg['variable']] + msg['data']
        return arr

    def gen_msg(self, function, variable, data=[0, 0, 0, 0, 0, 0]):
        """
            Genera objeto con la estructura para el envío

            function: int, Función a ejecutar.
            variable: int, Variable a consultar.
            data: list, Array con los datos a enviar.
        """
        return {
            'function': int(function, 0),
            'origin': master_address,
            'target': self.target,
            'variable': int(variable, 0),
            'data': data
        }

    def exec_query(self, msg, interval=0):
        """
            Genera un array para la consulta a partir del objeto de envío
            y llama a la función can_send.

            msg: dict, Objeto con los datos para el envío del mensaje.
        """
        query_array = self.gen_array(msg)
        return self.can_send(query_array, interval)

    def set_target(self, target):
        """
            Setea la dirección del equipo de destino.
        """
        self.target = target

    def can_read(self):
        """
            Lee el BUS CAN.
        """
        return self.msg_parse(self.conn.read_from_bus(self.target))

    def byte_array_to_list(self, bytearray):
        # Convierte de bytearray a lista
        lst_data = [hex(x) for x in bytearray]
        # Recupera la parte baja del mensaje y la da vuelta
        data_low = lst_data[0:4][::-1]
        # Recupera la parte alta del mensaje y la da vuelta
        data_high = lst_data[4:8][::-1]
        return data_low + data_high

    def parse_msg(self, msg):
        """
            Parsea el mensaje distinguiendo origen, funcion,
            cuerpo del mensaje y llama a la función de calculo de valor.
            Luego devuelve objeto de mensaje parseado.

            msg: list, Mensaje recibido por BUS CAN.
        """
        origen = hex(msg.arbitration_id & 0x1F)
        funcion = msg.arbitration_id >> 5
        lst_data = self.byte_array_to_list(msg.data)
        function_index = list(functions.values()).index(hex(funcion))
        status_code = list(functions.keys())[function_index]
        timestamp = datetime.fromtimestamp(msg.timestamp).isoformat(" ")
        variable = msg.data[2]

        calc_helper = cal.CalcHelper()
        valor, unidad = calc_helper.calc_value(variable, lst_data)
        return {'origen': origen,
                'status': status_code,
                'timestamp': timestamp,
                'data': lst_data,
                'valor': valor,
                'unidad': unidad}

    def msg_parse(self, msgs):
        """
            Recorre los mensajes encontrados en el bus, llama a la
            función de parseo y devuelve una lista con todos los
            mensajes encontrados.

            msgs: list, Lista de mensajes provenientes del BUS CAN.
        """
        ret = []
        for msg in msgs:
            parsed_msg = self.parse_msg(msg)
            ret.append(parsed_msg)

        return ret

    def do_digital_out(self, pin, mode):
        """
            Enciende/Apaga salida digital indicada.

            pin: int, PIN [2-9].
            mode: boolean, True enciende, False apaga.
        """
        if pin < 2 or pin > 9:
            raise ValueError('ERROR: Los pines digitales están comprendidos'
                  + 'entre el 2 y el 9')

        data_array = [pin, int(mode), 0, 0, 0, 0]
        msg = self.gen_msg(functions['DO'],
                           variables['DIGITAL_OUT'],
                           data_array)

        return self.exec_query(msg)

    def qry_digital_in(self, interval=0):
        """
            Recupera estado de los pines digitales.
        """
        msg = self.gen_msg(functions['QRY'], variables['DIGITAL_IN'])

        return self.exec_query(msg, interval)

    def qry_analog_in(self, pin, interval=0):
        """
            Recupera valor del pin analógico pasado por parámetro.

            pin: int, PIN [0-7].
        """
        if pin < 0 or pin > 7:
            raise ValueError('ERROR: Los pines analógicos sólo'
                             + 'pueden ser 0 o 7')

        data_array = [pin, 0, 0, 0, 0, 0]
        msg = self.gen_msg(functions['QRY'],
                           variables['ANALOG_IN'],
                           data_array)

        return self.exec_query(msg, interval)

    def do_analog_out(self, pin, steps):
        """
            Setea salida del DAC.

            pin: int, PIN [0-1].
            steps: int, Valor a setear como salida del DAC [0-4095].
        """
        if pin < 0 or pin > 1:
            raise ValueError('ERROR: Los pines del DAC sólo pueden ser 0 o 1')

        if steps < 0 or steps > 4095:
            raise ValueError('ERROR: El valor no puede ser mayor a 4095')

        data_array = [pin, 0, 0, 0, 0, 0]  # TODO: Pasar a bytes los steps
        msg = self.gen_msg(functions['DO'],
                           variables['ANALOG_OUT'],
                           data_array)

        return self.exec_query(msg)

    def set_modo_func(self, mode):
        """
            Setea el modo de funcionamiento de la placa.

            mode: int, Modo de trabajo de la placa [1-5].
        """
        if mode < 1 or mode > 4:
            raise ValueError('ERROR: Los modos disponibles están comprendidos'
                  + 'entre el 1 y el 5')

        data_array = [mode, 0, 0, 0, 0, 0]
        msg = self.gen_msg(functions['SET'],
                           variables['MODO_FUNC'],
                           data_array)

        return self.exec_query(msg)

    def set_analog(self, cant_can):
        """
            Setea cantidad de canales analógicos.

            cant_can: int, Cantidad de canales analógicos a habilitar [1-8].
        """
        if cant_can < 1 or cant_can > 8:
            raise ValueError('ERROR: La cantidad de canales analógicos'
                             + 'es entre 1 y 8')

        data_array = [cant_can, 0, 0, 0, 0, 0]
        msg = self.gen_msg(functions['SET'], variables['ANALOG'], data_array)

        return self.exec_query(msg)

    def set_in_amp(self, cant_can):
        """
            Setea cantidad de canales in-Amp.

            cant_can: int, Cantidad de canales in-Amp a habilitar [1-4].
        """
        if cant_can < 1 or cant_can > 4:
            raise ValueError('ERROR: La cantidad de canales in-Amp'
                             + 'es entre 1 y 4')

        data_array = [cant_can, 0, 0, 0, 0, 0]
        msg = self.gen_msg(functions['SET'], variables['IN-AMP'], data_array)

        return self.exec_query(msg)

    def set_amp_in_amp(self, pin, amp):
        """
            Setea amplificación de canales in-Amp.

            pin: int, Canal in-Amp a amplificar [9-12].
            amp: int, Amplificación [0-3].
        """
        if pin < 9 or pin > 12:
            raise ValueError('ERROR: Los canales in-Amp están comprendidos'
                  + 'entre el 9 y el 12')

        if amp < 0 or amp > 3:
            raise ValueError('ERROR: La amplificación es un valor comprendido'
                  + 'entre el 0 y el 3')

        data_array = [pin, amp, 0, 0, 0, 0]
        msg = self.gen_msg(functions['SET'],
                           variables['AMP-INAMP'],
                           data_array)

        return self.exec_query(msg)

    def do_pwm(self, pin, duty):
        """
            Habilita salida PWM.

            pin: int, Pin de salida [10-13].
            duty: int, Duty-Cycle [0-255].
        """
        if pin < 10 or pin > 13:
            raise ValueError('ERROR: Los pines PWM deben estar comprendidos'
                  + 'entre el 10 y el 13')

        if duty < 0 or duty > 255:
            raise ValueError('ERROR: El duty cycle debe ser un valor'
                             + 'entre 0 y 255')

        data_array = [pin, duty, 0, 0, 0, 0]
        msg = self.gen_msg(functions['DO'], variables['PWM'], data_array)

        return self.exec_query(msg)

    def hb_echo(self, char):
        """
            Devuelve el mismo valor pasado por parámetro.
            Sirve a modo de heartbeat.

            char: int, Valor [0-127].
        """
        if char < 0 or char > 127:
            raise ValueError('ERROR: El valor de estar comprendido'
                             + 'entre 0 y 127')

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

        if ((len(parsed_date) != 3)
                or (int(dd) > 31 or int(dd) < 1)
                or (int(mm) > 12 or int(mm) < 1)):
            raise ValueError('ERROR: Formato de fecha incorrecto')

        if ((len(parsed_hour) != 3)
                or (int(hh) > 24 or int(hh) < 1)
                or (int(MM) > 60 or int(MM) < 0)
                or (int(ss) > 60 or int(ss) < 0)):
            raise ValueError('ERROR: Formato de hora incorrecto')

        # Hora
        data_array = [int(hh[0]),
                      int(hh[1]),
                      int(MM[0]),
                      int(MM[1]),
                      int(ss[0]),
                      int(ss[1])]
        msg = self.gen_msg(functions['SET'], variables['RTC'], data_array)
        self.exec_query(msg)

        # Fecha
        data_array = [int(dd[0]),
                      int(dd[1]),
                      int(mm[0]),
                      int(mm[1]),
                      int(aa[0]),
                      int(aa[1])]
        msg = self.gen_msg(functions['SET'], variables['RTC'], data_array)

        return self.exec_query(msg)

    def qry_rtc(self, interval=0):
        """
            Recupera fecha y hora del RTC del equipo.
        """
        msg = self.gen_msg(functions['QRY'], variables['RTC'])

        return self.exec_query(msg, interval)

    def do_parada(self):
        """
            Detiene todas las interrupciones y lecturas del equipo.
        """
        msg = self.gen_msg(functions['DO'], variables['PARADA'])

        return self.exec_query(msg)

    def do_soft_reset(self):
        """
            Reinicia el equipo.
        """
        msg = self.gen_msg(functions['DO'], variables['SOFT_RESET'])

        return self.exec_query(msg)

    def qry_u_a(self, interval=0):
        """
            Recupera tensión F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['U_A'])

        return self.exec_query(msg, interval)

    def qry_u_b(self, interval=0):
        """
            Recupera tensión F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['U_B'])

        return self.exec_query(msg, interval)

    def qry_u_c(self, interval=0):
        """
            Recupera tensión F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['U_C'])

        return self.exec_query(msg, interval)

    def qry_i_a(self, interval=0):
        """
            Recupera corriente F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['I_A'])

        return self.exec_query(msg, interval)

    def qry_i_b(self, interval=0):
        """
            Recupera corriente F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['I_B'])

        return self.exec_query(msg, interval)

    def qry_i_c(self, interval=0):
        """
            Recupera corriente F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['I_C'])

        return self.exec_query(msg, interval)

    def qry_i_n1(self, interval=0):
        """
            Recupera corriente N.
        """
        msg = self.gen_msg(functions['QRY'], variables['I_N1'])

        return self.exec_query(msg, interval)

    def qry_pa_a(self, interval=0):
        """
            Recupera potencia activa F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['PA_A'])

        return self.exec_query(msg, interval)

    def qry_pa_b(self, interval=0):
        """
            Recupera potencia activa F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['PA_B'])

        return self.exec_query(msg, interval)

    def qry_pa_c(self, interval=0):
        """
            Recupera potencia activa F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['PA_C'])

        return self.exec_query(msg, interval)

    def qry_pa_tot(self, interval=0):
        """
            Recupera potencia activa total.
        """
        msg = self.gen_msg(functions['QRY'], variables['PA_TOT'])

        return self.exec_query(msg, interval)

    def qry_pr_a(self, interval=0):
        """
            Recupera potencia reactiva F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['PR_A'])

        return self.exec_query(msg, interval)

    def qry_pr_b(self, interval=0):
        """
            Recupera potencia reactiva F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['PR_B'])

        return self.exec_query(msg, interval)

    def qry_pr_c(self, interval=0):
        """
            Recupera potencia reactiva F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['PR_C'])

        return self.exec_query(msg, interval)

    def qry_pr_tot(self, interval=0):
        """
            Recupera potencia reactiva total.
        """
        msg = self.gen_msg(functions['QRY'], variables['PR_TOT'])

        return self.exec_query(msg, interval)

    def qry_fp_a(self, interval=0):
        """
            Recupera factor de potencia F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['FP_A'])

        return self.exec_query(msg, interval)

    def qry_fp_b(self, interval=0):
        """
            Recupera factor de potencia F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['FP_B'])

        return self.exec_query(msg, interval)

    def qry_fp_c(self, interval=0):
        """
            Recupera factor de potencia F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['FP_C'])

        return self.exec_query(msg, interval)

    def qry_fp_tot(self, interval=0):
        """
            Recupera factor de potencia total.
        """
        msg = self.gen_msg(functions['QRY'], variables['FP_TOT'])

        return self.exec_query(msg, interval)

    def qry_thdu_a(self, interval=0):
        """
            Recupera distorsion armónica en tensión F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDU_A'])

        return self.exec_query(msg, interval)

    def qry_thdu_b(self, interval=0):
        """
            Recupera distorsion armónica en tensión F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDU_B'])

        return self.exec_query(msg, interval)

    def qry_thdu_c(self, interval=0):
        """
            Recupera distorsion armónica en tensión F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDU_C'])

        return self.exec_query(msg, interval)

    def qry_thdi_a(self, interval=0):
        """
            Recupera distorsion armónica en corriente F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDI_A'])

        return self.exec_query(msg, interval)

    def qry_thdi_b(self, interval=0):
        """
            Recupera distorsion armónica en corriente F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDI_B'])

        return self.exec_query(msg, interval)

    def qry_thdi_c(self, interval=0):
        """
            Recupera distorsion armónica en corriente F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDI_C'])

        return self.exec_query(msg, interval)

    def qry_frec(self, interval=0):
        """
            Recupera frecuencia.
        """
        msg = self.gen_msg(functions['QRY'], variables['FREC'])

        return self.exec_query(msg, interval)

    def qry_temp(self, interval=0):
        """
            Recupera temperatura.
        """
        msg = self.gen_msg(functions['QRY'], variables['TEMP'])

        return self.exec_query(msg, interval)
