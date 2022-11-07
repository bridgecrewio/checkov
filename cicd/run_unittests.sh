#!/bin/bash

prepare_data () {
  echo "Preparing data for unit tests"
  pip install extras_require
  python setup.py install
  python setup.py sdist bdist_wheel
  pip install responses mock pytest_mock aioresponses
  python -m unittest
  cd integration_tests
  python3 prepare_data.py
  cd ..
}