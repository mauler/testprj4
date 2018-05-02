default: test

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  test    						to run tests using pytest"

.PHONY: test
test:
	python3.6 -m pytest
