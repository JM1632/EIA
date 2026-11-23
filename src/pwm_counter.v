
/*
 * Contador del PWM — Subgrupo 1
 * SPDX-License-Identifier: Apache-2.0
 *
 * Cuenta de 0 a 255 avanzando solo con tick, y vuelve a 0.
 * period_end vale 1 cuando cnt = 255 y llega tick.
 */

`default_nettype none

module pwm_counter (
    input  wire       clk,         // Reloj del sistema
    input  wire       rst_n,       // Reset activo en bajo
    input  wire       tick,        // Avanza un paso ahora
    output wire [7:0] cnt,         // Posicion dentro del periodo (0-255)
    output wire       period_end   // Pulso de fin de periodo
);

    // Registro interno de 8 bits
    reg [7:0] count_reg;

    // Conexion del registro con la salida
    assign cnt = count_reg;

    // Indicador de fin de periodo
    assign period_end = (count_reg == 8'd255) && tick;

    // Logica secuencial del contador
    always @(posedge clk or negedge rst_n) begin

        if (!rst_n) begin
            count_reg <= 8'd0;
        end

        else if (tick) begin
            count_reg <= count_reg + 8'd1;
        end

    end

endmodule

`default_nettype wire
