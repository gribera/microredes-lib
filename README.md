# microredes-lib
## Listado de funciones

| Tipo | Función   |      Parámetros      |  Descripción |
|:--:|:----------|:-------------|:------|
| DO | doDigitalOut | **pin** (int) Pin [2-9] <br/> **mode:** (bool) Enciende/Apaga | Enciende/Apaga salida digital indicada. |
| DO | doAnalogOut | **pin** (int) Pin [0-1] <br/> **steps:** (int) Valor | Setea salida del DAC. |
| DO | doPwm | **pin** (int) Pin de salida [10-13] <br/> **duty** (int) Duty Cicle | Habilita salida PWM.
| DO | doParada | - | Detiene todas las interrupciones y lecturas del equipo. |
| DO | doSoftReset | - | Reinicia el equipo. |
| QRY | qryDigitalIn | - | Recupera estado de los pines digitales. |
| QRY | qryAnalogIn | **pin** (int) Pin [0-7] | Recupera valor del pin analógico pasado por parámetro. |
| QRY | qryRTC | - | Recupera fecha y hora del RTC del equipo. |
| SET | setModoFunc | **mode** (int) Modo de trabajo [0-4] | Setea el modo de funcionamiento de la placa. |
| SET | setAnalog | **cantCan** (int) Cantidad de canales analógicos a habilitar [1-8] | Setea cantidad de canales analógicos. |
| SET | setInAmp | **cantCan** (int) Cantidad de canales in-Amp a habilitar | Setea cantidad de canales in-Amp. |
| SET | setAmpInAmp | **pin** (int) Canal in-Amp a amplificar [9-12] <br/> **amp** (int) Amplificación [0-3] (int) Amplificación| Setea amplificación de canales in-Amp. |
| SET | setRTC | **fecha** (string) Fecha en formato dd/mm/aa. <br/> **hora** (string) Hora en formato hh:mm:ss | Setea la fecha y hora en el RTC del equipo. |
| HB | hbEcho | **val** (int) Valor [0-127] | Devuelve el mismo valor pasado por parámetro. Sirve a modo de heartbeat. |