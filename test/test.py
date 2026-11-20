# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)

    # Durante el reset el contador debe estar en 0
    assert int(dut.uio_out.value) == 0
    assert int(dut.uio_oe.value) == 0xFF

    dut._log.info("Test lógica combinacional: uo_out = ~ui_in")
    for val in [0x00, 0xFF, 0x55, 0xA5, 20]:
        dut.ui_in.value = val
        await Timer(1, unit="us")
        assert int(dut.uo_out.value) == (~val & 0xFF), f"ui_in={val:#04x}"

    dut._log.info("Test contador en uio_out")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    start = int(dut.uio_out.value)
    await ClockCycles(dut.clk, 5)
    assert int(dut.uio_out.value) == (start + 5) & 0xFF

    # El contador debe dar la vuelta después de 256 ciclos
    await ClockCycles(dut.clk, 256)
    assert int(dut.uio_out.value) == (start + 5) & 0xFF

    dut._log.info("Todo OK")
