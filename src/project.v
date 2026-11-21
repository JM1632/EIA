/*
 * Módulo superior — Subgrupo 5 (integración)
 * Copyright (c) 2026 Open Silicon Bootcamp
 * SPDX-License-Identifier: Apache-2.0
 *
 * PWM de 3 canales configurable por SPI.
 * Solo conecta los bloques entre sí y con los pines de Tiny Tapeout;
 * la única lógica propia es el flip-flop que registra period_end.
 *
 * Pines:
 *   ui_in[0] SCK · ui_in[1] MOSI · ui_in[2] CS_n · ui_in[7:3] sin uso
 *   uo_out[0..2] PWM0..2 · uo_out[3] MISO · uo_out[4] pulso de periodo
 *   uo_out[7:5] en 0 · uio: sin uso (todos como entrada)
 */

`default_nettype none

module tt_um_jm1632_pwm_spi (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // ---------------------------------------------------------------
  // Cables internos
  // ---------------------------------------------------------------

  // Sincronizador -> esclavo SPI
  wire mosi, csn, sck_rise, sck_fall;

  // Esclavo SPI <-> banco de registros
  wire [6:0] addr;
  wire [7:0] wdata, rdata;
  wire       wr_en;
  wire       miso;

  // Banco de registros -> núcleo PWM
  wire [2:0]  ch_en, ch_inv;
  wire [15:0] presc;
  wire [7:0]  duty0, duty1, duty2;

  // Prescaler -> contador -> canales
  wire       tick;
  wire [7:0] cnt;
  wire       period_end;

  // Canales -> pines
  wire pwm0, pwm1, pwm2;

  // ---------------------------------------------------------------
  // Interfaz y configuración
  // ---------------------------------------------------------------

  synchronizer u_sync (
      .clk     (clk),
      .rst_n   (rst_n),
      .sck_in  (ui_in[0]),
      .mosi_in (ui_in[1]),
      .csn_in  (ui_in[2]),
      .mosi    (mosi),
      .csn     (csn),
      .sck_rise(sck_rise),
      .sck_fall(sck_fall)
  );

  spi_slave u_spi (
      .clk     (clk),
      .rst_n   (rst_n),
      .csn     (csn),
      .mosi    (mosi),
      .sck_rise(sck_rise),
      .sck_fall(sck_fall),
      .rdata   (rdata),
      .addr    (addr),
      .wdata   (wdata),
      .wr_en   (wr_en),
      .miso    (miso)
  );

  reg_bank u_regs (
      .clk   (clk),
      .rst_n (rst_n),
      .addr  (addr),
      .wdata (wdata),
      .wr_en (wr_en),
      .rdata (rdata),
      .ch_en (ch_en),
      .ch_inv(ch_inv),
      .presc (presc),
      .duty0 (duty0),
      .duty1 (duty1),
      .duty2 (duty2)
  );

  // ---------------------------------------------------------------
  // Núcleo PWM
  // ---------------------------------------------------------------

  prescaler u_presc (
      .clk  (clk),
      .rst_n(rst_n),
      .presc(presc),
      .tick (tick)
  );

  pwm_counter u_cnt (
      .clk       (clk),
      .rst_n     (rst_n),
      .tick      (tick),
      .cnt       (cnt),
      .period_end(period_end)
  );

  pwm_channel u_ch0 (
      .clk       (clk),
      .rst_n     (rst_n),
      .cnt       (cnt),
      .period_end(period_end),
      .duty_in   (duty0),
      .en        (ch_en[0]),
      .inv       (ch_inv[0]),
      .pwm_out   (pwm0)
  );

  pwm_channel u_ch1 (
      .clk       (clk),
      .rst_n     (rst_n),
      .cnt       (cnt),
      .period_end(period_end),
      .duty_in   (duty1),
      .en        (ch_en[1]),
      .inv       (ch_inv[1]),
      .pwm_out   (pwm1)
  );

  pwm_channel u_ch2 (
      .clk       (clk),
      .rst_n     (rst_n),
      .cnt       (cnt),
      .period_end(period_end),
      .duty_in   (duty2),
      .en        (ch_en[2]),
      .inv       (ch_inv[2]),
      .pwm_out   (pwm2)
  );

  // ---------------------------------------------------------------
  // Salidas
  // ---------------------------------------------------------------

  // period_end registrado para que el pin tenga una señal limpia
  reg period_end_q;
  always @(posedge clk) begin
    if (!rst_n)
      period_end_q <= 1'b0;
    else
      period_end_q <= period_end;
  end

  assign uo_out  = {3'b000, period_end_q, miso, pwm2, pwm1, pwm0};
  assign uio_out = 8'd0;
  assign uio_oe  = 8'd0;

  // Entradas sin uso
  wire _unused = &{ena, ui_in[7:3], uio_in, 1'b0};

endmodule
