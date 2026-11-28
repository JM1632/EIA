`timescale 1ns / 1ps
/*
    Banco de resistros - Subgrupo 3
    SPDX-License-Identifier: Apache-2.0
    
    Mapa de registros (todos en 0 tras el reset, salvo ID):
        0x00 CTRL     bits 0-2: habilitar canal 0-2 . bits 3-5: invertir canal 0-2
        0x01 PRESC_L  byte bajo del prescaler
        0x02 PRESC_H  byte alto del prescaler
        0x03 DUTY0
        0x04 DUTY1
        0x05 DUTY2
        0x06 ID       solo lectura, constante 0xA5
    Escritura: con wr_en = 1 en el registro que indica addr.
    Lectura: rdata es combinacional seg[un addr; 0 en direcciones libres.
    
    ESQUELETO: los puertos son el contrato acordado, no cambiarlos sin 
    acordarlo con todo el equipo. Reemplazar los assign por la lógica real.
*/

//`default_nettype none

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
    
    // Constants definition
    // We use this to set up the addresses with their names, allowing for a better readibility
    // of the code!
    /////////////////////////////////////////////////////////////////////////////////////////////////
    localparam [7:0] CTRL    = 8'h00; 
    localparam [7:0] PRESC_L = 8'h01; 
    localparam [7:0] PRESC_H = 8'h02; 
    localparam [7:0] DUTY0   = 8'h03; 
    localparam [7:0] DUTY1   = 8'h04; 
    localparam [7:0] DUTY2   = 8'h05; 
    localparam [7:0] ID      = 8'h06; 
    localparam [7:0] ID_VAL  = 8'hA5;
    
    // Define internal signals used by the module
    // These signals might be both wires and registers so keep them all under here!
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    reg  [7:0] rdata_reg   = 8'h00;
    reg  [7:0] ctrl_reg    = 8'h00;
    reg  [7:0] presc_l_reg = 8'h00;
    reg  [7:0] presc_h_reg = 8'h00;
    reg  [7:0] duty0_reg   = 8'h00;
    reg  [7:0] duty1_reg   = 8'h00;
    reg  [7:0] duty2_reg   = 8'h00;
    
    // Register Bank access and control actions
    // With this piece of code we establish a MUX that executes certain actions according to 
    // the value present in the 'addr' input
    /////////////////////////////////////////////////////////////////////////////////////////////////
    always @(posedge clk or negedge rst_n) begin
        // Asynchronous active low reset
        if (!rst_n) begin
            // since the reset is activated, every signal must return to the original value
            // which should be zeros!
            // rdata_reg   <= 8'h00; // rdata_reg must be left out of here else I'm sure we'll get a multi driven net error!
            ctrl_reg    <= 3'h00;
            presc_l_reg <= 8'h00;
            presc_h_reg <= 8'h00;
            duty0_reg   <= 8'h00;
            duty1_reg   <= 8'h00;
            duty2_reg   <= 8'h00;
        end else if (wr_en) begin
            // Now that we are not resetting the system, just do what it should
            // allow for a register change only if the wr_en signal is asserted!
            case (addr)
                CTRL:     ctrl_reg     <= wdata;
                PRESC_L:  presc_l_reg  <= wdata;
                PRESC_H:  presc_h_reg  <= wdata;
                DUTY0:    duty0_reg    <= wdata;
                DUTY1:    duty1_reg    <= wdata;
                DUTY2:    duty2_reg    <= wdata;
                default: ; // Do nothing!
            endcase
        end
    end
    
    // Read Multiplexer
    // Based on combinational logic
    // Data is always shown without a read command. For any unlisted Address, return 0.
    /////////////////////////////////////////////////////////////////////////////////////////////////
    always @(*) begin
        // Another multiplexer, but this time it modifies the rdata signal 
        case (addr)
            CTRL:     rdata_reg  <= ctrl_reg;
            PRESC_L:  rdata_reg  <= presc_l_reg;
            PRESC_H:  rdata_reg  <= presc_h_reg;
            DUTY0:    rdata_reg  <= duty0_reg;
            DUTY1:    rdata_reg  <= duty1_reg;
            DUTY2:    rdata_reg  <= duty2_reg;
            ID:       rdata_reg  <= ID_VAL; // Remember to include the identifier R/O signal!
            default:  rdata_reg  <= 8'h00; // Show zeros when a differente Address is called
        endcase
    end
    
    // Output assignment
    /////////////////////////////////////////////////////////////////////////////////////////////////
    assign rdata  = rdata_reg;
    assign ch_en  = ctrl_reg[2:0];
    assign ch_inv = ctrl_reg[5:3];
    assign presc  = {presc_h_reg, presc_l_reg};
    assign duty0  = duty0_reg;
    assign duty1  = duty1_reg;
    assign duty2  = duty2_reg;
    
endmodule
