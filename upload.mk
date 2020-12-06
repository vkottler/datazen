.PHONY: check-env upload

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

upload: check-env $(PY_PREFIX)upload
