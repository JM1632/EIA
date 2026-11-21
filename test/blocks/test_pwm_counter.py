# SPDX-License-Identifier: Apache-2.0
#
# Test del contador del PWM (Subgrupo 1)
#
# Contrato:
#   - cnt avanza +1 solo en los ciclos en que tick = 1, y de 255 vuelve a 0.
#   - period_end = 1 cuando cnt = 255 Y tick = 1 (combinacional: en el mismo
#     ciclo, justo antes de volver a 0).
#
# Las entradas se cambian y las salidas se leen en el flanco de BAJADA de clk.

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, Timer

CLK_NS = 100  # 10 MHz


async def iniciar(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.tick.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1


async def poner_tick(dut, valor):
    """Pone tick y espera 1 ns para que period_end (combinacional) se actualice."""
    dut.tick.value = valor
    await Timer(1, unit="ns")


@cocotb.test()
async def test_reset(dut):
    """Tras el reset cnt = 0 y period_end = 0."""
    await iniciar(dut)
    await FallingEdge(dut.clk)
    assert int(dut.cnt.value) == 0, "cnt debe valer 0 tras el reset"
    assert int(dut.period_end.value) == 0, "period_end debe valer 0 tras el reset"


@cocotb.test()
async def test_sin_tick_no_avanza(dut):
    """Si tick = 0, la cuenta no cambia."""
    await iniciar(dut)
    for _ in range(20):
        await FallingEdge(dut.clk)
        assert int(dut.cnt.value) == 0, "con tick = 0 la cuenta no debe avanzar"
        assert int(dut.period_end.value) == 0


@cocotb.test()
async def test_cuenta_completa(dut):
    """Con tick = 1 siempre: 0, 1, ..., 255, 0, ... y un period_end por vuelta."""
    await iniciar(dut)
    await poner_tick(dut, 1)
    esperado = 0
    vueltas = 0
    for _ in range(256 * 3):
        cnt = int(dut.cnt.value)
        pe = int(dut.period_end.value)
        assert cnt == esperado, f"se esperaba cnt = {esperado}, se leyó {cnt}"
        assert pe == int(cnt == 255), f"cnt = {cnt}: period_end debe ser {int(cnt == 255)}, se leyó {pe}"
        vueltas += pe
        esperado = (esperado + 1) % 256
        await FallingEdge(dut.clk)
        await Timer(1, unit="ns")
    assert vueltas == 3, f"en 768 ticks debe haber 3 period_end, hubo {vueltas}"


@cocotb.test()
async def test_255_sin_tick(dut):
    """En 255 sin tick: la cuenta espera y period_end NO se activa."""
    await iniciar(dut)
    await poner_tick(dut, 1)
    while int(dut.cnt.value) != 255:
        await FallingEdge(dut.clk)
    await poner_tick(dut, 0)
    for _ in range(10):
        assert int(dut.cnt.value) == 255, "sin tick la cuenta debe quedarse en 255"
        assert int(dut.period_end.value) == 0, "period_end solo vale 1 si cnt = 255 Y tick = 1"
        await FallingEdge(dut.clk)
        await Timer(1, unit="ns")
    await poner_tick(dut, 1)
    assert int(dut.period_end.value) == 1, "con cnt = 255 y tick = 1, period_end debe valer 1"
    await FallingEdge(dut.clk)
    assert int(dut.cnt.value) == 0, "después de 255 la cuenta vuelve a 0"


@cocotb.test()
async def test_tick_aleatorio(dut):
    """tick aleatorio, comparado ciclo a ciclo con un modelo de referencia."""
    random.seed(1234)
    await iniciar(dut)
    modelo = 0
    for i in range(3000):
        cnt = int(dut.cnt.value)
        assert cnt == modelo, f"ciclo {i}: se esperaba cnt = {modelo}, se leyó {cnt}"
        t = int(random.random() < 0.7)
        await poner_tick(dut, t)
        pe = int(dut.period_end.value)
        assert pe == int(modelo == 255 and t), \
            f"ciclo {i}: cnt = {modelo}, tick = {t} -> period_end debe ser {int(modelo == 255 and t)}"
        if t:
            modelo = (modelo + 1) % 256
        await FallingEdge(dut.clk)
