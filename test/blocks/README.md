# Tests por bloque

Cada bloque del chip tiene aquí su propio testbench en Python (cocotb). Cada test comprueba que el bloque cumple
el contrato del documento del proyecto: nombres, anchos y comportamiento de cada señal.

| Bloque | Test | Subgrupo |
|---|---|---|
| `src/prescaler.v` | [test_prescaler.py](test_prescaler.py) | 1 |
| `src/pwm_counter.v` | [test_pwm_counter.py](test_pwm_counter.py) | 1 |
| `src/pwm_channel.v` | [test_pwm_channel.py](test_pwm_channel.py) | 2 |
| `src/reg_bank.v` | [test_reg_bank.py](test_reg_bank.py) | 3 |
| `src/synchronizer.v` | [test_synchronizer.py](test_synchronizer.py) | 4 |
| `src/spi_slave.v` | [test_spi_slave.py](test_spi_slave.py) | 4 |

Mientras un bloque sea solo el esqueleto, su test **falla**. Es lo esperado: el test pasa a verde cuando el
bloque está bien implementado.

## Ejecutarlos en GitHub (sin instalar nada)

Con cada push, el workflow **blocks** corre los 6 tests, cada uno como un job separado. En la pestaña
**Actions** del repositorio, abre la ejecución de **blocks** y busca el job de tu bloque:

- ✓ verde: tu bloque cumple todo el contrato.
- ✗ rojo: abre el job, paso *Run block test*, y busca la línea `FAIL` y el mensaje del `assert` que falló.

Las ondas de cada bloque se guardan en los artifacts de la ejecución (`ondas-<bloque>`). Descárgalas y ábrelas
con GTKWave o [Surfer](https://surfer-project.org/).

## Ejecutarlos en tu computador

Necesitas Icarus Verilog y Python con cocotb. Lo más fácil es abrir el repositorio en el **devcontainer** de
VS Code, que ya trae todo instalado. Desde esta carpeta:

```sh
cd test/blocks
make BLOCK=prescaler            # corre el test del prescaler
make BLOCK=prescaler WAVES=1    # además guarda las ondas en sim_build/prescaler/
make todos                      # corre los 6 tests y dice cuáles pasan
```

Al final verás una tabla con cada test (`PASS` o `FAIL`). Si algo falla, el mensaje dice qué se esperaba y
qué se leyó.

Para ver las ondas:

```sh
gtkwave sim_build/prescaler/prescaler.fst
```

Si tu bloque usa submódulos en archivos propios, agrégalos así:

```sh
make BLOCK=spi_slave EXTRA_SOURCES="mi_submodulo.v"
```

(Recuerda añadirlos también a `source_files` en `info.yaml` y a `PROJECT_SOURCES` en `test/Makefile`).

## Cómo están hechos

- El test hace de **resto del chip**: genera el reloj y el reset, y mueve las entradas como lo harían los
  bloques vecinos. Por ejemplo, el test del canal PWM hace de contador y el del esclavo SPI hace de
  sincronizador y de banco de registros.
- Las entradas se cambian y las salidas se leen en el **flanco de bajada** de `clk`, a mitad de ciclo, cuando
  todo está estable.
- Varios tests comparan el bloque **ciclo a ciclo** con un modelo de referencia en Python, con valores
  aleatorios (siempre la misma semilla, así que un fallo se repite igual cada vez).

## Si crees que el test está mal

Puede pasar: el test es una lectura del contrato y tú puedes haberlo leído distinto. No cambies el test para que
tu bloque pase. Coméntalo con el equipo, decidan cuál es el comportamiento correcto y, si hace falta, corrijan
el test o el documento.
