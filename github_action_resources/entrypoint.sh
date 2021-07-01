#!/bin/bash

# Leverage the default env variables as described in:
# https://docs.github.com/en/actions/reference/environment-variables#default-environment-variables
if [[ $GITHUB_ACTIONS != "true" ]]
then
  checkov $@
  exit $?
fi

# Actions pass inputs as $INPUT_<input name> environmet variables
#
[[ ! -z "$INPUT_CHECK" ]] && CHECK_FLAG="--check $INPUT_CHECK"
[[ ! -z "$INPUT_SKIP_CHECK" ]] && SKIP_CHECK_FLAG="--skip-check $INPUT_SKIP_CHECK"
[[ ! -z "$INPUT_FRAMEWORK" ]] && FRAMEWORK_FLAG="--framework $INPUT_FRAMEWORK"
[[ ! -z "$INPUT_OUTPUT_FORMAT" ]] && OUTPUT_FLAG="--output $INPUT_OUTPUT_FORMAT"

if [ ! -z "$INPUT_QUIET" ] && [ "$INPUT_QUIET" = "true" ]; then
  QUIET_FLAG="--quiet"
fi

if [ ! -z "$INPUT_DOWNLOAD_EXTERNAL_MODULES" ] && [ "$INPUT_DOWNLOAD_EXTERNAL_MODULES" = "true" ]; then
  DOWNLOAD_EXTERNAL_MODULES_FLAG="--download-external-modules true"
fi

if [ ! -z "$INPUT_SOFT_FAIL" ] && [ "$INPUT_SOFT_FAIL" =  "true" ]; then
  SOFT_FAIL_FLAG="--soft-fail"
fi

if [ ! -z "$INPUT_LOG_LEVEL" ]; then
  export LOG_LEVEL=$INPUT_LOG_LEVEL
fi

EXTCHECK_DIRS_FLAG=""
if [ ! -z "$INPUT_EXTERNAL_CHECKS_DIRS" ]; then
  IFS=', ' read -r -a extchecks_dir <<< "$INPUT_EXTERNAL_CHECKS_DIRS"
  for d in "${extchecks_dir[@]}"
  do
    EXTCHECK_DIRS_FLAG="$EXTCHECK_DIRS_FLAG --external-checks-dir $d"
  done
fi

EXTCHECK_REPOS_FLAG=""
if [ ! -z "$INPUT_EXTERNAL_CHECKS_REPOS" ]; then
  IFS=', ' read -r -a extchecks_git <<< "$INPUT_EXTERNAL_CHECKS_REPOS"
  for repo in "${extchecks_git[@]}"
  do
    EXTCHECK_REPOS_FLAG="$EXTCHECK_REPOS_FLAG --external-checks-git $repo"
  done
fi

echo "input_soft_fail:$INPUT_SOFT_FAIL"
matcher_path=`pwd`/checkov-problem-matcher.json
if [ ! -z "$INPUT_SOFT_FAIL" ]; then
    cp /usr/local/lib/checkov-problem-matcher.json "$matcher_path"
    else
    cp /usr/local/lib/checkov-problem-matcher-softfail.json "$matcher_path"
fi

echo "::add-matcher::checkov-problem-matcher.json"
echo "running checkov on directory: $1"
checkov -d $INPUT_DIRECTORY $CHECK_FLAG $SKIP_CHECK_FLAG $QUIET_FLAG $SOFT_FAIL_FLAG $FRAMEWORK_FLAG $EXTCHECK_DIRS_FLAG $EXTCHECK_REPOS_FLAG $OUTPUT_FLAG $DOWNLOAD_EXTERNAL_MODULES_FLAG
CHECKOV_EXIT_CODE=$?
if [ ! -z "$INPUT_DOWNLOAD_EXTERNAL_MODULES" ] && [ "$INPUT_DOWNLOAD_EXTERNAL_MODULES" = "true" ]; then
  echo "Cleaning up $INPUT_DIRECTORY/.external_modules directory"
  #This directory must be removed here for the self hosted github runners run as non-root user.
  rm -fr $INPUT_DIRECTORY/.external_modules
  exit $CHECKOV_EXIT_CODE
fi
exit $CHECKOV_EXIT_CODE
