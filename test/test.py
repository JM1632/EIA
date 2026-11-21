# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# Test del chip completo (Subgrupo 5).
# Por ahora solo comprueba el estado tras el reset, que debe cumplirse tanto
# con los esqueletos como con el diseño terminado. Aquí irán las pruebas de
# integración por SPI (spi_write / spi_read).

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

# Bits de ui_in
SCK = 1 << 0
MOSI = 1 << 1
CSN = 1 << 2


@cocotb.test()
async def test_reset_state(dut):
    """Tras el reset: canales apagados, MISO en 0 y uio como entradas."""

    # clk a 10 MHz (periodo de 100 ns), igual que clock_hz en info.yaml
    clock = Clock(dut.clk, 100, unit="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = CSN  # SPI en reposo: SCK = 0, CS_n = 1
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)

    assert int(dut.uio_oe.value) == 0x00, "uio debe quedar como entrada"
    assert int(dut.uio_out.value) == 0x00
    assert int(dut.uo_out.value) & 0b1110_0111 == 0, \
        "PWM0-2, MISO y bits 5-7 deben estar en 0 tras el reset"
