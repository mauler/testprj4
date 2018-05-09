default: test

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  test    						to run tests using pytest"
	@echo "  run    						to run the project locally"

.PHONY: test
test:
	python3.6 -m pytest

.PHONY: run
run:
	DJANGO_SETTINGS_MODULE=cards.settings PYTHONPATH=. python3.6 manage.py migrate
	DJANGO_SETTINGS_MODULE=cards.settings PYTHONPATH=. python3.6 manage.py runserver
