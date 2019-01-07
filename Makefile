#!/bin/bash

.PHONY: install utest stest test

all: test

install:
	pip install --upgrade pip wheel
	pip install --editable .[test] --upgrade

utest:
	@echo "Run unit tests..."
	openfisca-run-test tests/unittests/*.yaml --country-package openfisca_france --extensions openfisca_paris

stest:
	@echo "Run specific tests..."
	openfisca-run-test tests/*.yaml --country-package openfisca_france --extensions openfisca_paris

test: utest stest
