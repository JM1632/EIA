<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

Es un diseño de prueba sencillo para comprobar que la plantilla de Tiny Tapeout funciona.

- **Lógica combinacional:** las salidas dedicadas `uo_out` son las entradas `ui_in` invertidas (`uo_out = ~ui_in`).
- **Lógica secuencial:** un contador de 8 bits que aumenta en cada flanco de subida de `clk` y sale por los pines
  bidireccionales `uio_out`, que están configurados como salidas (`uio_oe = 8'hFF`). El reset (`rst_n`) es síncrono
  y activo en bajo, y pone el contador en 0.

## How to test

1. Mantén `rst_n` en bajo durante algunos ciclos de reloj: `uio[7:0]` debe quedar en 0.
2. Pon cualquier valor en `ui[7:0]` y comprueba que `uo[7:0]` muestra el valor invertido bit a bit.
3. Suelta el reset (`rst_n` en alto): `uio[7:0]` cuenta de 0 a 255 y vuelve a empezar, un paso por ciclo de reloj.
   Con un reloj lento (por ejemplo, unos pocos Hz) se puede ver contar con LEDs.

## External hardware

Ninguno. Opcionalmente, interruptores en las entradas y LEDs en las salidas.
