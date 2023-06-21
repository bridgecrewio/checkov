#!/bin/sh
################################################################################
# build checkov3 locally
################################################################################

VENV_NAME="sast-checkov3"

# install virtualenv
printf "\e[34mInstalling virtualenv\e[0m\n"
python3 -m pip install --user virtualenv

# create virtual env
printf "\e[34mCreating virtualenv %s\e[0m\n" "$VENV_NAME"
python3 -m venv $VENV_NAME

# activate venv
printf "\e[34mActivating virtualenv %s\e[0m\n" "$VENV_NAME"
source $VENV_NAME/bin/activate

# install/upgrade pip
printf "\e[34mUpgrading pip\e[0m\n"
python3 -m pip install --upgrade pip

printf "\e[34mInstalling local package\e[0m\n"
pip install -e .


printf "\e[34mIf installation was successful you should see the version is '(checkov3)<version>'\e[0m\n"
$VENV_NAME/bin/checkov -v

printf "\e[32mInstallation complete!!\nTo run checkov simply run \e[1m%s/bin/checkov -d ...\n" "$VENV_NAME"