#!/bin/bash

run_tests () {
  echo "Preparing data for unit tests"
  pip install extras_require
  python setup.py install
  python setup.py sdist bdist_wheel
  pip install responses mock pytest_mock aioresponses
  echo "Running unit tests"
  pytest tests
  pytest --cov-report term --cov=checkov tests
  python -m coverage_badge -o coverage.svg -f
  git commit -m "Update coverage" coverage.svg || echo "No changes to commit"
}

run_tests