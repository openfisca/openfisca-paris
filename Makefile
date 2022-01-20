#!/bin/bash

.PHONY: install utest stest test

all: test

clean:
	rm -rf build dist
	find . -name '*.pyc' -exec rm \{\} \;

deps:
	pip install --upgrade pip build twine

install-test:
	pip install --editable ".[test]"

install: deps
	@# Install OpenFisca-Paris for development.
	@# `make install` installs the editable version of OpenFisca-Paris.
	@# This allows contributors to test as they code.
	pip install --editable . --upgrade

build: clean deps
	@# Install OpenFisca-Paris for deployment and publishing.
	@# `make build` allows us to be be sure tests are run against the packaged version
	@# of OpenFisca-Paris, the same we put in the hands of users and reusers.
	python -m build
	pip uninstall --yes openfisca-paris
	find dist -name "*.whl" -exec pip install {} \;

test:
	openfisca test tests --country-package openfisca_france --extension openfisca_paris
