# SPDX-License-Identifier: Apache-2.0
#
# Test del prescaler (Subgrupo 1)
#
# Contrato:
#   - tick vale 1 durante un ciclo cada presc + 1 ciclos de clk.
#   - Con presc = 0, tick vale 1 siempre.
#   - El comparador es >= : si presc baja mientras la cuenta va por un valor
#     mayor, el siguiente tick llega enseguida (no 65 536 ciclos después).
#
# Las entradas se cambian y las salidas se leen en el flanco de BAJADA de clk,
# a mitad de ciclo, cuando todas las señales están estables.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

CLK_NS = 100  # 10 MHz


async def iniciar(dut, presc):
    """Arranca el reloj, aplica el reset y lo suelta en un flanco de bajada."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.presc.value = presc
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1


async def capturar_tick(dut, ciclos):
    """Lee tick en cada flanco de bajada y devuelve la lista de valores (0/1)."""
    muestras = []
    for _ in range(ciclos):
        await FallingEdge(dut.clk)
        muestras.append(int(dut.tick.value))
    return muestras


def intervalos(muestras):
    """Distancia, en ciclos, entre cada tick y el siguiente."""
    pos = [i for i, v in enumerate(muestras) if v]
    return [b - a for a, b in zip(pos, pos[1:])]


@cocotb.test()
async def test_reset(dut):
    """Durante el reset tick debe valer 0."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.presc.value = 0
    dut.rst_n.value = 0
    for _ in range(5):
        await FallingEdge(dut.clk)
        assert int(dut.tick.value) == 0, "tick debe ser 0 mientras rst_n = 0"


@cocotb.test()
async def test_presc_cero(dut):
    """Con presc = 0, tick vale 1 en todos los ciclos."""
    await iniciar(dut, 0)
    muestras = (await capturar_tick(dut, 30))[3:]
    assert all(muestras), f"con presc = 0 tick debe valer 1 siempre, se leyó {muestras}"


@cocotb.test()
async def test_periodo(dut):
    """Un tick cada presc + 1 ciclos, y cada tick dura un solo ciclo."""
    for presc in [1, 2, 3, 7, 100]:
        await iniciar(dut, presc)
        muestras = await capturar_tick(dut, (presc + 1) * 6 + 5)
        ints = intervalos(muestras)
        assert len(ints) >= 4, f"presc = {presc}: se esperaban al menos 5 ticks, hubo {len(ints) + 1}"
        assert all(d == presc + 1 for d in ints), \
            f"presc = {presc}: los ticks deben estar separados {presc + 1} ciclos, se midió {ints}"
        dut._log.info(f"presc = {presc}: OK, un tick cada {presc + 1} ciclos")


@cocotb.test()
async def test_presc_16_bits(dut):
    """presc usa los 16 bits (PRESC_H también cuenta)."""
    presc = 300  # 0x012C: necesita el byte alto
    await iniciar(dut, presc)
    ints = intervalos(await capturar_tick(dut, (presc + 1) * 4 + 5))
    assert len(ints) >= 2 and all(d == presc + 1 for d in ints), \
        f"presc = {presc}: se esperaba un tick cada {presc + 1} ciclos, se midió {ints}"


@cocotb.test()
async def test_bajar_presc(dut):
    """Si presc baja por debajo de la cuenta actual, el tick llega enseguida (comparador >=)."""
    await iniciar(dut, 1000)
    await ClockCycles(dut.clk, 600)  # la cuenta va por ~600
    await FallingEdge(dut.clk)
    dut.presc.value = 10

    muestras = await capturar_tick(dut, 3 + 11 * 4)
    primero = muestras.index(1) if 1 in muestras else None
    assert primero is not None and primero <= 2, (
        "al bajar presc de 1000 a 10 con la cuenta en ~600, el siguiente tick debe "
        "llegar en 1 o 2 ciclos. ¿El comparador usa == en vez de >=?"
    )
    ints = intervalos(muestras)
    assert all(d == 11 for d in ints), f"después del cambio: un tick cada 11 ciclos, se midió {ints}"
