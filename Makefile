
all:
	@echo "make egg|check|coverage"
	@echo

egg:
	python setup.py bdist_egg

check:
	nosetests

coverage:
	nosetests --quiet --with-coverage --cover-package Rosenberg-NMS


