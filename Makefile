.PHONY: lint sa test clean clean-venv view all venv todo host-coverage dist \
        sync clean-dz

.DEFAULT_GOAL  := all
PROJ           := datazen
$(PROJ)_DIR    := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
BUILD_DIR_NAME := build
BUILD_DIR      := $($(PROJ)_DIR)/$(BUILD_DIR_NAME)

include $($(PROJ)_DIR)/mk/functions.mk
include $($(PROJ)_DIR)/mk/venv.mk
include $($(PROJ)_DIR)/mk/python.mk
include $($(PROJ)_DIR)/mk/pypi.mk

$(BUILD_DIR):
	@mkdir -p $@

PY_EXTRA_LINT_ARGS += $($(PROJ)_DIR)/setup.py
lint: $(PY_PREFIX)lint
sa: $(PY_PREFIX)sa
test: $(PY_PREFIX)test
view: $(PY_PREFIX)view
host-coverage: $(PY_PREFIX)host-coverage
dist: $(PY_PREFIX)dist

all: lint sa test dist todo

sync: $(EDITABLE_CONC)
	$(PYTHON_BIN)/dz

sync-verbose: $(EDITABLE_CONC)
	$(PYTHON_BIN)/dz -v

todo:
	-cd $($(PROJ)_DIR) && ack -i todo $(PROJ) tests

clean-dz: $(EDITABLE_CONC)
	$(PYTHON_BIN)/dz -c

clean: $(PY_PREFIX)clean clean-dz
	@rm -rf $(BUILD_DIR)
