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

  // Internal registers
  reg [4:0] b_counter;  // internal bit counter
  reg [7:0] in_reg;     // 8 bit register for MOSI
  reg [7:0] out_reg;    // 8 bit register for MISO
  reg is_write;         // Is write 

  // auxiliar registers for outputs in Always block
  reg [6:0] addr_r;     // address
  reg [7:0] wdata_r;    // Write data
  reg wr_en_r;          // write data enable

  // output wire assignmets
  assign addr = addr_r;
  assign wdata = wdata_r;
  assign wr_en = wr_en_r;
  assign miso = ~csn & out_reg[7];

  always @(posedge clk  or negedge rst_n) begin
    
    if (!rst_n)begin      //reset internal registers on reset
      b_counter <= 5'b0_0000;
      in_reg <= 8'b0000_0000;
      out_reg <= 8'b0000_0000;
      is_write <= 0;
    end else begin
      wr_en_r <= 1'b0;

      if (csn) begin
        b_counter <= 5'b0_0000;
      end

      else if (sck_rise) begin
          b_counter <= b_counter + 5'b0_0001;
          in_reg <= {in_reg[6:0], mosi};

          if(b_counter == 5'd7)begin    // Encabezado: assign addres & is_write
            is_write <= in_reg[6];
            addr_r <= {in_reg[5:0], mosi};  
          end

          if(b_counter == 5'd15)begin   //Dato: assign wdata & wr_en
            if(is_write) begin
              wdata_r <= {in_reg[6:0], mosi};
              wr_en_r <= 1'b1;
            end
          end 
      end

      if(sck_fall) begin             // Registro de salida: saca datos por miso
        if (b_counter == 5'd8) begin
          out_reg <= rdata;
        end else if (b_counter > 5'd8 && b_counter < 5'd16)begin
          out_reg <= out_reg << 1;
        end            
      end
      

    end
    
    
  end


endmodule
