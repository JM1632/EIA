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
 * Los puertos son el contrato acordado: no cambiarlos sin acordarlo
 * con todo el equipo.
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

  // Registros internos
  reg [4:0] b_counter;  // bits recibidos en la trama (0 a 16)
  reg [7:0] in_reg;  // 8 bit register for MOSI
    reg [7:0] out_reg;  // 8 bit register for MISO
  reg is_write;   // 1 = escritura, 0 = lectura

  // Registros auxiliares para las salidas
  reg [6:0] addr_r; // dirección
  reg [7:0] wdata_r; // dato a escribir
  reg wr_en_r; // escritura enable

  // Asignación de salidas
  assign addr  = addr_r;
  assign wdata = wdata_r;
  assign wr_en = wr_en_r;
  assign miso = ~csn & out_reg[7];

  // in_reg[7] - marca para el linter
  wire _unused = &{in_reg[7], 1'b0};

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      b_counter <= 5'd0;
      in_reg <= 8'd0;
      out_reg <= 8'd0;
      is_write <= 1'b0;
      addr_r <= 7'd0;
      wdata_r <= 8'd0;
      wr_en_r <= 1'b0;
    end else begin
      wr_en_r <= 1'b0; // wr_en dura un solo ciclo

      if (csn) begin // reinicia contador y salida
        b_counter <= 5'd0;
        out_reg <= 8'd0;
      end else begin

        if (sck_rise && b_counter != 5'd16) begin  // tope
          b_counter <= b_counter + 5'd1;
          in_reg <= {in_reg[6:0], mosi};

        if (b_counter == 5'd7) begin
            is_write <= in_reg[6];
            addr_r <= {in_reg[5:0], mosi};
          end

        if (b_counter == 5'd15 && is_write) begin // dato: assign wdata & wr_en
            wdata_r <= {in_reg[6:0], mosi};
            wr_en_r <= 1'b1;
          end
        end

        if (sck_fall) begin // salida MISO
          if (b_counter == 5'd8)
            out_reg <= rdata;
          else if (b_counter > 5'd8 && b_counter < 5'd16)
            out_reg <= out_reg << 1;
        end

      end
    end
  end

endmodule

