# SPDX-License-Identifier: Apache-2.0
#
# Test del esclavo SPI (Subgrupo 4)
#
# Contrato (SPI modo 0, tramas de 16 bits, MSB primero):
#   - Byte 1: bit 7 = R/W (1 = escribir, 0 = leer), bits 6-0 = dirección.
#   - Escritura: tras la subida 16, wdata = byte 2 y wr_en = 1 durante UN ciclo.
#   - Lectura: no genera wr_en; por MISO salen los 8 bits de rdata (MSB primero),
#     que el maestro lee en las subidas 9 a 16.
#   - En una escritura, por MISO sale el valor que tenía el registro antes.
#   - Una trama incompleta (csn sube antes de 16 bits) no escribe nada.
#   - miso = 0 cuando csn = 1.
#
# El test hace de sincronizador (mueve csn, mosi, sck_rise y sck_fall igual que
# el bloque real: pulsos de un ciclo) y de banco de registros (responde rdata
# según addr y guarda lo que llega con wr_en).
# Las entradas se cambian y las salidas se leen en el flanco de BAJADA de clk.

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

CLK_NS = 100  # 10 MHz
ID = 0x06
ID_VALOR = 0xA5
MEDIO_SCK = 4  # ciclos de clk entre flancos de SCK (SCK = clk / 8, el máximo)


def valor(senal):
    """Lee una señal como entero; si tiene X o Z devuelve None."""
    try:
        return int(senal.value)
    except ValueError:
        return None


class Entorno:
    """Maestro SPI + banco de registros simulado + monitor de wr_en."""

    def __init__(self, dut):
        self.dut = dut
        self.regs = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        self.escrituras = []      # (addr, wdata) de cada pulso de wr_en
        self.errores = []
        cocotb.start_soon(self._banco_y_monitor())

    def leer_reg(self, addr):
        if addr == ID:
            return ID_VALOR
        return self.regs.get(addr, 0)

    async def _banco_y_monitor(self):
        wr_ant = 0
        while True:
            await FallingEdge(self.dut.clk)
            addr = valor(self.dut.addr)
            wr = valor(self.dut.wr_en)
            if wr:
                if wr_ant:
                    self.errores.append("wr_en duró más de un ciclo")
                else:
                    wdata = valor(self.dut.wdata)
                    self.escrituras.append((addr, wdata))
                    if addr in self.regs and wdata is not None:
                        self.regs[addr] = wdata
            wr_ant = wr
            if valor(self.dut.csn) == 1 and valor(self.dut.miso) != 0:
                self.errores.append("miso debe valer 0 cuando csn = 1")
            self.dut.rdata.value = self.leer_reg(addr) if addr is not None else 0

    async def ciclos(self, n):
        for _ in range(n):
            await FallingEdge(self.dut.clk)

    async def pulso(self, senal):
        senal.value = 1
        await self.ciclos(1)
        senal.value = 0

    async def transferir(self, byte1, byte2, nbits=16):
        """Envía una trama (o solo los primeros nbits) y devuelve el byte leído por MISO."""
        dut = self.dut
        palabra = (byte1 << 8) | byte2
        dut.csn.value = 0
        await self.ciclos(MEDIO_SCK)
        leidos = []
        for i in range(nbits):
            dut.mosi.value = (palabra >> (15 - i)) & 1   # MOSI cambia con SCK en 0
            await self.ciclos(MEDIO_SCK - 1)
            leidos.append(valor(dut.miso))               # el maestro lee MISO al subir SCK
            await self.pulso(dut.sck_rise)
            await self.ciclos(MEDIO_SCK - 1)
            await self.pulso(dut.sck_fall)
        await self.ciclos(MEDIO_SCK)
        dut.csn.value = 1
        await self.ciclos(MEDIO_SCK)
        bits = leidos[8:16]
        if len(bits) < 8 or None in bits:
            return None
        return int("".join(str(b) for b in bits), 2)

    async def escribir(self, addr, dato):
        return await self.transferir(0x80 | addr, dato)

    async def leer(self, addr):
        return await self.transferir(addr & 0x7F, 0x00)

    def comprobar_errores(self):
        assert not self.errores, self.errores[0]


async def iniciar(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.csn.value = 1
    dut.mosi.value = 0
    dut.sck_rise.value = 0
    dut.sck_fall.value = 0
    dut.rdata.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    entorno = Entorno(dut)
    await entorno.ciclos(4)
    return entorno


@cocotb.test()
async def test_reset(dut):
    """Tras el reset: wr_en = 0 y miso = 0."""
    env = await iniciar(dut)
    assert valor(dut.wr_en) == 0, "wr_en debe valer 0 tras el reset"
    assert valor(dut.miso) == 0, "miso debe valer 0 con csn = 1"
    env.comprobar_errores()


@cocotb.test()
async def test_escritura(dut):
    """Una escritura genera un único wr_en con la dirección y el dato correctos."""
    env = await iniciar(dut)
    await env.escribir(0x03, 0x5A)
    env.comprobar_errores()
    assert env.escrituras == [(0x03, 0x5A)], \
        f"se esperaba una escritura (addr 0x03, dato 0x5A), hubo {env.escrituras}"


@cocotb.test()
async def test_lectura_id(dut):
    """Leer la dirección 0x06 devuelve 0xA5 por MISO y no escribe nada."""
    env = await iniciar(dut)
    leido = await env.leer(ID)
    env.comprobar_errores()
    assert env.escrituras == [], f"una lectura no debe generar wr_en, hubo {env.escrituras}"
    assert leido == ID_VALOR, f"leer el ID debe devolver 0xA5, llegó {leido!r}"


@cocotb.test()
async def test_escribir_y_leer(dut):
    """Lo que se escribe por SPI se puede leer de vuelta por SPI."""
    env = await iniciar(dut)
    valores = {0: 0x15, 1: 0xC3, 2: 0x01, 3: 0x80, 4: 0xFF, 5: 0x7E}
    for addr, dato in valores.items():
        await env.escribir(addr, dato)
    for addr, dato in valores.items():
        leido = await env.leer(addr)
        assert leido == dato, f"dirección 0x{addr:02X}: se escribió 0x{dato:02X} y se leyó {leido!r}"
    env.comprobar_errores()


@cocotb.test()
async def test_miso_en_escritura(dut):
    """Durante una escritura, MISO devuelve el valor anterior del registro."""
    env = await iniciar(dut)
    await env.escribir(0x04, 0x11)
    anterior = await env.escribir(0x04, 0x22)
    env.comprobar_errores()
    assert anterior == 0x11, f"al escribir 0x22 sobre 0x11, MISO debía devolver 0x11, llegó {anterior!r}"
    assert env.regs[4] == 0x22


@cocotb.test()
async def test_trama_incompleta(dut):
    """Si csn sube antes de 16 bits no se escribe nada, y la trama siguiente funciona."""
    env = await iniciar(dut)
    for nbits in [1, 7, 8, 9, 15]:
        await env.transferir(0x80 | 0x05, 0xAA, nbits=nbits)
        assert env.escrituras == [], \
            f"una trama de {nbits} bits no debe escribir nada, hubo {env.escrituras}"
    await env.escribir(0x05, 0x3C)
    env.comprobar_errores()
    assert env.escrituras == [(0x05, 0x3C)], \
        f"tras las tramas incompletas, la escritura completa debía funcionar, hubo {env.escrituras}"


@cocotb.test()
async def test_tramas_aleatorias(dut):
    """Muchas tramas seguidas de lectura y escritura, comparadas con el banco simulado."""
    random.seed(2024)
    env = await iniciar(dut)
    for i in range(40):
        addr = random.choice([0, 1, 2, 3, 4, 5, ID, random.randrange(128)])
        if random.random() < 0.5:
            dato = random.randrange(256)
            antes = len(env.escrituras)
            await env.escribir(addr, dato)
            assert env.escrituras[antes:] == [(addr, dato)], \
                f"trama {i}: escritura de 0x{dato:02X} en 0x{addr:02X} dio {env.escrituras[antes:]}"
        else:
            esperado = env.leer_reg(addr)
            leido = await env.leer(addr)
            assert leido == esperado, \
                f"trama {i}: leer 0x{addr:02X} debía dar 0x{esperado:02X}, llegó {leido!r}"
    env.comprobar_errores()
