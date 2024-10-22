#!/bin/bash

export SAVE_SAST_REPORT_LOCALLY=TRUE

pipenv run checkov -s --framework sast_python -d flask --repo-id cli/flask -o json --output-file-path checkov_report_sast_python.json,
pipenv run checkov -s --framework sast_java -d WebGoat --repo-id cli/webgoat -o json --output-file-path checkov_report_sast_java.json,
pipenv run checkov -s --framework sast_javascript -d axios --repo-id cli/axios -o json --output-file-path checkov_report_sast_javascript.json,
