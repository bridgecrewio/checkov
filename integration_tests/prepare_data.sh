#!/bin/bash

echo "Received $1 and then $2"

if [[ "$1" == "windows-latest" ]]
then
  pipenv run checkov -s --framework terraform -d terragoat\\terraform\\ -o json > checkov_report_terragoat.json
  pipenv run checkov -s --framework terraform -d terragoat\\terraform\\ -o junitxml > checkov_report_terragoat.xml
  pipenv run checkov -s -d cfngoat\\ -o json --external-checks-dir .\\checkov\\cloudformation\\checks\\graph_checks\\aws > checkov_report_cfngoat.json
  pipenv run checkov -s -d kubernetes-goat\\ --framework kubernetes -o json > checkov_report_kubernetes-goat.json
#  LOG_LEVEL=DEBUG pipenv run checkov -s -d kubernetes-goat\\ --framework helm -o json > checkov_report_kubernetes-goat-helm.json
  pipenv run checkov -s --framework terraform --skip-check CKV_AWS_33,CKV_AWS_41 -d terragoat\\terraform\\ -o json > checkov_report_terragoat_with_skip.json
  pipenv run checkov -s -d cfngoat\\ -o json --quiet > checkov_report_cfngoat_quiet.json
  pipenv run checkov -s -d terragoat\\terraform\\ --config-file integration_tests\\example_config_files\\config.yaml -o json > checkov_config_report_terragoat.json
else
  pipenv run checkov -s --framework terraform -d terragoat/terraform/ -o json > checkov_report_terragoat.json
  pipenv run checkov -s --framework terraform -d terragoat/terraform/ -o junitxml > checkov_report_terragoat.xml
  pipenv run checkov -s -d cfngoat/ -o json --external-checks-dir ./checkov/cloudformation/checks/graph_checks/aws > checkov_report_cfngoat.json
  pipenv run checkov -s -d kubernetes-goat/ --framework kubernetes -o json > checkov_report_kubernetes-goat.json
  pipenv run checkov -s -d kubernetes-goat/ --framework helm -o json > checkov_report_kubernetes-goat-helm.json
  pipenv run checkov -s --framework terraform --skip-check CKV_AWS_33,CKV_AWS_41 -d terragoat/terraform/ -o json > checkov_report_terragoat_with_skip.json
  pipenv run checkov -s -d cfngoat/ -o json --quiet > checkov_report_cfngoat_quiet.json
  pipenv run checkov -s -d terragoat/terraform/ --config-file integration_tests/example_config_files/config.yaml -o json > checkov_config_report_terragoat.json
fi

if [[ "$2" == "3.7" ]]
then
  pipenv run checkov -s -f terragoat/terraform/aws/s3.tf --bc-api-key $BC_KEY > checkov_report_s3_singlefile_api_key_terragoat.txt
  pipenv run checkov -s -d terragoat/terraform/azure/ --bc-api-key $BC_KEY > checkov_report_azuredir_api_key_terragoat.txt
fi
