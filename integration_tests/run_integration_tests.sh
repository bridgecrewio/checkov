#!/bin/bash


prepare_data () {
  python checkov/main.py -s --framework terraform -d repositories/terragoat/terraform/ -o json > checkov_report_terragoat.json
  python checkov/main.py -s --framework terraform -d repositories/terragoat/terraform/ -o junitxml > checkov_report_terragoat.xml
  python checkov/main.py -s --framework terraform -d repositories/terragoat/terraform/ -o cyclonedx > checkov_report_terragoat_cyclonedx.xml
  python checkov/main.py -s --framework terraform -d repositories/terragoat/terraform/ -o sarif
  python checkov/main.py -s -d repositories/cfngoat/ -o json --external-checks-dir ./checkov/cloudformation/checks/graph_checks/aws > checkov_report_cfngoat.json
  python checkov/main.py -s -d repositories/kubernetes-goat/ --framework kubernetes -o json > checkov_report_kubernetes-goat.json
  python checkov/main.py -s -d repositories/kubernetes-goat/ --framework helm -o json > checkov_report_kubernetes-goat-helm.json
  python checkov/main.py -s -d repositories/kustomizegoat/ --framework kustomize -o json > checkov_report_kustomizegoat.json
  python checkov/main.py -s --framework terraform --skip-check CKV_AWS_33,CKV_AWS_41 -d repositories/terragoat/terraform/ -o json > checkov_report_terragoat_with_skip.json
  python checkov/main.py -s -d repositories/cfngoat/ -o json --quiet > checkov_report_cfngoat_quiet.json
  python checkov/main.py -s -d repositories/terragoat/terraform/ --config-file integration_tests/example_config_files/config.yaml -o json > checkov_config_report_terragoat.json

  python checkov/main.py -s -f repositories/terragoat/terraform/aws/s3.tf --bc-api-key $BC_KEY > checkov_report_s3_singlefile_api_key_terragoat.txt
  python checkov/main.py -s -d repositories/terragoat/terraform/azure/ --bc-api-key $BC_KEY > checkov_report_azuredir_api_key_terragoat.txt
#  export CHECKOV_EXPERIMENTAL_IMAGE_REFERENCING=True #cant run it on M1 mac
  python checkov/main.py -s -d integration_tests/example_workflow_file/.github/workflows/ -o json --bc-api-key $BC_KEY --include-all-checkov-policies > checkov_report_workflow_cve.json
  python checkov/main.py -s -d integration_tests/example_workflow_file/bitbucket/ -o json --bc-api-key $BC_KEY --include-all-checkov-policies > checkov_report_bitbucket_pipelines_cve.json
}

clone_repositories () {
  echo Clone Terragoat - vulnerable terraform;
  git clone https://github.com/bridgecrewio/terragoat
  test -d ./terragoat || { echo 'terragoat dir does not exist, please check your git connection and try again.'; exit 1; };

  echo Clone Cfngoat - vulnerable cloudformation;
  git clone https://github.com/bridgecrewio/cfngoat

  echo Clone Kubernetes-goat - vulnerable kubernetes;
  git clone https://github.com/madhuakula/kubernetes-goat

  echo Clone kustomize-goat - vulnerable kustomize;
  git clone https://github.com/bridgecrewio/kustomizegoat
}

delete_repositories () {
  rm -rf repositories
}

delete_reports () {
  rm -r checkov_report*
  rm -r checkov_config_report_terragoat*
  rm results.sarif
}

echo $BC_KEY
if [[ -z "$BC_KEY" ]]; then
   echo "BC_API_KEY is missing."
   exit 1
fi

echo $BC_API_URL
if [[ -z "$BC_API_URL" ]]; then
   echo "BC_API_URL is missing."
   exit 1
fi

docker run node:14.16
if [ $? -ne 0 ]; then
  echo "docker command failed."
  exit 1
fi

# Create repositories dir
mkdir repositories
cd repositories

echo "Cloning repositories"
clone_repositories

cd ..

deactivate

#activate virtual env
ENV_PATH=$(pipenv --venv)
echo $ENV_PATH
source $ENV_PATH/bin/activate

working_dir=$(pwd) # should be the path of local checkov project
export PYTHONPATH="$working_dir/checkov:$PYTHONPATH"

prepare_data

#Run integration tests.
pytest integration_tests

deactivate

echo "Deleting reports and repositories."
delete_reports
delete_repositories

