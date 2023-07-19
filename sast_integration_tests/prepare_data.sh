#!/bin/bash

pipenv run checkov -s --framework sast_python -d flask -o json > checkov_report_sast_python.json
pipenv run checkov -s --framework sast_java -d jenkins -o json > checkov_report_sast_java.json
pipenv run checkov -s --framework sast_javascript -d axios -o json > checkov_report_sast_javascript.json
