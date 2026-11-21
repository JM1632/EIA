# Tests por bloque (cocotb + Icarus Verilog)
#
# Uso:   make BLOCK=prescaler            ejecuta test_prescaler.py contra src/prescaler.v
#        make BLOCK=prescaler WAVES=1    además guarda las ondas en sim_build/prescaler/prescaler.fst
#        make todos                      ejecuta los tests de los 6 bloques y resume
#
# Si un bloque usa submódulos propios, agrégalos con EXTRA_SOURCES, por ejemplo:
#        make BLOCK=spi_slave EXTRA_SOURCES="shift_reg.v"

BLOCKS = prescaler pwm_counter pwm_channel reg_bank synchronizer spi_slave

SIM ?= icarus
TOPLEVEL_LANG ?= verilog
BLOCK ?= prescaler
EXTRA_SOURCES ?=

SRC_DIR = $(PWD)/../../src
VERILOG_SOURCES = $(SRC_DIR)/$(BLOCK).v $(addprefix $(SRC_DIR)/,$(EXTRA_SOURCES))
COCOTB_TOPLEVEL = $(BLOCK)
COCOTB_TEST_MODULES = test_$(BLOCK)
SIM_BUILD = sim_build/$(BLOCK)
COCOTB_RESULTS_FILE = results_$(BLOCK).xml

include $(shell cocotb-config --makefiles)/Makefile.sim

# Ejecuta todos los bloques y muestra cuáles pasan. Devuelve error si alguno falla.
.PHONY: todos
todos:
	@failed=""; \
	for b in $(BLOCKS); do \
	  $(MAKE) --no-print-directory BLOCK=$$b > /dev/null 2>&1; \
	  if python -m cocotb_tools.check_results results_$$b.xml > /dev/null 2>&1; then \
	    echo "  OK     $$b"; \
	  else \
	    echo "  FALLA  $$b"; failed="$$failed $$b"; \
	  fi; \
	done; \
	if [ -n "$$failed" ]; then echo "Bloques con fallos:$$failed"; exit 1; fi
