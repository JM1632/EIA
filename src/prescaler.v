/*
 * Prescaler — Subgrupo 1
 * SPDX-License-Identifier: Apache-2.0
 *
 * Genera un pulso tick de un ciclo cada presc + 1 ciclos de clk.
 * Usar comparación >= (no ==) para tolerar que presc baje en marcha.
 * Con presc = 0, tick vale 1 siempre.
 *
 * ESQUELETO: los puertos son el contrato acordado, no cambiarlos sin
 * acordarlo con todo el equipo. Reemplazar los assign por la lógica real.
 */

`default_nettype none

module prescaler (
    input  wire        clk,    // Reloj del sistema
    input  wire        rst_n,  // Reset activo en bajo
    input  wire [15:0] presc,  // Un tick cada presc + 1 ciclos
    output wire        tick    // Pulso de un ciclo: avanza un paso ahora
);

  // TODO: implementar
  assign tick = 1'b0;

  // Quitar de aquí cada entrada a medida que se use
  wire _unused = &{clk, rst_n, presc, 1'b0};

endmodule
