#!/bin/bash

.PHONY: install test

all: test

install:
	pip install --upgrade pip twine wheel
	pip install --editable .[test] --upgrade

test:
	openfisca-run-test tests/* --country-package openfisca_france --extensions openfisca_paris
