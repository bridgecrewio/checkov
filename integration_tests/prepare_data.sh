#!/bin/bash

echo "Received $1 and then $2"

if [[ "$1" == "windows-latest" ]]
then
  checkov -s --framework terraform -d terragoat\\terraform\\ -o json > checkov_report_terragoat.json
  checkov -s --framework terraform -d terragoat\\terraform\\ -o junitxml > checkov_report_terragoat.xml
  checkov -s --framework cloudformation -d cfngoat\\ -o json --external-checks-dir .\\checkov\\cloudformation\\checks\\graph_checks\\aws > checkov_report_cfngoat.json
  checkov -s -d kubernetes-goat\\ --framework kubernetes -o json > checkov_report_kubernetes-goat.json
  checkov -s --framework terraform -d terragoat\\terraform\\ -o cyclonedx > checkov_report_terragoat_cyclonedx.xml
  checkov -s --framework terraform -d terragoat\\terraform\\ -o sarif
#  LOG_LEVEL=DEBUG checkov -s -d kubernetes-goat\\ --framework helm -o json > checkov_report_kubernetes-goat-helm.json
  checkov -s --framework terraform --skip-check CKV_AWS_33,CKV_AWS_41 -d terragoat\\terraform\\ -o json > checkov_report_terragoat_with_skip.json
  checkov -s --framework cloudformation -d cfngoat\\ -o json --quiet > checkov_report_cfngoat_quiet.json
  checkov -s -d terragoat\\terraform\\ --config-file integration_tests\\example_config_files\\config.yaml -o json > checkov_config_report_terragoat.json
else
  checkov -s --framework terraform -d terragoat/terraform/ -o json > checkov_report_terragoat.json
  checkov -s --framework terraform -d terragoat/terraform/ -o junitxml > checkov_report_terragoat.xml
  checkov -s --framework terraform -d terragoat/terraform/ -o cyclonedx > checkov_report_terragoat_cyclonedx.xml
  checkov -s --framework terraform -d terragoat/terraform/ -o sarif
  checkov -s --framework cloudformation -d cfngoat/ -o json --external-checks-dir ./checkov/cloudformation/checks/graph_checks/aws > checkov_report_cfngoat.json
  checkov -s -d kubernetes-goat/ --framework kubernetes -o json > checkov_report_kubernetes-goat.json
  checkov -s -d kubernetes-goat/ --framework helm -o json > checkov_report_kubernetes-goat-helm.json
  checkov -s -d kustomizegoat/ --framework kustomize -o json > checkov_report_kustomizegoat.json
  checkov -s --framework terraform --skip-check CKV_AWS_33,CKV_AWS_41 -d terragoat/terraform/ -o json > checkov_report_terragoat_with_skip.json
  checkov -s --framework cloudformation -d cfngoat/ -o json --quiet > checkov_report_cfngoat_quiet.json
  checkov -s -d terragoat/terraform/ --config-file integration_tests/example_config_files/config.yaml -o json > checkov_config_report_terragoat.json

fi

if [[ "$2" == "3.7" && "$1" == "ubuntu-latest" ]]
then
  checkov -s -f terragoat/terraform/aws/s3.tf  > checkov_report_s3_singlefile_api_key_terragoat.txt
  checkov -s -d terragoat/terraform/azure/  > checkov_report_azuredir_api_key_terragoat.txt
  export CHECKOV_EXPERIMENTAL_IMAGE_REFERENCING=True
  echo "running image referencing"
  checkov -s -d integration_tests/example_workflow_file/.github/workflows/ -o json  --include-all-checkov-policies > checkov_report_workflow_cve.json
#  checkov -s -d integration_tests/example_workflow_file/bitbucket/ -o json  --include-all-checkov-policies > checkov_report_bitbucket_pipelines_cve.json
  echo "running list"
  checkov --list  --output-bc-ids > checkov_checks_list.txt
  echo "running tfc"
#  GITHUB_PAT="$GITHUB_PAT" TFC_TOKEN="$TFC_TOKEN" checkov -s -d integration_tests/example_ext_private_modules/ --download-external-modules True

fi
