import connection as conn
import calc_helper as cal
from constants import master_address, functions, variables
from datetime import datetime

class Microredes(object):
    def __init__(self, port, baudrate, bitrate=250000):
        self.conn = conn.Connection()
        self.conn.connect(port, baudrate, bitrate)

    def can_send(self, arr: list, interval: int):
        """
            Envia la consulta al BUS CAN.

            arr: list, Array con los datos de la consulta a enviar.
            interval: int, Intervalo de repetición de la consulta,
                           en caso de ser 0 ejecuta una sola.
        """
        arbitration_id = (arr[0] << 5) | arr[1]

        # Da vuelta los valores low y high para el envío
        data_low = arr[2:6][::-1]
        data_high = arr[6:10][::-1]
        envio = data_low + data_high

        self.conn.send_cmd(arbitration_id, envio, interval)

    def gen_array(self, msg: dict) -> list:
        """
            Genera array para la consulta CAN.

            msg: dict, Objeto con los datos de la consulta.
        """
        arr = [msg['function'], msg['origin'], msg['target'], msg['variable']] + msg['data']
        return arr

    def gen_msg(self, function: int, variable: int, data: list = [0, 0, 0, 0, 0, 0]) -> dict:
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

    def exec_query(self, msg, interval: int = 0) -> None:
        """
            Genera un array para la consulta a partir del objeto de envío
            y llama a la función can_send.

            msg: dict, Objeto con los datos para el envío del mensaje.
        """
        query_array = self.gen_array(msg)
        self.can_send(query_array, interval)

    def set_target(self, target: int) -> None:
        """
            Setea la dirección del equipo de destino.
        """
        self.target = target

    def can_read(self) -> list:
        """
            Lee el BUS CAN.
        """
        return self.msg_parse(self.conn.read_from_bus(self.target))

    def byte_array_to_list(self, bytearray: bytearray) -> list:
        # Convierte de bytearray a lista
        lst_data = [hex(x) for x in bytearray]
        # Recupera la parte baja del mensaje y la da vuelta
        data_low = lst_data[0:4][::-1]
        # Recupera la parte alta del mensaje y la da vuelta
        data_high = lst_data[4:8][::-1]
        return data_low + data_high

    def parse_msg(self, msg: list) -> dict:
        """
            Parsea el mensaje distinguiendo origen, funcion, cuerpo del mensaje y llama a
            la función de calculo de valor. Luego devuelve objeto de mensaje parseado.

            msg: list, Mensaje recibido por BUS CAN.
        """
        origen = hex(msg.arbitration_id & 0x1F)
        funcion = msg.arbitration_id >> 5
        lst_data = self.byte_array_to_list(msg.data)
        status_code = list(functions.keys())[list(functions.values()).index(hex(funcion))]
        timestamp = datetime.fromtimestamp(msg.timestamp).isoformat(" ")
        variable = msg.data[2]

        calc_helper = cal.CalcHelper()
        valor, unidad = calc_helper.calc_value(variable, lst_data)
        return {
                'origen': origen,
                'status': status_code,
                'timestamp': timestamp,
                'data': lst_data,
                'valor': valor,
                'unidad': unidad
            }

    def msg_parse(self, msgs: list) -> list:
        """
            Recorre los mensajes encontrados en el bus, llama a la función de parseo
            y devuelva una lista con todos los mensajes encontrados.

            msgs: list, Lista de mensajes provenientes del BUS CAN.
        """
        ret = []
        for msg in msgs:
            parsed_msg = self.parse_msg(msg)
            ret.append(parsed_msg)

        return ret

    def do_digital_out(self, pin: int, mode: bool) -> None:
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

    def qry_digital_in(self, interval: int = 0) -> None:
        """
            Recupera estado de los pines digitales.
        """
        msg = self.gen_msg(functions['QRY'], variables['DIGITAL_IN'])

        self.exec_query(msg, interval)

    def qry_analog_in(self, pin: int, interval: int = 0) -> None:
        """
            Recupera valor del pin analógico pasado por parámetro.

            pin: int, PIN [0-7].
        """
        data_array = [pin, 0, 0, 0, 0, 0]
        msg = self.gen_msg(functions['QRY'], variables['ANALOG_IN'], data_array)

        self.exec_query(msg, interval)

    def do_analog_out(self, pin: int, steps: int) -> None:
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

    def set_in_amp(self, cant_can: int) -> None:
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

    def set_amp_in_amp(self, pin: int, amp: int) -> None:
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

    def do_pwm(self, pin: int, duty: int) -> None:
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

    def hb_echo(self, char: int) -> None:
        """
            Devuelve el mismo valor pasado por parámetro. Sirve a modo de heartbeat.

            char: int, Valor [0-127].
        """
        if char < 0 or char > 127:
            print('ERROR: El valor de estar comprendido entre 0 y 127')
            return

        data_array = [char, 0, 0, 0, 0, 0]
        msg = self.gen_msg(functions['HB'], variables['ECHO'], data_array)

        return self.exec_query(msg)

    def set_rtc(self, date: str, hour: str) -> None:
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

    def qry_rtc(self, interval: int = 0) -> None:
        """
            Recupera fecha y hora del RTC del equipo.
        """
        msg = self.gen_msg(functions['QRY'], variables['RTC'])

        self.exec_query(msg, interval)

    def do_parada(self) -> None:
        """
            Detiene todas las interrupciones y lecturas del equipo.
        """
        msg = self.gen_msg(functions['DO'], variables['PARADA'])

        self.exec_query(msg)

    def do_soft_reset(self) -> None:
        """
            Reinicia el equipo.
        """
        msg = self.gen_msg(functions['DO'], variables['SOFT_RESET'])

        self.exec_query(msg)

    def qry_u_a(self) -> None:
        """
            Recupera tensión F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['U_A'])

        self.exec_query(msg)

    def qry_u_b(self) -> None:
        """
            Recupera tensión F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['U_B'])

        self.exec_query(msg)

    def qry_u_c(self) -> None:
        """
            Recupera tensión F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['U_C'])

        self.exec_query(msg)

    def qry_i_a(self) -> None:
        """
            Recupera corriente F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['I_A'])

        self.exec_query(msg)

    def qry_i_b(self) -> None:
        """
            Recupera corriente F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['I_B'])

        self.exec_query(msg)

    def qry_i_c(self) -> None:
        """
            Recupera corriente F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['I_C'])

        self.exec_query(msg)

    def qry_i_n1(self) -> None:
        """
            Recupera corriente N.
        """
        msg = self.gen_msg(functions['QRY'], variables['I_N1'])

        self.exec_query(msg)

    def qry_pa_a(self) -> None:
        """
            Recupera potencia activa F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['PA_A'])

        self.exec_query(msg)

    def qry_pa_b(self) -> None:
        """
            Recupera potencia activa F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['PA_B'])

        self.exec_query(msg)

    def qry_pa_c(self) -> None:
        """
            Recupera potencia activa F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['PA_C'])

        self.exec_query(msg)

    def qry_pa_tot(self) -> None:
        """
            Recupera potencia activa total.
        """
        msg = self.gen_msg(functions['QRY'], variables['PA_TOT'])

        self.exec_query(msg)

    def qry_pr_a(self) -> None:
        """
            Recupera potencia reactiva F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['PR_A'])

        self.exec_query(msg)

    def qry_pr_b(self) -> None:
        """
            Recupera potencia reactiva F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['PR_B'])

        self.exec_query(msg)

    def qry_pr_c(self) -> None:
        """
            Recupera potencia reactiva F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['PR_C'])

        self.exec_query(msg)

    def qry_pr_tot(self) -> None:
        """
            Recupera potencia reactiva total.
        """
        msg = self.gen_msg(functions['QRY'], variables['PR_TOT'])

        self.exec_query(msg)

    def qry_fp_a(self) -> None:
        """
            Recupera factor de potencia F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['FP_A'])

        self.exec_query(msg)

    def qry_fp_b(self) -> None:
        """
            Recupera factor de potencia F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['FP_B'])

        self.exec_query(msg)

    def qry_fp_c(self) -> None:
        """
            Recupera factor de potencia F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['FP_C'])

        self.exec_query(msg)

    def qry_fp_tot(self) -> None:
        """
            Recupera factor de potencia total.
        """
        msg = self.gen_msg(functions['QRY'], variables['FP_TOT'])

        self.exec_query(msg)

    def qry_thdu_a(self) -> None:
        """
            Recupera distorsion armónica en tensión F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDU_A'])

        self.exec_query(msg)

    def qry_thdu_b(self) -> None:
        """
            Recupera distorsion armónica en tensión F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDU_B'])

        self.exec_query(msg)

    def qry_thdu_c(self) -> None:
        """
            Recupera distorsion armónica en tensión F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDU_C'])

        self.exec_query(msg)

    def qry_thdi_a(self) -> None:
        """
            Recupera distorsion armónica en corriente F1.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDI_A'])

        self.exec_query(msg)

    def qry_thdi_b(self) -> None:
        """
            Recupera distorsion armónica en corriente F2.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDI_B'])

        self.exec_query(msg)

    def qry_thdi_c(self) -> None:
        """
            Recupera distorsion armónica en corriente F3.
        """
        msg = self.gen_msg(functions['QRY'], variables['THDI_C'])

        self.exec_query(msg)

    def qry_frec(self) -> None:
        """
            Recupera frecuencia.
        """
        msg = self.gen_msg(functions['QRY'], variables['FREC'])

        self.exec_query(msg)

    def qry_temp(self) -> None:
        """
            Recupera temperatura.
        """
        msg = self.gen_msg(functions['QRY'], variables['TEMP'])

        self.exec_query(msg)
