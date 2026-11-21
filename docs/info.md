<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

El chip genera tres señales PWM independientes. El duty, la frecuencia, el encendido y la polaridad de cada canal
se configuran desde un microcontrolador por SPI (modo 0, tramas de 16 bits).

- **Interfaz y configuración:** un sincronizador alinea SCK, MOSI y CS_n al reloj del chip; el esclavo SPI
  convierte cada trama en una orden (dirección, dato, lectura o escritura) y el banco de registros la guarda.
- **Núcleo PWM:** un prescaler fija la duración de cada paso, un contador recorre de 0 a 255 y cada canal pone
  su salida en 1 mientras la cuenta sea menor que su duty.

### Mapa de registros

| Dir. | Nombre  | Contenido |
|------|---------|-----------|
| 0x00 | CTRL    | Bits 0-2: habilitar canal 0-2 · Bits 3-5: invertir canal 0-2 |
| 0x01 | PRESC_L | Byte bajo del prescaler |
| 0x02 | PRESC_H | Byte alto del prescaler |
| 0x03 | DUTY0   | Duty del canal 0 (0-255) |
| 0x04 | DUTY1   | Duty del canal 1 (0-255) |
| 0x05 | DUTY2   | Duty del canal 2 (0-255) |
| 0x06 | ID      | Solo lectura, 0xA5 |

Frecuencia del PWM: `clk / ((PRESC + 1) × 256)`.

## How to test

1. Conecta un microcontrolador por SPI modo 0: SCK a `ui[0]`, MOSI a `ui[1]`, CS_n a `ui[2]` y MISO a `uo[3]`.
   SCK debe ser como mucho `clk / 8` (1 MHz con `clk` a 10 MHz).
2. Lee el registro ID (primer byte `0x06`, bit 7 = 0): debe responder `0xA5`.
3. Escribe el prescaler, los duty y por último CTRL para encender los canales. Para escribir, pon el bit 7 del
   primer byte en 1, por ejemplo `0x83 0x80` pone DUTY0 = 128 (50 %).
4. Observa las ondas en `uo[0]`-`uo[2]` y el pulso de fin de periodo en `uo[4]`.

## External hardware

Un microcontrolador como maestro SPI (por ejemplo, el RP2040 de la placa de Tiny Tapeout) y, opcionalmente,
LEDs, servos o drivers de motor en las salidas PWM.
