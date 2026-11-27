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

  reg [3:0] b_counter;  // internal bit counter
  reg [7:0] in_reg;     // 8 bit register for MOSI
  reg [7:0] out_reg;    // 8 bit register for MISO
  wire is_write;

  always @(posedge clk  or rst_n) begin
    
    if (!rst_n)begin      //reset internal registers on reset
      b_counter <= 4'b0000;
      in_reg <= 8'b0000_0000;
      assign is_write <= 0;
    end
    
    if (csn) begin
      b_counter <= 4'b0000;
    end

    if(!csn)begin
        b_counter <= b_counter + 4'b0001;
    end


    if (sck_rise) begin
      in_reg <= in_reg << 1 + mosi;

      if(b_counter == 4d'7)begin    // Encabezado: assign addres & is_write
        assign is_write <= in_reg[7];
        assign addr <= in_reg[6:0]
        in_reg <= 8b'0000_0000;
      end

      if(b_counter == 4'd15)begin   //Dato: assign wdata & wr_en
        if(is_write) begin
          assign wdata <= in_reg;
          assign wr_en <= 1;
        end
        in_reg <= 8b'0000_0000;
      end
    end

    if(sck_fall) begin             // Registro de salida: saca datos por miso
      if(b_counter == 4d'7)begin 
        out_reg <= rdata;
        assign miso <= out_reg[0]
      end
      if(b_counter >= 4d'7) begin
        out_reg <= out_reg >> 1;
        assign miso <= out_reg[0]
      end
    end
  end


endmodule
