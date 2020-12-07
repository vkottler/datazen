.PHONY: lint sa test clean clean-venv view all venv todo host-coverage dist \
        sync upload

.DEFAULT_GOAL  := all
PROJ           := datazen
$(PROJ)_DIR    := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

PY_EXTRA_LINT_ARGS += $($(PROJ)_DIR)/setup.py

include $($(PROJ)_DIR)/mk/conf.mk

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

clean: $(PY_PREFIX)editable $(DZ_PREFIX)clean $(PY_PREFIX)clean
	@rm -rf $(BUILD_DIR)
