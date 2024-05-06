#!/bin/bash

# iterate over all the cdk python checks
#for file in "checkov/cdk/checks/python"/*; do
#  # Ensure it's a yaml file
#  if [[ -f "$file" && "$file" == *.yaml ]]; then
#      basename=$(basename -- "$file")
#      filename="${basename%.*}"
#      check_id=$(grep 'id:' $file | awk '{print $2}')
#      if [[ $check_id != CKV* ]]; then
#        #expects only CKV check ids
#        continue
#      fi
#      # create a report for this check
#      echo "creating report for check: $filename, id: $check_id"
#      pipenv run checkov -s --framework cdk --repo-id cli/cdk -o json --check $check_id \
#        -d "cdk_integration_tests/src/python/$filename" --external-checks-dir "checkov/cdk/checks/python" \
#         > "checkov_report_cdk_python_$filename.json"
#  fi
#done

export ENABLE_SAST_TYPESCRIPT="true"


echo "creating report for CDK"
pipenv run checkov -s --framework cdk --repo-id cli/cdk -o json \
        -d "cdk_integration_tests/src" > "checkov_report_cdk.json"

#todo: iterate over all the cdk typescript checks - when ts supported in sast
