#!/bin/bash
set -e

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

set_env_vars_local_sast_report() {
  export SAVE_SAST_REPORT_LOCALLY=TRUE
}

prepare_data () {
  python checkov/main.py -s --framework sast_python -d repositories/flask --repo-id cli/flask -o json > checkov_report_sast_python.json
  python checkov/main.py -s --framework sast_java -d repositories/WebGoat --repo-id cli/WebGoat -o json > checkov_report_sast_java.json
  python checkov/main.py -s --framework sast_javascript -d repositories/axios --repo-id cli/axios -o json > checkov_report_sast_javascript.json
}

clone_repositories () {
  echo Clone flask - Python repo for SAST;
  git clone https://github.com/pallets/flask
  echo Clone WebGoat - Java repo for SAST
  git clone https://github.com/WebGoat/WebGoat
  echo Clone axios - JavaScript repo for SAST
  git clone https://github.com/axios/axios
}


delete_repositories () {
  rm -rf repositories
}

delete_reports () {
  rm -r checkov_report*
}

#set_env_vars

set_env_vars_local_sast_report

echo $BC_API_KEY
if [[ -z "BC_API_KEY" ]]; then
   echo "BC_API_KEY is missing."
   exit 1
fi

echo $PRISMA_API_URL
if [[ -z "PRISMA_API_URL" ]]; then
   echo "PRISMA_API_URL is missing."
   exit 1
fi

# Create repositories dir
mkdir repositories
cd repositories

echo "Cloning repositories"
clone_repositories

cd ..

if [ ! -z "$VIRTUAL_ENV" ]; then
  deactivate
fi

#activate virtual env
ENV_PATH=$(pipenv --venv)
echo $ENV_PATH
source $ENV_PATH/bin/activate

working_dir=$(pwd) # should be the path of local checkov project
export PYTHONPATH="$working_dir/checkov:$PYTHONPATH"

prepare_data

#Run integration tests.
echo "running integration tests"
pytest sast_integration_tests

deactivate

echo "Deleting reports and repositories."
delete_reports
delete_repositories

