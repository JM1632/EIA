# SPDX-License-Identifier: Apache-2.0
#
# Test del sincronizador (Subgrupo 4)
#
# Contrato:
#   - mosi y csn son mosi_in y csn_in pasados por 2 flip-flops: aparecen
#     exactamente 2 flancos de clk después.
#   - sck_rise / sck_fall: pulso de UN ciclo por cada subida / bajada de sck_in,
#     alineado con mosi (cuando sck_rise vale 1, mosi ya muestra el bit que había
#     en MOSI al subir SCK).
#   - Tras el reset: csn = 1 y todo lo demás en 0.
#
# Las entradas sck_in, mosi_in y csn_in vienen de afuera y cambian en cualquier
# momento, por eso algunos tests las mueven en instantes no alineados con clk.

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, Timer

CLK_NS = 100  # 10 MHz


async def iniciar(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.sck_in.value = 0
    dut.mosi_in.value = 0
    dut.csn_in.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 4)
    await FallingEdge(dut.clk)


class Monitor:
    """Cuenta los pulsos de sck_rise / sck_fall y comprueba que duren un ciclo."""

    def __init__(self, dut):
        self.dut = dut
        self.subidas = 0
        self.bajadas = 0
        self.mosi_en_subida = []
        self.errores = []
        cocotb.start_soon(self._vigilar())

    async def _vigilar(self):
        rise_ant = fall_ant = 0
        while True:
            await FallingEdge(self.dut.clk)
            rise = int(self.dut.sck_rise.value)
            fall = int(self.dut.sck_fall.value)
            if rise and fall:
                self.errores.append("sck_rise y sck_fall valen 1 en el mismo ciclo")
            if rise and rise_ant:
                self.errores.append("sck_rise duró más de un ciclo")
            if fall and fall_ant:
                self.errores.append("sck_fall duró más de un ciclo")
            if rise:
                self.subidas += 1
                self.mosi_en_subida.append(int(self.dut.mosi.value))
            if fall:
                self.bajadas += 1
            rise_ant, fall_ant = rise, fall


@cocotb.test()
async def test_reset(dut):
    """Durante el reset: csn = 1 y el resto en 0, aunque las entradas digan otra cosa."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.sck_in.value = 1
    dut.mosi_in.value = 1
    dut.csn_in.value = 0
    dut.rst_n.value = 0
    for _ in range(5):
        await FallingEdge(dut.clk)
        assert int(dut.csn.value) == 1, "csn debe valer 1 durante el reset (CS inactivo)"
        assert int(dut.mosi.value) == 0, "mosi debe valer 0 durante el reset"
        assert int(dut.sck_rise.value) == 0, "sck_rise debe valer 0 durante el reset"
        assert int(dut.sck_fall.value) == 0, "sck_fall debe valer 0 durante el reset"


@cocotb.test()
async def test_latencia_mosi_csn(dut):
    """mosi y csn aparecen exactamente 2 ciclos después de la entrada."""
    await iniciar(dut)
    for senal_in, senal_out, nuevo in [("mosi_in", "mosi", 1), ("csn_in", "csn", 0),
                                       ("mosi_in", "mosi", 0), ("csn_in", "csn", 1)]:
        anterior = 1 - nuevo
        getattr(dut, senal_in).value = nuevo
        await FallingEdge(dut.clk)
        assert int(getattr(dut, senal_out).value) == anterior, \
            f"{senal_out} cambió después de 1 ciclo: debe pasar por 2 flip-flops"
        await FallingEdge(dut.clk)
        assert int(getattr(dut, senal_out).value) == nuevo, \
            f"{senal_out} debe mostrar el valor nuevo de {senal_in} después de 2 ciclos"
        await ClockCycles(dut.clk, 3)
        await FallingEdge(dut.clk)


@cocotb.test()
async def test_latencia_sck(dut):
    """Una subida de SCK da sck_rise 2 ciclos después, durante 1 ciclo. Igual con la bajada."""
    await iniciar(dut)
    for valor, senal in [(1, "sck_rise"), (0, "sck_fall")]:
        dut.sck_in.value = valor
        lecturas = []
        for _ in range(4):
            await FallingEdge(dut.clk)
            lecturas.append(int(getattr(dut, senal).value))
        assert lecturas == [0, 1, 0, 0], (
            f"tras cambiar sck_in a {valor}, {senal} leído en los 4 ciclos siguientes fue "
            f"{lecturas}; se esperaba [0, 1, 0, 0] (2 flip-flops + detector)"
        )


@cocotb.test()
async def test_cuenta_flancos(dut):
    """Un pulso por cada flanco de SCK, con SCK asíncrono a clk (a 1/8 de clk, el máximo)."""
    await iniciar(dut)
    mon = Monitor(dut)
    medio_periodo = 4 * CLK_NS + 7  # no alineado con clk
    flancos = 100
    for _ in range(flancos):
        dut.sck_in.value = 1
        await Timer(medio_periodo, unit="ns")
        dut.sck_in.value = 0
        await Timer(medio_periodo, unit="ns")
    await ClockCycles(dut.clk, 5)
    assert not mon.errores, mon.errores[0]
    assert mon.subidas == flancos, f"{flancos} subidas de SCK dieron {mon.subidas} pulsos de sck_rise"
    assert mon.bajadas == flancos, f"{flancos} bajadas de SCK dieron {mon.bajadas} pulsos de sck_fall"


@cocotb.test()
async def test_mosi_alineado(dut):
    """Trama SPI modo 0: en cada sck_rise, mosi ya tiene el bit que envió el maestro."""
    random.seed(7)
    await iniciar(dut)
    mon = Monitor(dut)
    medio_periodo = 5 * CLK_NS + 33  # SCK ~ clk / 10, no alineado con clk
    bits = [random.randrange(2) for _ in range(64)]

    dut.csn_in.value = 0
    await Timer(medio_periodo, unit="ns")
    for b in bits:
        dut.mosi_in.value = b          # el maestro cambia MOSI con SCK en 0
        await Timer(medio_periodo, unit="ns")
        dut.sck_in.value = 1           # y el esclavo lo lee en la subida
        await Timer(medio_periodo, unit="ns")
        dut.sck_in.value = 0
    await Timer(medio_periodo, unit="ns")
    dut.csn_in.value = 1
    await ClockCycles(dut.clk, 5)

    assert not mon.errores, mon.errores[0]
    assert mon.subidas == len(bits), f"{len(bits)} subidas de SCK dieron {mon.subidas} pulsos de sck_rise"
    assert mon.mosi_en_subida == bits, "en algún sck_rise, mosi no tenía el bit enviado por el maestro"
