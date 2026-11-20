/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// Diseño de prueba sencillo para verificar la plantilla de Tiny Tapeout:
//  - uo_out  = ui_in invertido (lógica combinacional)
//  - uio_out = contador de 8 bits (lógica secuencial con clk y rst_n)
//  - uio_oe  = 8'hFF (todos los uio como salidas)
module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  reg [7:0] counter;

  always @(posedge clk) begin
    if (!rst_n)
      counter <= 8'd0;
    else
      counter <= counter + 8'd1;
  end

  assign uo_out  = ~ui_in;
  assign uio_out = counter;
  assign uio_oe  = 8'hFF;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in, 1'b0};

endmodule
