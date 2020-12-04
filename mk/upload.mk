.PHONY: dist check-env upload

dist: $(BUILD_DIR)/$(VENV_NAME).txt
	@rm -rf $($(PROJ)_DIR)/dist
	$(PYTHON_BIN)/python $($(PROJ)_DIR)/setup.py sdist
	$(PYTHON_BIN)/python $($(PROJ)_DIR)/setup.py bdist_wheel

UPLOAD_ENV := $($(PROJ)_DIR)/.upload.env
$(UPLOAD_ENV):
	@rm -f $@
	@echo "export TWINE_USERNAME=__token__" >> $@
	@echo "export TWINE_PASSWORD=`secrethub read vkottler/pypi/api-keys/personal-upload`" >> $@
	+@echo "wrote '$@'"

check-env: | $($(PROJ)_DIR)/.upload.env
ifndef TWINE_USERNAME
	$(error TWINE_USERNAME not set, run 'source $(UPLOAD_ENV)')
endif
ifndef TWINE_PASSWORD
	$(error TWINE_PASSWORD not set, run 'source $(UPLOAD_ENV)')
endif

TWINE_ARGS := --non-interactive --verbose
upload: $(BUILD_DIR)/$(VENV_NAME).txt check-env lint sa test dist
	$(PYTHON_BIN)/twine upload $(TWINE_ARGS) $($(PROJ)_DIR)/dist/*
