.PHONY: lint sa test clean clean-venv view all venv todo host-coverage

.DEFAULT_GOAL  := all
PYTHON_VERSION := 3.8
PROJ           := datazen
$(PROJ)_DIR    := .
BUILD_DIR      := $($(PROJ)_DIR)/build
VENV_NAME      := venv$(PYTHON_VERSION)
VENV_DIR       := $($(PROJ)_DIR)/$(VENV_NAME)
PYTHON_BIN     := $(VENV_DIR)/bin

$(BUILD_DIR):
	@mkdir -p $@

$(VENV_DIR):
	python$(PYTHON_VERSION) -m venv $(VENV_DIR)
	$(PYTHON_BIN)/pip install --upgrade pip

$(BUILD_DIR)/$(VENV_NAME)/req-%.txt: $($(PROJ)_DIR)/%.txt | $(BUILD_DIR) $(VENV_DIR)
	$(PYTHON_BIN)/pip install -r $<
	@mkdir -p $(dir $@)
	@date > $@

$(BUILD_DIR)/$(VENV_NAME).txt: $(BUILD_DIR)/$(VENV_NAME)/req-requirements.txt $(BUILD_DIR)/$(VENV_NAME)/req-dev_requirements.txt
	@date > $@

venv: $(BUILD_DIR)/$(VENV_NAME).txt

lint-%: $(BUILD_DIR)/$(VENV_NAME).txt
	$(PYTHON_BIN)/$* $(PROJ) tests

lint: lint-flake8 lint-pylint

sa: lint-mypy

test: $(BUILD_DIR)/$(VENV_NAME).txt
	$(PYTHON_BIN)/pytest --log-cli-level=10 --cov=$(PROJ) --cov-report html

view:
	@$(BROWSER) htmlcov/index.html

host-coverage:
	cd $($(PROJ)_DIR)/htmlcov && python -m http.server 8080

all: lint sa test

todo:
	cd $($(PROJ)_DIR) && ack -i todo $(PROJ) tests

clean:
	find -iname '*.pyc' -delete
	find -iname '__pycache__' -delete
	rm -rf $(BUILD_DIR)
	rm -rf cover .coverage build dist *.egg-info htmlcov .pytest_cache

clean-venv:
	rm -rf $(VENV_DIR) $(BUILD_DIR)/$(VENV_NAME).txt
