/*
 * Canal PWM — Subgrupo 2 (se instancia tres veces)
 * SPDX-License-Identifier: Apache-2.0
 *
 * - Buffer del duty: copia duty_in solo cuando llega period_end.
 * - Onda: 1 mientras cnt < buffer.
 * - Polaridad: XOR con inv.
 * - Habilitación: con en = 0 la salida vale inv (nivel de reposo).
 * - Salida registrada en un flip-flop (sin glitches).
 *
 * ESQUELETO: los puertos son el contrato acordado, no cambiarlos sin
 * acordarlo con todo el equipo. Reemplazar los assign por la lógica real.
 */

`default_nettype none

module pwm_channel (
    input  wire       clk,         // Reloj del sistema
    input  wire       rst_n,       // Reset activo en bajo
    input  wire [7:0] cnt,         // Posición dentro del periodo
    input  wire       period_end,  // Momento de cargar el duty nuevo
    input  wire [7:0] duty_in,     // Duty pedido (DUTY0, 1 o 2)
    input  wire       en,          // 1 = canal encendido
    input  wire       inv,         // 1 = polaridad invertida
    output wire       pwm_out      // Onda PWM (pin uo_out[0], [1] o [2])
);

  // TODO: implementar
  assign pwm_out = 1'b0;

  // Quitar de aquí cada entrada a medida que se use
  wire _unused = &{clk, rst_n, cnt, period_end, duty_in, en, inv, 1'b0};

endmodule
