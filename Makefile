#!/bin/bash

.PHONY: install utest stest test

all: test

clean:
	rm -rf build dist
	find . -name '*.pyc' -exec rm \{\} \;

install:
	pip install --upgrade pip wheel
	pip install --editable .[test] --upgrade
