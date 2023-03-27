#!/bin/bash

echo "Received $1 and then $2"

if [[ "$1" == "windows-latest" ]]
then
  pipenv run checkov --framework terraform -d terragoat\\terraform\\ -o json > checkov_report_terragoat.json
  pipenv run checkov --framework terraform -d terragoat\\terraform\\ -o junitxml > checkov_report_terragoat.xml
  pipenv run checkov --framework cloudformation -d cfngoat\\ -o json --external-checks-dir .\\checkov\\cloudformation\\checks\\graph_checks\\aws > checkov_report_cfngoat.json
  pipenv run checkov -d kubernetes-goat\\ --framework kubernetes -o json > checkov_report_kubernetes-goat.json
  pipenv run checkov --framework terraform -d terragoat\\terraform\\ -o cyclonedx > checkov_report_terragoat_cyclonedx.xml
  pipenv run checkov --framework terraform -d terragoat\\terraform\\ -o sarif
#  LOG_LEVEL=DEBUG pipenv run checkov -d kubernetes-goat\\ --framework helm -o json > checkov_report_kubernetes-goat-helm.json
  pipenv run checkov --framework terraform --skip-check CKV_AWS_33,CKV_AWS_41 -d terragoat\\terraform\\ -o json > checkov_report_terragoat_with_skip.json
  pipenv run checkov --framework cloudformation -d cfngoat\\ -o json --quiet > checkov_report_cfngoat_quiet.json
  pipenv run checkov -d terragoat\\terraform\\ --config-file integration_tests\\example_config_files\\config.yaml -o json > checkov_config_report_terragoat.json
else
  pipenv run checkov --framework terraform -d terragoat/terraform/ -o json > checkov_report_terragoat.json
  pipenv run checkov --framework terraform -d terragoat/terraform/ -o junitxml > checkov_report_terragoat.xml
  pipenv run checkov --framework terraform -d terragoat/terraform/ -o cyclonedx > checkov_report_terragoat_cyclonedx.xml
  pipenv run checkov --framework terraform -d terragoat/terraform/ -o sarif
  pipenv run checkov --framework cloudformation -d cfngoat/ -o json --external-checks-dir ./checkov/cloudformation/checks/graph_checks/aws > checkov_report_cfngoat.json
  pipenv run checkov -d kubernetes-goat/ --framework kubernetes -o json > checkov_report_kubernetes-goat.json
  pipenv run checkov -d kubernetes-goat/ --framework helm -o json > checkov_report_kubernetes-goat-helm.json
  pipenv run checkov -d kustomizegoat/ --framework kustomize -o json > checkov_report_kustomizegoat.json
  pipenv run checkov --framework terraform --skip-check CKV_AWS_33,CKV_AWS_41 -d terragoat/terraform/ -o json > checkov_report_terragoat_with_skip.json
  pipenv run checkov --framework cloudformation -d cfngoat/ -o json --quiet > checkov_report_cfngoat_quiet.json
  pipenv run checkov -d terragoat/terraform/ --config-file integration_tests/example_config_files/config.yaml -o json > checkov_config_report_terragoat.json

fi

if [[ "$2" == "3.7" && "$1" == "ubuntu-latest" ]]
then
  echo checkov -f terragoat/terraform/aws/s3.tf --bc-api-key $BC_KEY
  pipenv run checkov -f terragoat/terraform/aws/s3.tf --bc-api-key $BC_KEY > checkov_report_s3_singlefile_api_key_terragoat.txt
  pipenv run checkov -d terragoat/terraform/azure/ --bc-api-key $BC_KEY > checkov_report_azuredir_api_key_terragoat.txt
  echo "running image referencing"
  pipenv run checkov -d integration_tests/example_workflow_file/.github/workflows/ -o json --bc-api-key $BC_KEY --include-all-checkov-policies > checkov_report_workflow_cve.json
  pipenv run checkov -d integration_tests/example_workflow_file/bitbucket/ -o json --bc-api-key $BC_KEY --include-all-checkov-policies > checkov_report_bitbucket_pipelines_cve.json
  echo "running list"
  pipenv run checkov--list --bc-api-key $BC_KEY --output-bc-ids > checkov_checks_list.txt
  echo "running tfc"
#  GITHUB_PAT="$GITHUB_PAT" TFC_TOKEN="$TFC_TOKEN" pipenv run checkov -d integration_tests/example_ext_private_modules/ --download-external-modules True

fi
