# microredes-lib

## Listado de funciones

| Tipo | Función        | Parámetros                                                                                                 | Descripción                                                              |
| :--: | :------------- | :--------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------- |
|  DO  | do_digital_out | **pin** (int) Pin [2-9] <br/> **mode:** (bool) Enciende/Apaga                                              | Enciende/Apaga salida digital indicada.                                  |
|  DO  | do_analog_out  | **pin** (int) Pin [0-1] <br/> **steps:** (int) Valor                                                       | Setea salida del DAC.                                                    |
|  DO  | do_pwm         | **pin** (int) Pin de salida [10-13] <br/> **duty** (int) Duty Cicle                                        | Habilita salida PWM.                                                     |
|  DO  | do_parada      | -                                                                                                          | Detiene todas las interrupciones y lecturas del equipo.                  |
|  DO  | do_soft_reset  | -                                                                                                          | Reinicia el equipo.                                                      |
| QRY  | qry_digital_in | -                                                                                                          | Recupera estado de los pines digitales.                                  |
| QRY  | qry_analog_in  | **pin** (int) Pin [0-7]                                                                                    | Recupera valor del pin analógico pasado por parámetro.                   |
| QRY  | qry_rtc        | -                                                                                                          | Recupera fecha y hora del RTC del equipo.                                |
| SET  | set_modo_func  | **mode** (int) Modo de trabajo [0-4]                                                                       | Setea el modo de funcionamiento de la placa.                             |
| SET  | set_analog     | **cant_can** (int) Cantidad de canales analógicos a habilitar [1-8]                                        | Setea cantidad de canales analógicos.                                    |
| SET  | set_in_amp     | **cant_can** (int) Cantidad de canales in-Amp a habilitar                                                  | Setea cantidad de canales in-Amp.                                        |
| SET  | set_amp_in_amp | **pin** (int) Canal in-Amp a amplificar [9-12] <br/> **amp** (int) Amplificación [0-3] (int) Amplificación | Setea amplificación de canales in-Amp.                                   |
| SET  | set_rtc        | **fecha** (string) Fecha en formato dd/mm/aa. <br/> **hora** (string) Hora en formato hh:mm:ss             | Setea la fecha y hora en el RTC del equipo.                              |
|  HB  | hb_echo        | **val** (int) Valor [0-127]                                                                                | Devuelve el mismo valor pasado por parámetro. Sirve a modo de heartbeat. |
