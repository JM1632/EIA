/*
 * Esclavo SPI — Subgrupo 4
 * SPDX-License-Identifier: Apache-2.0
 *
 * SPI modo 0, tramas de 16 bits, MSB primero.
 *   Byte 1: bit 7 = R/W (1 = escribir), bits 6-0 = dirección.
 *   Byte 2: dato (escritura) o respuesta por MISO (lectura).
 * En la subida 8 se capturan is_write y addr; en la subida 16, si es
 * escritura, se copia wdata y se genera wr_en durante un ciclo.
 * MISO: carga rdata en la bajada tras el bit 8; vale 0 si csn = 1.
 *
 * ESQUELETO: los puertos son el contrato acordado, no cambiarlos sin
 * acordarlo con todo el equipo. Reemplazar los assign por la lógica real.
 */

`default_nettype none

module spi_slave (
    input  wire       clk,       // Reloj del sistema
    input  wire       rst_n,     // Reset activo en bajo
    input  wire       csn,       // 0 = trama en curso; 1 = reinicia el contador
    input  wire       mosi,      // Bit de dato del maestro
    input  wire       sck_rise,  // «Lee MOSI ahora»
    input  wire       sck_fall,  // «Saca el siguiente bit por MISO ahora»
    input  wire [7:0] rdata,     // Valor del registro que indica addr
    output wire [6:0] addr,      // Registro que se quiere tocar
    output wire [7:0] wdata,     // Valor que se quiere escribir
    output wire       wr_en,     // Pulso de un ciclo: escribe wdata en addr
    output wire       miso       // Bit hacia el maestro (pin uo_out[3])
);

  // TODO: implementar
  assign addr  = 7'd0;
  assign wdata = 8'd0;
  assign wr_en = 1'b0;

  // PROVISIONAL: MISO devuelve MOSI mientras CS_n = 0 (eco). Existe solo
  // para que el chip tenga un camino real entre pines y el flujo GDS no
  // falle por pines desconectados. Reemplazar por el registro de salida.
  assign miso  = mosi & ~csn;

  // Quitar de aquí cada entrada a medida que se use
  wire _unused = &{clk, rst_n, sck_rise, sck_fall, rdata, 1'b0};

endmodule
