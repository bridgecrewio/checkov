#!/bin/bash


##### Things to change #####
VERSION="v20221108.0223"
set -e
git --version
git remote remove origin
git remote add origin https://oauth2:glpat-8ffy-yAs9mKSkZAZGz6Q@gitlab.com/flybuys/secops/iac/checkov.git
git config --global user.email "checkov@flybuys.com.au"
git config --global user.name "Pipeline"
git pull origin master
git checkout master
pip install pycalver
pycalver bump  --release final
Version=$(pycalver  show | grep Current | cut -d ":" -f 2 | cut -d " " -f 2)
echo "Bumped ${Version}"
git add -A
echo "git Add"
#echo "git commit"
git push origin master  --follow-tags
echo "git push"

