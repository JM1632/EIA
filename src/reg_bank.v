/*
 * Banco de registros — Subgrupo 3
 * SPDX-License-Identifier: Apache-2.0
 *
 * Mapa de registros (todos en 0 tras el reset, salvo ID):
 *   0x00 CTRL     bits 0-2: habilitar canal 0-2 · bits 3-5: invertir canal 0-2
 *   0x01 PRESC_L  byte bajo del prescaler
 *   0x02 PRESC_H  byte alto del prescaler
 *   0x03 DUTY0
 *   0x04 DUTY1
 *   0x05 DUTY2
 *   0x06 ID       solo lectura, constante 0xA5
 * Escritura: con wr_en = 1 en el registro que indica addr.
 * Lectura: rdata es combinacional según addr; 0 en direcciones libres.
 *
 * ESQUELETO: los puertos son el contrato acordado, no cambiarlos sin
 * acordarlo con todo el equipo. Reemplazar los assign por la lógica real.
 */

`default_nettype none

module reg_bank (
    input  wire        clk,     // Reloj del sistema
    input  wire        rst_n,   // Reset activo en bajo
    input  wire [6:0]  addr,    // Registro que se escribe o se lee
    input  wire [7:0]  wdata,   // Valor a escribir
    input  wire        wr_en,   // Pulso de un ciclo: escribe ahora
    output wire [7:0]  rdata,   // Contenido del registro que indica addr
    output wire [2:0]  ch_en,   // CTRL bits 0-2: 1 = canal encendido
    output wire [2:0]  ch_inv,  // CTRL bits 3-5: 1 = polaridad invertida
    output wire [15:0] presc,   // {PRESC_H, PRESC_L}
    output wire [7:0]  duty0,   // DUTY0
    output wire [7:0]  duty1,   // DUTY1
    output wire [7:0]  duty2    // DUTY2
);

  // TODO: implementar
  assign rdata  = 8'd0;
  assign ch_en  = 3'd0;
  assign ch_inv = 3'd0;
  assign presc  = 16'd0;
  assign duty0  = 8'd0;
  assign duty1  = 8'd0;
  assign duty2  = 8'd0;

  // Quitar de aquí cada entrada a medida que se use
  wire _unused = &{clk, rst_n, addr, wdata, wr_en, 1'b0};

endmodule
