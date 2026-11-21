# SPDX-License-Identifier: Apache-2.0
#
# Test del canal PWM (Subgrupo 2)
#
# Contrato (por dentro: buffer -> comparador -> XOR -> selector -> FF de salida):
#   - El buffer del duty copia duty_in solo cuando period_end = 1.
#   - Onda: 1 mientras cnt < buffer.
#   - inv = 1 invierte la onda.
#   - en = 0: la salida vale inv (nivel de reposo).
#   - La salida pasa por un flip-flop: refleja las entradas del ciclo anterior.
#   - Tras el reset: buffer = 0 y pwm_out = 0.
#
# El test hace de contador del PWM: pone cnt = 0, 1, ..., 255, 0, ... (un paso
# por ciclo) y period_end = 1 cuando cnt = 255, igual que el bloque real.
# Las entradas se cambian y las salidas se leen en el flanco de BAJADA de clk.

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

CLK_NS = 100  # 10 MHz


class Modelo:
    """Modelo de referencia del canal, ciclo a ciclo."""

    def __init__(self):
        self.buf = 0
        self.out = 0

    def flanco(self, cnt, period_end, duty_in, en, inv):
        """Lo que hace el canal en un flanco de subida de clk."""
        onda = int(cnt < self.buf) ^ inv
        self.out = onda if en else inv
        if period_end:
            self.buf = duty_in


class Banco:
    """Hace de contador del PWM y mantiene el modelo sincronizado con el DUT."""

    def __init__(self, dut):
        self.dut = dut
        self.modelo = Modelo()
        self.cnt = 0
        self.duty = 0
        self.en = 0
        self.inv = 0
        self.ciclo = 0

    async def paso(self):
        """Avanza un ciclo: comprueba pwm_out y pone el siguiente cnt."""
        await FallingEdge(self.dut.clk)
        leido = int(self.dut.pwm_out.value)
        assert leido == self.modelo.out, (
            f"ciclo {self.ciclo}: pwm_out = {leido}, se esperaba {self.modelo.out} "
            f"(cnt anterior = {(self.cnt - 1) % 256}, buffer = {self.modelo.buf}, "
            f"en = {self.en}, inv = {self.inv})"
        )
        pe = int(self.cnt == 255)
        self.dut.cnt.value = self.cnt
        self.dut.period_end.value = pe
        self.dut.duty_in.value = self.duty
        self.dut.en.value = self.en
        self.dut.inv.value = self.inv
        self.modelo.flanco(self.cnt, pe, self.duty, self.en, self.inv)
        self.cnt = (self.cnt + 1) % 256
        self.ciclo += 1
        return leido

    async def pasos(self, n):
        return [await self.paso() for _ in range(n)]

    async def hasta_cnt(self, valor):
        """Avanza hasta que el siguiente cnt que se va a poner sea 'valor'."""
        while self.cnt != valor:
            await self.paso()


async def iniciar(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.cnt.value = 0
    dut.period_end.value = 0
    dut.duty_in.value = 0
    dut.en.value = 0
    dut.inv.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    return Banco(dut)


@cocotb.test()
async def test_reset(dut):
    """Durante el reset pwm_out = 0."""
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.cnt.value = 10
    dut.period_end.value = 1
    dut.duty_in.value = 200
    dut.en.value = 1
    dut.inv.value = 0
    dut.rst_n.value = 0
    for _ in range(5):
        await FallingEdge(dut.clk)
        assert int(dut.pwm_out.value) == 0, "pwm_out debe ser 0 mientras rst_n = 0"


@cocotb.test()
async def test_duty(dut):
    """En cada periodo, la salida vale 1 exactamente 'duty' ciclos de 256."""
    banco = await iniciar(dut)
    banco.en = 1
    for duty in [0, 1, 64, 128, 200, 255]:
        banco.duty = duty
        await banco.pasos(512)  # dos periodos: el duty nuevo ya está cargado
        unos = sum(await banco.pasos(256))
        assert unos == duty, f"duty = {duty}: la salida estuvo en 1 {unos} de 256 ciclos"
        dut._log.info(f"duty = {duty}: OK")


@cocotb.test()
async def test_inversion(dut):
    """Con inv = 1 la onda se invierte: 256 - duty ciclos en 1."""
    banco = await iniciar(dut)
    banco.en = 1
    banco.inv = 1
    for duty in [0, 64, 255]:
        banco.duty = duty
        await banco.pasos(512)
        unos = sum(await banco.pasos(256))
        assert unos == 256 - duty, f"duty = {duty}, inv = 1: se esperaban {256 - duty} ciclos en 1, hubo {unos}"


@cocotb.test()
async def test_apagado(dut):
    """Con en = 0 la salida queda fija en inv, sea cual sea el duty."""
    banco = await iniciar(dut)
    banco.duty = 128
    await banco.pasos(512)
    for inv in [0, 1]:
        banco.en = 0
        banco.inv = inv
        await banco.pasos(2)
        salidas = await banco.pasos(256)
        assert all(s == inv for s in salidas), f"en = 0, inv = {inv}: la salida debe quedarse en {inv}"


@cocotb.test()
async def test_doble_buffer(dut):
    """Un cambio de duty a mitad de periodo solo se aplica en el periodo siguiente."""
    banco = await iniciar(dut)
    banco.en = 1
    banco.duty = 50
    await banco.pasos(512)

    await banco.hasta_cnt(100)
    banco.duty = 200  # cambio a mitad de periodo
    # Resto de este periodo: con el duty viejo (50) la salida debe seguir en 0.
    # Si el buffer se actualizara enseguida, valdría 1 hasta cnt = 199.
    resto = await banco.pasos(150)
    assert sum(resto) == 0, (
        "el duty cambió a mitad de periodo y la salida cambió enseguida: "
        "el buffer solo debe copiar duty_in cuando period_end = 1"
    )
    await banco.hasta_cnt(0)
    unos = sum(await banco.pasos(256))
    assert unos == 200, f"en el periodo siguiente ya debe usar duty = 200, la salida estuvo en 1 {unos} ciclos"


@cocotb.test()
async def test_aleatorio(dut):
    """Cambios aleatorios de duty, en e inv, comparados ciclo a ciclo con el modelo."""
    random.seed(4321)
    banco = await iniciar(dut)
    for _ in range(256 * 12):
        if random.random() < 0.02:
            banco.duty = random.randrange(256)
        if random.random() < 0.005:
            banco.en = random.randrange(2)
        if random.random() < 0.005:
            banco.inv = random.randrange(2)
        await banco.paso()
