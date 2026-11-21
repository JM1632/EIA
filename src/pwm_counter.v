/*
 * Contador del PWM — Subgrupo 1
 * SPDX-License-Identifier: Apache-2.0
 *
 * Cuenta de 0 a 255 avanzando solo con tick, y vuelve a 0.
 * period_end vale 1 durante un ciclo cuando cnt = 255 y llega tick.
 *
 * ESQUELETO: los puertos son el contrato acordado, no cambiarlos sin
 * acordarlo con todo el equipo. Reemplazar los assign por la lógica real.
 */

`default_nettype none

module pwm_counter (
    input  wire       clk,         // Reloj del sistema
    input  wire       rst_n,       // Reset activo en bajo
    input  wire       tick,        // Avanza un paso ahora
    output wire [7:0] cnt,         // Posición dentro del periodo (0-255)
    output wire       period_end   // Pulso de un ciclo: terminó un periodo
);

  // TODO: implementar
  assign cnt        = 8'd0;
  assign period_end = 1'b0;

  // Quitar de aquí cada entrada a medida que se use
  wire _unused = &{clk, rst_n, tick, 1'b0};

endmodule
