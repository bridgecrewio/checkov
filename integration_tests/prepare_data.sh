#!/bin/bash

echo "Received $1 and then $2"

if [[ "$1" == "windows-latest" ]]
then
  pipenv run checkov -s --framework terraform -d terragoat\\terraform\\ -o json > checkov_report_terragoat.json
  pipenv run checkov -s --framework terraform -d terragoat\\terraform\\ -o junitxml > checkov_report_terragoat.xml
  pipenv run checkov -s --framework cloudformation -d cfngoat\\ -o json --external-checks-dir .\\checkov\\cloudformation\\checks\\graph_checks\\aws > checkov_report_cfngoat.json
  pipenv run checkov -s -d kubernetes-goat\\ --framework kubernetes -o json > checkov_report_kubernetes-goat.json
  pipenv run checkov -s --framework terraform -d terragoat\\terraform\\ -o cyclonedx > checkov_report_terragoat_cyclonedx.xml
  pipenv run checkov -s --framework terraform -d terragoat\\terraform\\ -o sarif
#  LOG_LEVEL=DEBUG pipenv run checkov -s -d kubernetes-goat\\ --framework helm -o json > checkov_report_kubernetes-goat-helm.json
  pipenv run checkov -s --framework terraform --skip-check CKV_AWS_33,CKV_AWS_41 -d terragoat\\terraform\\ -o json > checkov_report_terragoat_with_skip.json
  pipenv run checkov -s --framework cloudformation -d cfngoat\\ -o json --quiet > checkov_report_cfngoat_quiet.json
  pipenv run checkov -s -d terragoat\\terraform\\ --config-file integration_tests\\example_config_files\\config.yaml -o json > checkov_config_report_terragoat.json
else
  pipenv run checkov -s --framework terraform -d terragoat/terraform/ -o json > checkov_report_terragoat.json
  pipenv run checkov -s --framework terraform -d terragoat/terraform/ -o junitxml > checkov_report_terragoat.xml
  pipenv run checkov -s --framework terraform -d terragoat/terraform/ -o cyclonedx > checkov_report_terragoat_cyclonedx.xml
  pipenv run checkov -s --framework terraform -d terragoat/terraform/ -o sarif
  pipenv run checkov -s --framework cloudformation -d cfngoat/ -o json --external-checks-dir ./checkov/cloudformation/checks/graph_checks/aws > checkov_report_cfngoat.json
  pipenv run checkov -s -d kubernetes-goat/ --framework kubernetes -o json > checkov_report_kubernetes-goat.json
  pipenv run checkov -s -d kubernetes-goat/ --framework helm -o json > checkov_report_kubernetes-goat-helm.json
  pipenv run checkov -s -d kustomizegoat/ --framework kustomize -o json > checkov_report_kustomizegoat.json
  pipenv run checkov -s --framework terraform --skip-check CKV_AWS_33,CKV_AWS_41 -d terragoat/terraform/ -o json > checkov_report_terragoat_with_skip.json
  pipenv run checkov -s --framework cloudformation -d cfngoat/ -o json --quiet > checkov_report_cfngoat_quiet.json
  pipenv run checkov -s -d terragoat/terraform/ --config-file integration_tests/example_config_files/config.yaml -o json > checkov_config_report_terragoat.json

fi

if [[ "$2" == "3.8" && "$1" == "ubuntu-latest" ]]
then
  pipenv run checkov -s -f terragoat/terraform/aws/s3.tf --repo-id checkov/integration_test --bc-api-key $BC_KEY > checkov_report_s3_singlefile_api_key_terragoat.txt
  pipenv run checkov -s -d terragoat/terraform/azure/ --repo-id checkov/integration_test --bc-api-key $BC_KEY > checkov_report_azuredir_api_key_terragoat.txt
  pipenv run checkov -s -d terragoat/terraform/azure/ --repo-id checkov/integration_test --skip-results-upload --bc-api-key $BC_KEY > checkov_report_azuredir_api_key_terragoat_no_upload.txt
  echo "running image referencing"
  pipenv run checkov -s -d integration_tests/example_workflow_file/bitbucket/ -o json --repo-id checkov/integration_test --bc-api-key $BC_KEY --include-all-checkov-policies > checkov_report_bitbucket_pipelines_cve.json
  echo "running list"
  pipenv run checkov --list --bc-api-key $BC_KEY --output-bc-ids > checkov_checks_list.txt
  echo "running tfc"
#  GITHUB_PAT="$GITHUB_PAT" TF_REGISTRY_TOKEN="$TFC_TOKEN" pipenv run checkov -s -d integration_tests/example_ext_private_modules/ --download-external-modules True

fi
