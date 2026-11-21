# SPDX-License-Identifier: Apache-2.0
#
# Test del banco de registros (Subgrupo 3)
#
# Contrato:
#   0x00 CTRL     bits 0-2 -> ch_en, bits 3-5 -> ch_inv
#   0x01 PRESC_L  \
#   0x02 PRESC_H  / presc = {PRESC_H, PRESC_L}
#   0x03 DUTY0, 0x04 DUTY1, 0x05 DUTY2
#   0x06 ID       solo lectura, siempre 0xA5
#   - Se escribe en el flanco de clk en que wr_en = 1, en el registro de addr.
#   - rdata es combinacional: muestra el registro de addr sin esperar al reloj.
#   - Direcciones libres (0x07-0x7F): leer da 0 y escribir no hace nada.
#   - Tras el reset, los 6 registros valen 0.
#
# Las entradas se cambian y las salidas se leen en el flanco de BAJADA de clk.

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, Timer

CLK_NS = 100  # 10 MHz

CTRL, PRESC_L, PRESC_H, DUTY0, DUTY1, DUTY2, ID = range(7)
NOMBRES = ["CTRL", "PRESC_L", "PRESC_H", "DUTY0", "DUTY1", "DUTY2", "ID"]
ID_VALOR = 0xA5

# Los bits 6-7 de CTRL están libres: el test no comprueba qué se lee en ellos.
MASCARA = {CTRL: 0x3F}


async def iniciar(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.addr.value = 0
    dut.wdata.value = 0
    dut.wr_en.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    await FallingEdge(dut.clk)


async def escribir(dut, addr, dato):
    """Pulso de wr_en de un ciclo con addr y wdata. Termina en un flanco de bajada."""
    dut.addr.value = addr
    dut.wdata.value = dato
    dut.wr_en.value = 1
    await FallingEdge(dut.clk)
    dut.wr_en.value = 0
    await FallingEdge(dut.clk)


async def leer(dut, addr):
    """Pone addr y lee rdata 1 ns después, sin flanco de reloj de por medio."""
    dut.addr.value = addr
    await Timer(1, unit="ns")
    return int(dut.rdata.value)


async def comprobar(dut, esperado):
    """Lee los 7 registros y las salidas hacia el PWM y los compara con 'esperado'."""
    for addr in range(7):
        m = MASCARA.get(addr, 0xFF)
        valor = await leer(dut, addr)
        assert valor & m == esperado[addr] & m, \
            f"{NOMBRES[addr]} (0x{addr:02X}): se leyó 0x{valor:02X}, se esperaba 0x{esperado[addr]:02X}"
    ctrl = esperado[CTRL]
    assert int(dut.ch_en.value) == ctrl & 0b111, "ch_en debe ser CTRL[2:0]"
    assert int(dut.ch_inv.value) == (ctrl >> 3) & 0b111, "ch_inv debe ser CTRL[5:3]"
    presc = (esperado[PRESC_H] << 8) | esperado[PRESC_L]
    assert int(dut.presc.value) == presc, \
        f"presc debe ser {{PRESC_H, PRESC_L}} = 0x{presc:04X}, se leyó 0x{int(dut.presc.value):04X}"
    assert int(dut.duty0.value) == esperado[DUTY0], "duty0 debe ser DUTY0"
    assert int(dut.duty1.value) == esperado[DUTY1], "duty1 debe ser DUTY1"
    assert int(dut.duty2.value) == esperado[DUTY2], "duty2 debe ser DUTY2"


def inicial():
    return [0, 0, 0, 0, 0, 0, ID_VALOR]


@cocotb.test()
async def test_reset(dut):
    """Tras el reset: todo en 0 y el ID en 0xA5."""
    await iniciar(dut)
    await comprobar(dut, inicial())


@cocotb.test()
async def test_escribir_y_leer(dut):
    """Cada registro guarda lo que se le escribe y no toca a los demás."""
    await iniciar(dut)
    esperado = inicial()
    valores = {CTRL: 0b00_110_101, PRESC_L: 0x34, PRESC_H: 0x12, DUTY0: 10, DUTY1: 128, DUTY2: 255}
    for addr, dato in valores.items():
        await escribir(dut, addr, dato)
        esperado[addr] = dato
        await comprobar(dut, esperado)


@cocotb.test()
async def test_salidas(dut):
    """ch_en, ch_inv y presc salen de los bits correctos."""
    await iniciar(dut)
    await escribir(dut, CTRL, 0b00_110_101)
    assert int(dut.ch_en.value) == 0b101, "ch_en debe ser CTRL[2:0] = 0b101"
    assert int(dut.ch_inv.value) == 0b110, "ch_inv debe ser CTRL[5:3] = 0b110"
    await escribir(dut, PRESC_L, 0xCD)
    await escribir(dut, PRESC_H, 0xAB)
    assert int(dut.presc.value) == 0xABCD, "presc = {PRESC_H, PRESC_L}: ¿bytes al revés?"


@cocotb.test()
async def test_id_solo_lectura(dut):
    """Escribir en el ID no lo cambia ni afecta a otros registros."""
    await iniciar(dut)
    await escribir(dut, ID, 0x00)
    await escribir(dut, ID, 0xFF)
    await comprobar(dut, inicial())


@cocotb.test()
async def test_direcciones_libres(dut):
    """Las direcciones 0x07-0x7F leen 0 y escribir en ellas no hace nada."""
    await iniciar(dut)
    for addr in [0x07, 0x08, 0x10, 0x40, 0x7F]:
        await escribir(dut, addr, 0x5A)
        await comprobar(dut, inicial())
        assert await leer(dut, addr) == 0, f"la dirección libre 0x{addr:02X} debe leer 0"


@cocotb.test()
async def test_sin_wr_en(dut):
    """Sin wr_en no se escribe nada, aunque addr y wdata cambien."""
    await iniciar(dut)
    for addr in range(6):
        dut.addr.value = addr
        dut.wdata.value = 0x77
        await ClockCycles(dut.clk, 3)
    await FallingEdge(dut.clk)
    await comprobar(dut, inicial())


@cocotb.test()
async def test_reset_borra(dut):
    """Un reset en marcha vuelve todos los registros a 0."""
    await iniciar(dut)
    for addr in range(6):
        await escribir(dut, addr, 0x3F)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    await FallingEdge(dut.clk)
    await comprobar(dut, inicial())


@cocotb.test()
async def test_aleatorio(dut):
    """Escrituras y lecturas aleatorias comparadas con un modelo."""
    random.seed(99)
    await iniciar(dut)
    esperado = inicial()
    for _ in range(300):
        addr = random.choice([0, 1, 2, 3, 4, 5, 6, 7, random.randrange(128)])
        dato = random.randrange(256)
        await escribir(dut, addr, dato)
        if addr < 6:
            esperado[addr] = dato
        await comprobar(dut, esperado)
