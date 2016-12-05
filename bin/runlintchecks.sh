#!/bin/sh

set -e

isort -rc -c idv tests || { echo "isort failed"; exit 1; }

flake8 idv tests
