#!/bin/bash

pipenv run checkov -s --framework sast_python -d flask --repo-id cli/flask -o json > checkov_report_sast_python.json
pipenv run checkov -s --framework sast_java -d jenkins --repo-id cli/jenkins -o json > checkov_report_sast_java.json
pipenv run checkov -s --framework sast_javascript -d axios --repo-id cli/axios -o json > checkov_report_sast_javascript.json
