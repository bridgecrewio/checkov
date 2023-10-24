#!/bin/bash

# iterate over all the cdk python checks
for file in "checkov/cdk/checks/python"/*; do
  # Ensure it's a yaml file
    if [[ -f "$file" && "$file" == *.yaml ]]; then
        basename=$(basename -- "$file")
        filename="${basename%.*}"
        # create a report for this check
        echo "creating report for check: $filename"
        pipenv run checkov -s --framework cdk --repo-id cli/cdk -o json \
          -d "cdk_integration_tests/src/python/$filename" \
          --external-checks-dir "checkov/cdk/checks/python/$filename.yaml" > "checkov_report_cdk_python_$filename.json"
    fi
done

#todo: iterate over all the cdk typescript checks - when ts supported in sast
