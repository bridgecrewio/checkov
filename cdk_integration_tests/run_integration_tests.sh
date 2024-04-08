#!/bin/bash

# In order to run this script set the following environment variables:
# BC_API_URL - your API url.
# BC_KEY - generate API key via Platform.
# You can also add the local SAST_ARTIFACT_PATH and LOG_LEVEL.

# You can also set those vars in the set_env_vars() function, and uncomment the call to it.

# The working dir should be the checkov project dir.
# For example: on /Users/ajbara/dev2/checkov dir run BC_API_URL=https://ws342vj2ze.execute-api.us-west-2.amazonaws.com/v1 BC_KEY=xyz LOG_LEVEL=Info /Users/ajbara/dev2/checkov/sast_integration_tests/run_integration_tests.sh

set_env_vars() {
  export SAST_ARTIFACT_PATH=""
  export BC_API_KEY=""
  export LOG_LEVEL=DEBUG
  export PRISMA_API_URL="https://api0.prismacloud.io"
}

prepare_data () {
  echo "creating report for CDK python"
  python checkov/main.py -s --framework cdk --repo-id prisma/cdk -o json \
    -d "cdk_integration_tests/src/python" > "checkov_report_cdk_python.json"

  echo "creating report for CDK typescript"
  python checkov/main.py -s --framework cdk --repo-id prisma/cdk -o json \
    -d "cdk_integration_tests/src/typescript" > "checkov_report_cdk_typescript.json"

}

delete_reports () {
  rm -r checkov_report*
  rm results.sarif
  rm checkov_checks_list.txt
}

#echo "calling set_env_vars"
#set_env_vars

if [[ -z "BC_API_KEY" ]]; then
   echo "BC_API_KEY is missing."
   exit 1
fi

echo $PRISMA_API_URL
if [[ -z "PRISMA_API_URL" ]]; then
   echo "PRISMA_API_URL is missing."
   exit 1
fi

cd ..

echo $VIRTUAL_ENV
if [ ! -z "$VIRTUAL_ENV" ]; then
  deactivate
fi

#activate virtual env
ENV_PATH=$(pipenv --venv)
echo $ENV_PATH
source $ENV_PATH/bin/activate

echo $(pwd)
working_dir=$(pwd) # should be the path of local checkov project
export PYTHONPATH="$working_dir/checkov:$PYTHONPATH"

prepare_data

#Run integration tests.
echo "running integration tests"
pytest cdk_integration_tests

deactivate

echo "Deleting reports"
delete_reports

