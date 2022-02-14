# microredes-lib

## Instalación

### Requerimientos

Python 3.6 o superior

### Librerías necesarias para instalar

```sh
$ pip install --upgrade --pre python-can
```

### Instalación de la librería

```sh
$ pip install microredes
```

## Ejemplos de uso

```python3
from microredes import microredes as mr # Importación de la librería

bus = mr.Microredes('/dev/ttyUSB0', '115200') # Conexión al BUS
```

### Seteo de salida digital

```python3
bus.set_target(2) # Setea la dirección de destino del equipo a consultar
bus.do_digital_out(2, True) # Pone en True el pin digital 2
```

### Leyendo entrada analógica

```python3
bus.set_target(2) # Setea la dirección de destino del equipo a consultar
bus.qry_analog_in(0) # Lee la entrada analógica 0
res = bus.can_read() # Lee el BUS de datos y guarda la respuesta del query
print(res)
```

### Uso del intervalo

En el caso de las funciones de consulta (qry), existe un parámetro opcional que permite dejar en ejecución una consulta durante el tiempo indicado expresado en segundos.

```python3
bus.set_target(2) # Setea la dirección de destino del equipo a consultar
query_id = bus.qry_analog_in(0, interval=1) # Lee la entrada analógica 0 con un intervalo de 1 segundo

cont = 0  # Inicio contador en 0
while True:  # Lee en bucle infinito la respuesta desde el BUS
  res = bus.can_read()

  if len(res):
    print(res)
    cont += 1  # Incremento contador
    if cont == 5:  # Si el contador llega a 5
      bus.stop_listener(query_id)  # Detiene la consulta
      break
```

### Objeto de respuesta

La respuesta de cada consulta devuelve un objeto del siguiente tipo:

```
[
  {
    'origen': '0x2',                                                   # Dir. de origen de la respuesta
    'status': 'ACK',                                                   # Status de la respuesta
    'timestamp': '2021-09-29 09:44:26.931015',                         # Fecha y hora de recepción
    'data': ['0x1', '0x3', '0x0', '0x4', '0x51', '0x0', '0x0', '0x0'], # Mensaje completo
    'valor': 0.825,                                                    # Valor leído
    'unidad': 'v'                                                      # Unidad
  }
]
```

## Listado de funciones

### ACQ-II

| Tipo | Función        | Parámetros                                                                                                 | Descripción                                                              |
| :--: | :------------- | :--------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------- |
|  DO  | do_digital_out | **pin** (int) Pin [2-9] <br/> **mode:** (bool) Enciende/Apaga                                              | Enciende/Apaga salida digital indicada.                                  |
|  DO  | do_analog_out  | **pin** (int) Pin [0-1] <br/> **steps:** (int) Valor                                                       | Setea salida del DAC.                                                    |
|  DO  | do_pwm         | **pin** (int) Pin de salida [10-13] <br/> **duty** (int) Duty Cicle                                        | Habilita salida PWM.                                                     |
|  DO  | do_parada      | -                                                                                                          | Detiene todas las interrupciones y lecturas del equipo.                  |
|  DO  | do_soft_reset  | -                                                                                                          | Reinicia el equipo.                                                      |
| QRY  | qry_digital_in | -                                                                                                          | Devuelve estado de los pines digitales.                                  |
| QRY  | qry_analog_in  | **pin** (int) Pin [0-7]                                                                                    | Devuelve valor del pin analógico pasado por parámetro.                   |
| QRY  | qry_rtc        | -                                                                                                          | Devuelve fecha y hora del RTC del equipo.                                |
| SET  | set_modo_func  | **mode** (int) Modo de trabajo [0-4]                                                                       | Setea el modo de funcionamiento de la placa.                             |
| SET  | set_analog     | **cant_can** (int) Cantidad de canales analógicos a habilitar [1-8]                                        | Setea cantidad de canales analógicos.                                    |
| SET  | set_in_amp     | **cant_can** (int) Cantidad de canales in-Amp a habilitar                                                  | Setea cantidad de canales in-Amp.                                        |
| SET  | set_amp_in_amp | **pin** (int) Canal in-Amp a amplificar [9-12] <br/> **amp** (int) Amplificación [0-3] (int) Amplificación | Setea amplificación de canales in-Amp.                                   |
| SET  | set_rtc        | **fecha** (string) Fecha en formato dd/mm/aa. <br/> **hora** (string) Hora en formato hh:mm:ss             | Setea la fecha y hora en el RTC del equipo.                              |
|  HB  | hb_echo        | **val** (int) Valor [0-127]                                                                                | Devuelve el mismo valor pasado por parámetro. Sirve a modo de heartbeat. |

### M90E36A

| Tipo | Función    | Descripción                                  |
| :--: | :--------- | :------------------------------------------- |
| QRY  | qry_u_a    | Devuelve tensión F1                          |
| QRY  | qry_u_b    | Devuelve tensión F2                          |
| QRY  | qry_u_c    | Devuelve tensión F3                          |
| QRY  | qry_i_a    | Devuelve corriente F1                        |
| QRY  | qry_i_b    | Devuelve corriente F2                        |
| QRY  | qry_i_c    | Devuelve corriente F3                        |
| QRY  | qry_i_n1   | Devuelve corriente N                         |
| QRY  | qry_pa_a   | Devuelve potencia activa F1                  |
| QRY  | qry_pa_b   | Devuelve potencia activa F2                  |
| QRY  | qry_pa_c   | Devuelve potencia activa F3                  |
| QRY  | qry_pa_tot | Devuelve potencia activa total               |
| QRY  | qry_pr_a   | Devuelve potencia reactiva F1                |
| QRY  | qry_pr_b   | Devuelve potencia reactiva F2                |
| QRY  | qry_pr_c   | Devuelve potencia reactiva F3                |
| QRY  | qry_pr_tot | Devuelve potencia reactiva total             |
| QRY  | qry_fp_a   | Devuelve potencia factor de potencia F1      |
| QRY  | qry_fp_b   | Devuelve potencia factor de potencia F2      |
| QRY  | qry_fp_c   | Devuelve potencia factor de potencia F3      |
| QRY  | qry_fp_tot | Devuelve potencia factor de potencia total   |
| QRY  | qry_thdu_a | Devuelve distorsión armónica en tensión F1   |
| QRY  | qry_thdu_b | Devuelve distorsión armónica en tensión F2   |
| QRY  | qry_thdu_c | Devuelve distorsión armónica en tensión F3   |
| QRY  | qry_thdi_a | Devuelve distorsión armónica en corriente F1 |
| QRY  | qry_thdi_b | Devuelve distorsión armónica en corriente F2 |
| QRY  | qry_thdi_c | Devuelve distorsión armónica en corriente F3 |
| QRY  | qry_frec   | Devuelve temperatura                         |
| QRY  | qry_temp   | Devuelve frecuencia                          |
