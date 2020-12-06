.PHONY: lint sa test clean clean-venv view all venv todo host-coverage dist \
        sync upload

.DEFAULT_GOAL  := all
PROJ           := datazen
$(PROJ)_DIR    := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
BUILD_DIR_NAME := build
BUILD_DIR      := $($(PROJ)_DIR)/$(BUILD_DIR_NAME)

include $($(PROJ)_DIR)/mk/functions.mk
include $($(PROJ)_DIR)/mk/venv.mk
include $($(PROJ)_DIR)/mk/python.mk
include $($(PROJ)_DIR)/mk/pypi.mk
include $($(PROJ)_DIR)/mk/datazen.mk

$(BUILD_DIR):
	@mkdir -p $@

PY_EXTRA_LINT_ARGS += $($(PROJ)_DIR)/setup.py
lint: $(PY_PREFIX)lint
sa: $(PY_PREFIX)sa
test: $(PY_PREFIX)test
view: $(PY_PREFIX)view
host-coverage: $(PY_PREFIX)host-coverage
dist: $(PY_PREFIX)dist
upload: sync $(PYPI_PREFIX)upload
sync: $(EDITABLE_CONC) $(DZ_PREFIX)sync

all: sync lint sa test dist todo

todo:
	-cd $($(PROJ)_DIR) && ack -i todo $(PROJ) tests

clean: $(PY_PREFIX)clean $(DZ_PREFIX)clean
	@rm -rf $(BUILD_DIR)
