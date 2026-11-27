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

  reg [7:0] ctrl;
  reg [7:0] presc_l;
  reg [7:0] presc_h;
  reg [7:0] duty0_reg;

  always @(posedge clk or negedge rst_n) begin
      if (!rst_n) begin
          ctrl    <= 8'h00;
          presc_l <= 8'h00;
          presc_h <= 8'h00;
          duty0_reg   <= 8'h00;
          duty1   <= 8'h00;
          duty2   <= 8'h00;
      end else if (wr_en) begin
          case (addr)
              7'h00: ctrl    <= wdata;
              7'h01: presc_l <= wdata;
              7'h02: presc_h <= wdata;
              7'h03: duty0_reg   <= wdata;
              7'h04: duty1   <= wdata;
              7'h05: duty2   <= wdata;
              //default: ; // do nothing
          endcase
      end
  end

  always @(*) begin
      case (addr)
          7'h00:   rdata = ctrl;
          7'h01:   rdata = presc_l;
          7'h02:   rdata = presc_h;
          7'h03:   rdata = duty0;
          7'h04:   rdata = duty1;
          7'h05:   rdata = duty2;
          7'h06:   rdata = 8'hA5;     // ID
          default: rdata = 8'h00; // Si piden cualquier otro número, muestra 0
      endcase
  end

  assign ch_en  = ctrl[2:0];
  assign ch_inv = ctrl[5:3];
  assign presc  = {presc_h, presc_l};
  assign duty0 = duty0_reg;

  // // TODO: implementar
  // assign rdata  = 8'd0;
  // assign ch_en  = 3'd0;
  // assign ch_inv = 3'd0;
  // assign presc  = 16'd0;
  // assign duty0  = 8'd0;
  // assign duty1  = 8'd0;
  // assign duty2  = 8'd0;

  // // Quitar de aquí cada entrada a medida que se use
  // wire _unused = &{clk, rst_n, addr, wdata, wr_en, 1'b0};

endmodule
