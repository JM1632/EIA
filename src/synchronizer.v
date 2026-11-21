/*
 * Sincronizador — Subgrupo 4
 * SPDX-License-Identifier: Apache-2.0
 *
 * Alinea SCK, MOSI y CS_n al reloj del chip (2 flip-flops por señal)
 * y genera un pulso de un ciclo cuando SCK sube (sck_rise) o baja (sck_fall).
 * Tras el reset, los flip-flops de CS_n valen 1 y los demás 0.
 *
 * ESQUELETO: los puertos son el contrato acordado, no cambiarlos sin
 * acordarlo con todo el equipo. Reemplazar los assign por la lógica real.
 */

`default_nettype none

module synchronizer (
    input  wire clk,       // Reloj del sistema
    input  wire rst_n,     // Reset activo en bajo
    input  wire sck_in,    // SCK crudo   (pin ui_in[0])
    input  wire mosi_in,   // MOSI crudo  (pin ui_in[1])
    input  wire csn_in,    // CS_n crudo  (pin ui_in[2])
    output wire mosi,      // MOSI sincronizado
    output wire csn,       // CS_n sincronizado; 1 tras el reset
    output wire sck_rise,  // Pulso de un ciclo: SCK acaba de subir
    output wire sck_fall   // Pulso de un ciclo: SCK acaba de bajar
);

  // TODO: implementar
  //
  // PROVISIONAL: un solo flip-flop para MOSI y CS_n (en vez de dos) y sin
  // detector de flancos. Existe solo para que el chip tenga un camino real
  // entre pines y el flujo GDS no falle por pines desconectados. Reemplazar.
  reg mosi_q, csn_q;
  always @(posedge clk) begin
    if (!rst_n) begin
      mosi_q <= 1'b0;
      csn_q  <= 1'b1;  // CS inactivo tras el reset
    end else begin
      mosi_q <= mosi_in;
      csn_q  <= csn_in;
    end
  end

  assign mosi     = mosi_q;
  assign csn      = csn_q;
  assign sck_rise = 1'b0;
  assign sck_fall = 1'b0;

  // Quitar de aquí cada entrada a medida que se use
  wire _unused = &{sck_in, 1'b0};

endmodule
