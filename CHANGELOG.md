# CHANGELOG

## [Unreleased](https://github.com/bridgecrewio/checkov/compare/2.3.302...HEAD)

## [2.3.302](https://github.com/bridgecrewio/checkov/compare/2.3.301...2.3.302) - 2023-06-25

### Bug Fix

- **terraform:** add missing AWS RDS CA certificate identifiers for aws_db_instance resource - [#5247](https://github.com/bridgecrewio/checkov/pull/5247)

## [2.3.301](https://github.com/bridgecrewio/checkov/compare/2.3.299...2.3.301) - 2023-06-22

### Feature

- **general:** remove log from parallel common - [#5244](https://github.com/bridgecrewio/checkov/pull/5244)

### Platform

- **general:** Fix local repo generated name if ends with / - [#5243](https://github.com/bridgecrewio/checkov/pull/5243)

## [2.3.299](https://github.com/bridgecrewio/checkov/compare/2.3.296...2.3.299) - 2023-06-21

### Feature

- **terraform:** ensure kms key policy is defined - [#5235](https://github.com/bridgecrewio/checkov/pull/5235)

### Bug Fix

- **sca:** fix wrongly invoked Image Referencer scanning when scanning a single file - [#5237](https://github.com/bridgecrewio/checkov/pull/5237)
- **terraform_plan:** add terraform plan vertices to terraform graph if not exist - [#5230](https://github.com/bridgecrewio/checkov/pull/5230)

## [2.3.296](https://github.com/bridgecrewio/checkov/compare/2.3.294...2.3.296) - 2023-06-19

### Bug Fix

- **dockerfile:** negative `is_dockerfile()` lookup on `.dockerignore` suffix - [#5219](https://github.com/bridgecrewio/checkov/pull/5219)
- **terraform:** fix empty value issue for CKV_GIT_4 - [#5222](https://github.com/bridgecrewio/checkov/pull/5222)

### Documentation

- **graph:** add jsonpath custom policy example - [#5221](https://github.com/bridgecrewio/checkov/pull/5221)

## [2.3.294](https://github.com/bridgecrewio/checkov/compare/2.3.292...2.3.294) - 2023-06-15

### Feature

- **gha:** add skip_path flag to GHA and allow multiple values in var_file - [#5213](https://github.com/bridgecrewio/checkov/pull/5213)
- **sca:** add root package name and version to csv sbom - [#5211](https://github.com/bridgecrewio/checkov/pull/5211)

## [2.3.292](https://github.com/bridgecrewio/checkov/compare/2.3.289...2.3.292) - 2023-06-14

### Feature

- **arm:** Handle another structure for SQL retention policy - [#5210](https://github.com/bridgecrewio/checkov/pull/5210)

### Bug Fix

- **secrets:** limit line length for custom secrets - [#5208](https://github.com/bridgecrewio/checkov/pull/5208)
- **terraform:** Update GCP checks for plan files - [#5197](https://github.com/bridgecrewio/checkov/pull/5197)

## [2.3.289](https://github.com/bridgecrewio/checkov/compare/2.3.287...2.3.289) - 2023-06-13

### Feature

- **sca:** removing the using of the constant CHECKOV_DISPLAY_REGISTRY_URL - [#5204](https://github.com/bridgecrewio/checkov/pull/5204)

## [2.3.287](https://github.com/bridgecrewio/checkov/compare/2.3.285...2.3.287) - 2023-06-11

### Feature

- **general:** add checkov_diff pre-commit hook for scanning all changed files - [#5192](https://github.com/bridgecrewio/checkov/pull/5192)

### Bug Fix

- **cloudformation:** fix CKV_AWS_33 to consider deny statements - [#5193](https://github.com/bridgecrewio/checkov/pull/5193)

### Documentation

- **general:** Update pre-commit.md - [#5190](https://github.com/bridgecrewio/checkov/pull/5190)

## [2.3.285](https://github.com/bridgecrewio/checkov/compare/2.3.283...2.3.285) - 2023-06-08

### Feature

- **arm:** and bicep: Ensure that Azure Front Door uses WAF in "Detection" or "Prevention" modes CKV_AZURE_123 - [#5049](https://github.com/bridgecrewio/checkov/pull/5049)

### Bug Fix

- **general:** handle cloned checks filtered via labels - [#5188](https://github.com/bridgecrewio/checkov/pull/5188)
- **terraform:** adjust CKV_AZURE_6 to comply with new provider version - [#5189](https://github.com/bridgecrewio/checkov/pull/5189)

## [2.3.283](https://github.com/bridgecrewio/checkov/compare/2.3.281...2.3.283) - 2023-06-07

### Feature

- **arm:** Handle arm db servers 2021 05 01 - [#5187](https://github.com/bridgecrewio/checkov/pull/5187)
- **terraform:** Mark unresolved tf function calls as unresolved - [#5186](https://github.com/bridgecrewio/checkov/pull/5186)

### Documentation

- **general:** Add Enforcement CLI Command - [#5185](https://github.com/bridgecrewio/checkov/pull/5185)

## [2.3.281](https://github.com/bridgecrewio/checkov/compare/2.3.278...2.3.281) - 2023-06-06

### Feature

- **terraform_plan:** Expose field changes to python checks - [#5112](https://github.com/bridgecrewio/checkov/pull/5112)

### Bug Fix

- **general:** Check that the result is not None before extracting vars in cli multiprocess runs - [#5183](https://github.com/bridgecrewio/checkov/pull/5183)
- **general:** Correctly handle cli graphs in case we run with multiprocessing - [#5177](https://github.com/bridgecrewio/checkov/pull/5177)

## [2.3.278](https://github.com/bridgecrewio/checkov/compare/2.3.276...2.3.278) - 2023-06-05

### Bug Fix

- **kubernetes:** dont' fail if spec is missing and default value is set to the fix value. - [#5167](https://github.com/bridgecrewio/checkov/pull/5167)

## [2.3.276](https://github.com/bridgecrewio/checkov/compare/2.3.273...2.3.276) - 2023-06-04

### Feature

- **arm:** ARM and bicep checks for CKV_AZURE_121 - [#5029](https://github.com/bridgecrewio/checkov/pull/5029)
- **terraform:** Ensure Application Gateway defines secure SSL protocols CKV_AZURE_217, 218 - [#5027](https://github.com/bridgecrewio/checkov/pull/5027)
- **terraform:** Ensure Azure firewall sets threatintelMode to Deny - [#5013](https://github.com/bridgecrewio/checkov/pull/5013)
- **terraform:** Ensure firewall defines a policy - [#5038](https://github.com/bridgecrewio/checkov/pull/5038)
- **terraform:** Ensure Firewall policy has IDPS mode as deny - [#5039](https://github.com/bridgecrewio/checkov/pull/5039)

### Bug Fix

- **dockerfile:** support platform flag in CKV_DOCKER_11 - [#5170](https://github.com/bridgecrewio/checkov/pull/5170)
- **terraform:** support condition in IAM policy data blocks - [#5171](https://github.com/bridgecrewio/checkov/pull/5171)
- **terraform:** Unable to download Terraform modules from JFrog Artifactory - [#5155](https://github.com/bridgecrewio/checkov/pull/5155)

## [2.3.273](https://github.com/bridgecrewio/checkov/compare/2.3.267...2.3.273) - 2023-06-01

### Feature

- **ansible:** add support of inline suppression for Ansible graph checks - [#5143](https://github.com/bridgecrewio/checkov/pull/5143)
- **terraform:** Use just AWS regex to check EC2Credentials - [#5159](https://github.com/bridgecrewio/checkov/pull/5159)

### Bug Fix

- **cloudformation:** fix evaluate_default_refs func in cfn - [#5164](https://github.com/bridgecrewio/checkov/pull/5164)
- **general:** fix SARIF output related to security-severity field - [#5160](https://github.com/bridgecrewio/checkov/pull/5160)
- **terraform:** adjust CKV_AWS_85 to only look for one log type to pass - [#5162](https://github.com/bridgecrewio/checkov/pull/5162)
- **terraform:** update latest major version of Postgres to v15 - [#5163](https://github.com/bridgecrewio/checkov/pull/5163)

### Platform

- **general:** Add no upload flag and report contributors for all API key runs - [#5052](https://github.com/bridgecrewio/checkov/pull/5052)

## [2.3.267](https://github.com/bridgecrewio/checkov/compare/2.3.264...2.3.267) - 2023-05-31

### Bug Fix

- **kubernetes:** fix extracting k8s nested resources - [#5146](https://github.com/bridgecrewio/checkov/pull/5146)
- **sca:** suppression - fix unit testing - [#5158](https://github.com/bridgecrewio/checkov/pull/5158)
- **sca:** suppression is not working on SCA packages - [#5156](https://github.com/bridgecrewio/checkov/pull/5156)

## [2.3.264](https://github.com/bridgecrewio/checkov/compare/2.3.261...2.3.264) - 2023-05-30

### Feature

- **terraform:** don't fail CKV_AWS_2 on un-rendered value - [#5147](https://github.com/bridgecrewio/checkov/pull/5147)
- **terraform:** Foreach support resources edges - [#5145](https://github.com/bridgecrewio/checkov/pull/5145)

### Bug Fix

- **terraform:** exclude unrestrictable actions in CKV_AWS_355 and CKV_AWS_356 - [#5135](https://github.com/bridgecrewio/checkov/pull/5135)

### Documentation

- **general:** Update operators with examples - [#5137](https://github.com/bridgecrewio/checkov/pull/5137)

## [2.3.261](https://github.com/bridgecrewio/checkov/compare/2.3.259...2.3.261) - 2023-05-28

### Feature

- **general:** Added computation of git_root_path to igraph serialization - [#5107](https://github.com/bridgecrewio/checkov/pull/5107)
- **sca:** adding validation for the file_line_number - [#5132](https://github.com/bridgecrewio/checkov/pull/5132)
- **terraform:** foreach remove error from info log. - [#5139](https://github.com/bridgecrewio/checkov/pull/5139)

### Bug Fix

- **terraform:** Should use UNKNOWN rather than skipped - [#5136](https://github.com/bridgecrewio/checkov/pull/5136)

## [2.3.259](https://github.com/bridgecrewio/checkov/compare/2.3.257...2.3.259) - 2023-05-24

### Feature

- **terraform:** extend CKV2_AWS_5 with new resources - [#5129](https://github.com/bridgecrewio/checkov/pull/5129)
- **terraform:** IAM limit resource access - [#5015](https://github.com/bridgecrewio/checkov/pull/5015)

### Bug Fix

- **kustomize:** fix empty kustomize file crash - [#5131](https://github.com/bridgecrewio/checkov/pull/5131)

### Platform

- **general:** SBOM lines numbers adjusting  - [#5127](https://github.com/bridgecrewio/checkov/pull/5127)

## [2.3.257](https://github.com/bridgecrewio/checkov/compare/2.3.251...2.3.257) - 2023-05-23

### Feature

- **sca:** adding the risk factor v2 to the vulnerability details - [#5108](https://github.com/bridgecrewio/checkov/pull/5108)
- **sca:** dockerfile image-referencer fixes - [#5120](https://github.com/bridgecrewio/checkov/pull/5120)
- **secrets:** Add new pre-commit hook for secrets - [#5103](https://github.com/bridgecrewio/checkov/pull/5103)
- **terraform:** add check to look at star resources - [#4996](https://github.com/bridgecrewio/checkov/pull/4996)

### Bug Fix

- **gitlab:** Skipping image blocks without name attribute - [#5126](https://github.com/bridgecrewio/checkov/pull/5126)
- **terraform:** fix terraform variable rendering for provider alias - [#5124](https://github.com/bridgecrewio/checkov/pull/5124)

### Platform

- **general:** Enhancing Sarif output with Security Severity Level - [#5074](https://github.com/bridgecrewio/checkov/pull/5074)

## [2.3.251](https://github.com/bridgecrewio/checkov/compare/2.3.247...2.3.251) - 2023-05-21

### Feature

- **secrets:** add jwt detector to the secret runner - [#5116](https://github.com/bridgecrewio/checkov/pull/5116)
- **terraform:** Adding yaml based build time policies for corresponding PC runtime policies - [#5089](https://github.com/bridgecrewio/checkov/pull/5089)
- **terraform:** AWS Ensure RDS performance insights uses a CMK - [#4985](https://github.com/bridgecrewio/checkov/pull/4985)
- **terraform:** NACL should restrict port ingress - [#4976](https://github.com/bridgecrewio/checkov/pull/4976)
- **terraform:** RDS Enable Performance insights - [#4983](https://github.com/bridgecrewio/checkov/pull/4983)

### Bug Fix

- **dockerfile:** improve update searching in CKV_DOCKER_5 - [#5115](https://github.com/bridgecrewio/checkov/pull/5115)

### Documentation

- **general:** Update CLI Command Reference.md - [#5114](https://github.com/bridgecrewio/checkov/pull/5114)

## [2.3.247](https://github.com/bridgecrewio/checkov/compare/2.3.245...2.3.247) - 2023-05-18

### Feature

- **general:** add SPDX output - [#5104](https://github.com/bridgecrewio/checkov/pull/5104)
- **kubernetes:** seperate service acoount builder to improve performance - [#5093](https://github.com/bridgecrewio/checkov/pull/5093)
- **sca:** showing line numbers in the cli output for csv - [#5096](https://github.com/bridgecrewio/checkov/pull/5096)
- **sca:** showing line numbers in the cli output for licenses - [#5098](https://github.com/bridgecrewio/checkov/pull/5098)

## [2.3.245](https://github.com/bridgecrewio/checkov/compare/2.3.243...2.3.245) - 2023-05-16

### Feature

- **dockerfile:** Support docker graph check skips - [#5085](https://github.com/bridgecrewio/checkov/pull/5085)
- **sca:** using the lines in the directly in the record, rather than in the "vulnerability_details" + having it in ExtraResources - [#5092](https://github.com/bridgecrewio/checkov/pull/5092)

## [2.3.243](https://github.com/bridgecrewio/checkov/compare/2.3.240...2.3.243) - 2023-05-15

### Feature

- **kubernetes:** Improve k8s perf - [#5083](https://github.com/bridgecrewio/checkov/pull/5083)
- **terraform:** EMR -  At rest local disk, EBS and in transit encryption checks - [#4968](https://github.com/bridgecrewio/checkov/pull/4968)

### Bug Fix

- **kubernetes:** add mini k8s parser for invalid templates - [#5088](https://github.com/bridgecrewio/checkov/pull/5088)
- **terraform:** handle false-positives for Route53ZoneEnableDNSSECSigning - [#5084](https://github.com/bridgecrewio/checkov/pull/5084)

### Platform

- **general:** Add lines to SBOM  - [#5078](https://github.com/bridgecrewio/checkov/pull/5078)
- **graph:** upload graphs to the platform - [#5073](https://github.com/bridgecrewio/checkov/pull/5073)

## [2.3.240](https://github.com/bridgecrewio/checkov/compare/2.3.239...2.3.240) - 2023-05-14

### Bug Fix

- **terraform:** skip invalid multiple modules names - [#5079](https://github.com/bridgecrewio/checkov/pull/5079)

## [2.3.239](https://github.com/bridgecrewio/checkov/compare/2.3.238...2.3.239) - 2023-05-12

### Bug Fix

- **sca:** only run image referencer with sca_image framework - [#5081](https://github.com/bridgecrewio/checkov/pull/5081)

## [2.3.238](https://github.com/bridgecrewio/checkov/compare/2.3.237...2.3.238) - 2023-05-11

### Feature

- **kustomize:** Support inline skips for Kubernetes graph checks - [#5070](https://github.com/bridgecrewio/checkov/pull/5070)

## [2.3.237](https://github.com/bridgecrewio/checkov/compare/2.3.234...2.3.237) - 2023-05-10

### Bug Fix

- **secrets:** add filter for suppressed custom secret checks - [#5068](https://github.com/bridgecrewio/checkov/pull/5068)
- **secrets:** exclude Kubernetes secretName from secret scanning - [#5071](https://github.com/bridgecrewio/checkov/pull/5071)
- **secrets:** omit the code line - [#5075](https://github.com/bridgecrewio/checkov/pull/5075)

## [2.3.234](https://github.com/bridgecrewio/checkov/compare/2.3.231...2.3.234) - 2023-05-09

### Feature

- **terraform:** Added caller_file_path and caller_file_line_range to reduced report - [#5062](https://github.com/bridgecrewio/checkov/pull/5062)
- **terraform:** AWS IAM don't generate root credentials 348 - [#4966](https://github.com/bridgecrewio/checkov/pull/4966)
- **terraform:** Ensure Neptune cluster is encrypted with a CMK CKV_AWS_347 - [#4965](https://github.com/bridgecrewio/checkov/pull/4965)

### Bug Fix

- **terraform:** fix SQS encryption check CKV_AWS_27 - [#5065](https://github.com/bridgecrewio/checkov/pull/5065)

### Documentation

- **general:** Fix some links - [#5064](https://github.com/bridgecrewio/checkov/pull/5064)
- **general:** update Python custom checks docs - [#5054](https://github.com/bridgecrewio/checkov/pull/5054)

## [2.3.231](https://github.com/bridgecrewio/checkov/compare/2.3.227...2.3.231) - 2023-05-08

### Feature

- **terraform:** aws ensure delete protection for firewalls 344 - [#4870](https://github.com/bridgecrewio/checkov/pull/4870)
- **terraform:** check that WAF rules have an action 342 - [#4806](https://github.com/bridgecrewio/checkov/pull/4806)
- **terraform:** Ensure encryption for firewall uses a CMK CKV_AWS_345 - [#4871](https://github.com/bridgecrewio/checkov/pull/4871)
- **terraform:** Ensure Network firewall policy defines a encryption configuration that uses a CMK - CKV_AWS_346 - [#4877](https://github.com/bridgecrewio/checkov/pull/4877)

### Bug Fix

- **kubernetes:** Update ckv_k8s_31 - [#4991](https://github.com/bridgecrewio/checkov/pull/4991)

## [2.3.227](https://github.com/bridgecrewio/checkov/compare/2.3.224...2.3.227) - 2023-05-07

### Feature

- **general:** include missing files in save repository - [#5056](https://github.com/bridgecrewio/checkov/pull/5056)
- **terraform:** launch config/template Ensure metadata hop =1 341 - [#4817](https://github.com/bridgecrewio/checkov/pull/4817)
- **terraform:** Update CKV_AZURE_43 StorageAccountName.py VARIABLE_REFS - [#5045](https://github.com/bridgecrewio/checkov/pull/5045)

### Bug Fix

- **arm:** enabled is not true - [#5051](https://github.com/bridgecrewio/checkov/pull/5051)
- **cloudformation:** Enable ALB to support tls1.3 policies #4962 - [#5035](https://github.com/bridgecrewio/checkov/pull/5035)
- **secrets:** add handling of unicode error - [#5055](https://github.com/bridgecrewio/checkov/pull/5055)

## [2.3.224](https://github.com/bridgecrewio/checkov/compare/2.3.223...2.3.224) - 2023-05-05

### Platform

- **general:** Catch None responses from BE - [#5033](https://github.com/bridgecrewio/checkov/pull/5033)

## [2.3.223](https://github.com/bridgecrewio/checkov/compare/2.3.220...2.3.223) - 2023-05-04

### Feature

- **terraform:** Elastic beanstalk uses managed updates and fixes the EB check while i… 340 - [#4816](https://github.com/bridgecrewio/checkov/pull/4816)

### Bug Fix

- **secrets:** don't scan images in git history - [#5040](https://github.com/bridgecrewio/checkov/pull/5040)
- **terraform:** fix foreach render value for lookup - [#5037](https://github.com/bridgecrewio/checkov/pull/5037)
- **terraform:** Handle entity context for for_each resources - [#5036](https://github.com/bridgecrewio/checkov/pull/5036)

## [2.3.220](https://github.com/bridgecrewio/checkov/compare/2.3.214...2.3.220) - 2023-05-03

### Feature

- **secrets:** open the feature - scan git history - [#5022](https://github.com/bridgecrewio/checkov/pull/5022)
- **terraform:** Set TF Modules for_each env var to true - [#5021](https://github.com/bridgecrewio/checkov/pull/5021)
- **terraform:** Set TF modules for_each env vars as True - [#4794](https://github.com/bridgecrewio/checkov/pull/4794)

### Bug Fix

- **secrets:** add filter for suppressed custom secret checks - [#5016](https://github.com/bridgecrewio/checkov/pull/5016)
- **terraform:** improve attribute performance - [#5014](https://github.com/bridgecrewio/checkov/pull/5014)
- **terraform:** Update CKV_AWS_338 message and retention check for 0 - [#5018](https://github.com/bridgecrewio/checkov/pull/5018)
- **terraform:** Update CKV2_AZURE_33 to remove checks on unrelated conditions - [#5020](https://github.com/bridgecrewio/checkov/pull/5020)

## [2.3.214](https://github.com/bridgecrewio/checkov/compare/2.3.212...2.3.214) - 2023-05-02

### Bug Fix

- **secrets:** Adding quote to required secret in case needed - [#5008](https://github.com/bridgecrewio/checkov/pull/5008)
- **secrets:** change color of invalid secret message - [#5007](https://github.com/bridgecrewio/checkov/pull/5007)

### Platform

- **general:** upload checks code_block to report - [#5001](https://github.com/bridgecrewio/checkov/pull/5001)

## [2.3.212](https://github.com/bridgecrewio/checkov/compare/2.3.205...2.3.212) - 2023-04-30

### Feature

- **kubernetes:** support suppressing custom K8s policies - [#4990](https://github.com/bridgecrewio/checkov/pull/4990)
- **terraform:** AWS EKS Use only platform supported versions 339 - [#4810](https://github.com/bridgecrewio/checkov/pull/4810)
- **terraform:** Azure APIm backend uses only HTTPS - [#4811](https://github.com/bridgecrewio/checkov/pull/4811)
- **terraform:** Ensure Cloudwatch retention is a year or more 338 - [#4799](https://github.com/bridgecrewio/checkov/pull/4799)
- **terraform:** remove redundant foreach deepcopy - [#4982](https://github.com/bridgecrewio/checkov/pull/4982)

### Bug Fix

- **secrets:** fix missing history results when history store is used - [#4992](https://github.com/bridgecrewio/checkov/pull/4992)
- **terraform:** secret- also check user data in launch config and template - [#4969](https://github.com/bridgecrewio/checkov/pull/4969)

## [2.3.205](https://github.com/bridgecrewio/checkov/compare/2.3.204...2.3.205) - 2023-04-28

### Bug Fix

- **gitlab:** fix resource id parsing recursive - [#4987](https://github.com/bridgecrewio/checkov/pull/4987)

### Documentation

- **terraform:** fix docs formatting - [#4988](https://github.com/bridgecrewio/checkov/pull/4988)

## [2.3.204](https://github.com/bridgecrewio/checkov/compare/2.3.199...2.3.204) - 2023-04-27

### Feature

- **terraform:** add support for private terraform registries - [#4964](https://github.com/bridgecrewio/checkov/pull/4964)
- **terraform:** remove cross varaibles bad list comprehension - [#4948](https://github.com/bridgecrewio/checkov/pull/4948)

### Bug Fix

- **general:** log all returned enforcement rules for debugging - [#4989](https://github.com/bridgecrewio/checkov/pull/4989)
- **general:** remove invalid URLs in GitLab SAST output - [#4960](https://github.com/bridgecrewio/checkov/pull/4960)
- **secrets:** change default value of secret values to empty strings - [#4973](https://github.com/bridgecrewio/checkov/pull/4973)
- **terraform:** Added a condition to not override source module object for old parser - [#4975](https://github.com/bridgecrewio/checkov/pull/4975)

## [2.3.199](https://github.com/bridgecrewio/checkov/compare/2.3.194...2.3.199) - 2023-04-24

### Feature

- **terraform:** Ensure container defines a readonly root drive 336  - [#4788](https://github.com/bridgecrewio/checkov/pull/4788)
- **terraform:** ensure pidmode is not set to host 335  - [#4786](https://github.com/bridgecrewio/checkov/pull/4786)
- **terraform:** Ensure SSM params are encrypted using a CMK 337  - [#4789](https://github.com/bridgecrewio/checkov/pull/4789)
- **terraform:** Network firewall must define a logging configuration CKV2_AWS_63 - [#4872](https://github.com/bridgecrewio/checkov/pull/4872)
- **terraform:** Reduce module loading in TF Parser - [#4959](https://github.com/bridgecrewio/checkov/pull/4959)

### Bug Fix

- **kustomize:** fix image_referencer paths - [#4898](https://github.com/bridgecrewio/checkov/pull/4898)
- **terraform:** support TF provider v3 for lifecycle existence check - [#4952](https://github.com/bridgecrewio/checkov/pull/4952)

### Documentation

- **terraform_plan:** Add Deep Analysis to docs - [#4950](https://github.com/bridgecrewio/checkov/pull/4950)

## [2.3.194](https://github.com/bridgecrewio/checkov/compare/2.3.192...2.3.194) - 2023-04-23

### Feature

- **general:** deserialize report & record from json  - [#4947](https://github.com/bridgecrewio/checkov/pull/4947)
- **sca:** fix extract fix version in sbom report - [#4936](https://github.com/bridgecrewio/checkov/pull/4936)
- **terraform:** cross variable performance improvement - [#4946](https://github.com/bridgecrewio/checkov/pull/4946)

### Bug Fix

- **github:** make GH Actions delimiter unique in multiline env vars - [#4938](https://github.com/bridgecrewio/checkov/pull/4938)

## [2.3.192](https://github.com/bridgecrewio/checkov/compare/2.3.187...2.3.192) - 2023-04-20

### Feature

- **general:** add policy-metadata-filter to gh action - [#4941](https://github.com/bridgecrewio/checkov/pull/4941)
- **secrets:** support first commit results - [#4927](https://github.com/bridgecrewio/checkov/pull/4927)
- **terraform:** Used generator instead of list comprehension to improve performance for large graphs - [#4939](https://github.com/bridgecrewio/checkov/pull/4939)

### Bug Fix

- **terraform:** make the ECS cluster logging check more resilient - [#4942](https://github.com/bridgecrewio/checkov/pull/4942)
- **terraform:** remove invalid Terraform module reference support - [#4931](https://github.com/bridgecrewio/checkov/pull/4931)
- **terraform:** support null values in list of dicts - [#4937](https://github.com/bridgecrewio/checkov/pull/4937)

### Documentation

- **bitbucket:** Update Bitbucket documentation to match the code. - [#4934](https://github.com/bridgecrewio/checkov/pull/4934)
- **sca:** Add more ways to skip CVEs - [#4928](https://github.com/bridgecrewio/checkov/pull/4928)

## [2.3.187](https://github.com/bridgecrewio/checkov/compare/2.3.183...2.3.187) - 2023-04-19

### Feature

- **general:** 3D policies syntax refactor - [#4865](https://github.com/bridgecrewio/checkov/pull/4865)
- **secrets:** support scanning of secrets in hidden paths - [#4925](https://github.com/bridgecrewio/checkov/pull/4925)

### Bug Fix

- **secrets:** Revert timeout in unix to work with signals - [#4932](https://github.com/bridgecrewio/checkov/pull/4932)
- **secrets:** timeout in unix to work with signals - [#4933](https://github.com/bridgecrewio/checkov/pull/4933)

### Documentation

- **secrets:** Add readme file for Git History - [#4913](https://github.com/bridgecrewio/checkov/pull/4913)

## [2.3.183](https://github.com/bridgecrewio/checkov/compare/2.3.176...2.3.183) - 2023-04-18

### Feature

- **sca:** add is public fix version to sbom report  - [#4915](https://github.com/bridgecrewio/checkov/pull/4915)
- **secrets:** add more files to ignore list in git history - [#4912](https://github.com/bridgecrewio/checkov/pull/4912)
- **terraform:** Ensure that container definition is not privileged 334 - [#4779](https://github.com/bridgecrewio/checkov/pull/4779)
- **terraform:** TF provider check support - [#4911](https://github.com/bridgecrewio/checkov/pull/4911)

### Bug Fix

- **general:** Dedup results contain multiple identical images if using template syntax - [#4924](https://github.com/bridgecrewio/checkov/pull/4924)
- **general:** fix wrong abs path in IR record - [#4919](https://github.com/bridgecrewio/checkov/pull/4919)
- **secrets:** Save fetched policy destination from current work dir to temp - [#4914](https://github.com/bridgecrewio/checkov/pull/4914)
- **secrets:** timeout in unix to work with signals - [#4920](https://github.com/bridgecrewio/checkov/pull/4920)
- **terraform:** Fix for_each flow conditions - [#4918](https://github.com/bridgecrewio/checkov/pull/4918)
- **terraform:** make sure K8s volume is a dict - [#4917](https://github.com/bridgecrewio/checkov/pull/4917)

## [2.3.176](https://github.com/bridgecrewio/checkov/compare/2.3.171...2.3.176) - 2023-04-17

### Feature

- **arm:** add Storage accounts disallow public access check for ARM - [#4906](https://github.com/bridgecrewio/checkov/pull/4906)
- **dockerfile:** Add CKV2_DOCKER_16 for PIP_TRUSTED_HOST - [#4893](https://github.com/bridgecrewio/checkov/pull/4893)
- **sca:** add is private fix version to sca output - [#4891](https://github.com/bridgecrewio/checkov/pull/4891)

### Bug Fix

- **secrets:** fix absolute file path cases - [#4901](https://github.com/bridgecrewio/checkov/pull/4901)
- **terraform:** fix foreach count is none bug - [#4907](https://github.com/bridgecrewio/checkov/pull/4907)
- **terraform:** limit RDS cluster audit logging to MySQL engine - [#4897](https://github.com/bridgecrewio/checkov/pull/4897)
- **terraform:** remove duplicate call to convert graph vertices - [#4909](https://github.com/bridgecrewio/checkov/pull/4909)
- **terraform:** remove local blocks with just line number - [#4902](https://github.com/bridgecrewio/checkov/pull/4902)

## [2.3.171](https://github.com/bridgecrewio/checkov/compare/2.3.165...2.3.171) - 2023-04-16

### Feature

- **secrets:** improve timing git history - [#4890](https://github.com/bridgecrewio/checkov/pull/4890)
- **terraform:** add support for list of dicts in for loop - [#4895](https://github.com/bridgecrewio/checkov/pull/4895)

### Bug Fix

- **cloudformation:** fix invalid fn sub param in cfn - [#4900](https://github.com/bridgecrewio/checkov/pull/4900)
- **secrets:** fix error if writing to file when don't have access - [#4896](https://github.com/bridgecrewio/checkov/pull/4896)
- **secrets:** fix None in file name - [#4899](https://github.com/bridgecrewio/checkov/pull/4899)
- **secrets:** reduce false positives in yaml files - case of serverless and secretmanager - [#4892](https://github.com/bridgecrewio/checkov/pull/4892)

## [2.3.165](https://github.com/bridgecrewio/checkov/compare/2.3.160...2.3.165) - 2023-04-13

### Feature

- **terraform:** ECS Service should not auto assign public IPs 333  - [#4777](https://github.com/bridgecrewio/checkov/pull/4777)
- **terraform:** EFS access points should define a user and a path 329-330  - [#4768](https://github.com/bridgecrewio/checkov/pull/4768)
- **terraform:** Ensure ECS Fargate uses latest version 332 - [#4775](https://github.com/bridgecrewio/checkov/pull/4775)
- **terraform:** Transit gateway should not be set  up to autoaccept any VPC 331  - [#4770](https://github.com/bridgecrewio/checkov/pull/4770)

### Bug Fix

- **general:** fix duplicate sarif output - [#4886](https://github.com/bridgecrewio/checkov/pull/4886)
- **secrets:** fix slicing in githistory  - [#4889](https://github.com/bridgecrewio/checkov/pull/4889)
- **terraform:** exclude GCP asymmetric keys from key rotation - [#4879](https://github.com/bridgecrewio/checkov/pull/4879)
- **terraform:** Paid is now standard - [#4880](https://github.com/bridgecrewio/checkov/pull/4880)
- **terraform:** support empty filter in S3 lifecycle config - [#4875](https://github.com/bridgecrewio/checkov/pull/4875)

## [2.3.160](https://github.com/bridgecrewio/checkov/compare/2.3.158...2.3.160) - 2023-04-11

### Bug Fix

- **general:** catch unexpected errors when querying OpenAI - [#4883](https://github.com/bridgecrewio/checkov/pull/4883)

## [2.3.158](https://github.com/bridgecrewio/checkov/compare/2.3.155...2.3.158) - 2023-04-10

### Feature

- **secrets:** Add fields to record of secrets in git history - [#4838](https://github.com/bridgecrewio/checkov/pull/4838)

### Bug Fix

- **terraform_plan:** Handled TFDefinitionKey in plan runner as well - [#4864](https://github.com/bridgecrewio/checkov/pull/4864)

## [2.3.155](https://github.com/bridgecrewio/checkov/compare/2.3.152...2.3.155) - 2023-04-09

### Feature

- **cloudformation:** support inline suppression of CFN graph checks - [#4843](https://github.com/bridgecrewio/checkov/pull/4843)
- **terraform:** Aurora DB should enable backtrack - [#4739](https://github.com/bridgecrewio/checkov/pull/4739)
- **terraform:** Desync must be set to defensive or strictest - [#4766](https://github.com/bridgecrewio/checkov/pull/4766)
- **terraform:** Ensure that RDS clusters are encrypted using a CMK - [#4742](https://github.com/bridgecrewio/checkov/pull/4742)
- **terraform:** RDS Cluster - make sure rds cluster defined defaults for logging and audit logging - [#4736](https://github.com/bridgecrewio/checkov/pull/4736)

### Bug Fix

- **general:** be more forgiving of skipped checks without comment - [#4844](https://github.com/bridgecrewio/checkov/pull/4844)
- **terraform:** default case should pass for auto updates - [#4847](https://github.com/bridgecrewio/checkov/pull/4847)
- **terraform:** False negative for CKV_AZURE_179 - [#4846](https://github.com/bridgecrewio/checkov/pull/4846)
- **terraform:** Only update config if len is bigger than 0 - [#4855](https://github.com/bridgecrewio/checkov/pull/4855)

## [2.3.152](https://github.com/bridgecrewio/checkov/compare/2.3.150...2.3.152) - 2023-04-04

### Feature

- **dockerfile:** Add CKV2_DOCKER_15 for yum-config-manager sslverify - [#4622](https://github.com/bridgecrewio/checkov/pull/4622)

### Bug Fix

- **cloudformation:** Security Group check now work for ranges and strings - [#4797](https://github.com/bridgecrewio/checkov/pull/4797)
- **terraform:** Ensure APPService default action is to ignore not fail - [#4790](https://github.com/bridgecrewio/checkov/pull/4790)
- **terraform:** Subnetworks with internal purpose can have private_ipv6_google_access… - [#4804](https://github.com/bridgecrewio/checkov/pull/4804)

## [2.3.150](https://github.com/bridgecrewio/checkov/compare/2.3.148...2.3.150) - 2023-04-03

### Feature

- **terraform:** Adding yaml based build time policies for corresponding PC runtime policies - [#4800](https://github.com/bridgecrewio/checkov/pull/4800)

### Bug Fix

- **terraform:** Fix for edge cases in for_each modules - [#4831](https://github.com/bridgecrewio/checkov/pull/4831)

## [2.3.148](https://github.com/bridgecrewio/checkov/compare/2.3.140...2.3.148) - 2023-04-02

### Feature

- **kubernetes:** support non-utf-8 encoded Kubernetes manifest files - [#4820](https://github.com/bridgecrewio/checkov/pull/4820)
- **terraform:** ElasticCache for Redis cluster should automatically take minor updates - [#4726](https://github.com/bridgecrewio/checkov/pull/4726)
- **terraform:** Ensure opensearch is configured for HA - [#4717](https://github.com/bridgecrewio/checkov/pull/4717)
- **terraform:** Ensure Redshift specifies a DB name - [#4723](https://github.com/bridgecrewio/checkov/pull/4723)
- **terraform:** Ensure Redshift uses enhanced vpc routing - [#4724](https://github.com/bridgecrewio/checkov/pull/4724)
- **terraform:** Fix up ES logging check - [#4720](https://github.com/bridgecrewio/checkov/pull/4720)

### Bug Fix

- **general:** don't add an invalid URL to helpUri field in SARIF output - [#4814](https://github.com/bridgecrewio/checkov/pull/4814)
- **graph:** support string values for resource_types in graph checks properly - [#4819](https://github.com/bridgecrewio/checkov/pull/4819)
- **kubernetes:** Don't require ImagePullPolicy when digest (#4776) - [#4781](https://github.com/bridgecrewio/checkov/pull/4781)
- **secrets:** catch errors in middle of process of getting commit diffs - [#4823](https://github.com/bridgecrewio/checkov/pull/4823)
- **terraform:** Fix add_to_block condition to support more edge cases   - [#4822](https://github.com/bridgecrewio/checkov/pull/4822)
- **terraform:** fix false positive CKV2_GCP_20 (fails for any non-MySQL instance) - [#4813](https://github.com/bridgecrewio/checkov/pull/4813)
- **terraform:** Length resolvers evaluate length of `dict` as 1. - [#4808](https://github.com/bridgecrewio/checkov/pull/4808)

### Platform

- **general:** Save error lines in IR records - [#4821](https://github.com/bridgecrewio/checkov/pull/4821)

## [2.3.140](https://github.com/bridgecrewio/checkov/compare/2.3.134...2.3.140) - 2023-03-30

### Feature

- **general:** add OpenAI integration - [#4782](https://github.com/bridgecrewio/checkov/pull/4782)
- **terraform:** Ensure that cloudwatch alarms are set on - [#4805](https://github.com/bridgecrewio/checkov/pull/4805)

### Bug Fix

- **general:** fix scan all files entrypoint - [#4801](https://github.com/bridgecrewio/checkov/pull/4801)
- **terraform:** Set back CHECKOV_ENABLE_FOREACH_HANDLING to False to check perfomence - [#4798](https://github.com/bridgecrewio/checkov/pull/4798)
- **terraform:** TF new parser - Check for tfvars block - [#4796](https://github.com/bridgecrewio/checkov/pull/4796)

## [2.3.134](https://github.com/bridgecrewio/checkov/compare/2.3.128...2.3.134) - 2023-03-29

### Feature

- **ansible:** PAN-OS policy and zone checks - [#4737](https://github.com/bridgecrewio/checkov/pull/4737)
- **terraform_plan:** support data blocks in Terraform plan files - [#4758](https://github.com/bridgecrewio/checkov/pull/4758)
- **terraform:** Set CHECKOV_ENABLE_FOREACH_HANDLING as True - [#4774](https://github.com/bridgecrewio/checkov/pull/4774)

### Bug Fix

- **terraform:** Correctly serialize/deserialize TFModule object - [#4780](https://github.com/bridgecrewio/checkov/pull/4780)
- **terraform:** Fix nested `each.value` replacement in for_each handler - [#4787](https://github.com/bridgecrewio/checkov/pull/4787)

## [2.3.128](https://github.com/bridgecrewio/checkov/compare/2.3.124...2.3.128) - 2023-03-28

### Feature

- **secrets:** make git history scan run in parallel  - [#4769](https://github.com/bridgecrewio/checkov/pull/4769)
- **terraform:** Add source_module_object_ to block attributes - [#4773](https://github.com/bridgecrewio/checkov/pull/4773)
- **terraform:** codebuild dont enable privilege mode - [#4714](https://github.com/bridgecrewio/checkov/pull/4714)

### Bug Fix

- **terraform:** Fix nested statements in _is_static_foreach_statement - [#4772](https://github.com/bridgecrewio/checkov/pull/4772)

## [2.3.124](https://github.com/bridgecrewio/checkov/compare/2.3.121...2.3.124) - 2023-03-27

### Feature

- **terraform:** AWS Use Launch templates in ASG - [#4698](https://github.com/bridgecrewio/checkov/pull/4698)
- **terraform:** Codebuild defines and uses logs - [#4696](https://github.com/bridgecrewio/checkov/pull/4696)

### Bug Fix

- **terraform:** Foreach - Fix regex on an empty list - [#4765](https://github.com/bridgecrewio/checkov/pull/4765)

## [2.3.121](https://github.com/bridgecrewio/checkov/compare/2.3.115...2.3.121) - 2023-03-26

### Feature

- **general:** Add scan all files to entrypoint - [#4746](https://github.com/bridgecrewio/checkov/pull/4746)
- **terraform:** check routes are authorised - [#4682](https://github.com/bridgecrewio/checkov/pull/4682)
- **terraform:** CloudDistribution set Failover origin - [#4686](https://github.com/bridgecrewio/checkov/pull/4686)
- **terraform:** code build s3 logs are encrypted - [#4687](https://github.com/bridgecrewio/checkov/pull/4687)
- **terraform:** Elasticbeanstalk should use enhanced health reporting - [#4692](https://github.com/bridgecrewio/checkov/pull/4692)
- **terraform:** RDS cluster copy tags to snapshot - [#4693](https://github.com/bridgecrewio/checkov/pull/4693)
- **terraform:** Support for_each/count statements in TF Modules - [#4708](https://github.com/bridgecrewio/checkov/pull/4708)

### Bug Fix

- **secrets:**  Don't show stack trace in failures  when uploading secrets to verify - [#4734](https://github.com/bridgecrewio/checkov/pull/4734)
- **secrets:** Compare abs paths in SecretsOmitter - [#4756](https://github.com/bridgecrewio/checkov/pull/4756)
- **terraform:** refine IAM assume role check CKV_AWS_61 - [#4749](https://github.com/bridgecrewio/checkov/pull/4749)
- **terraform:** refine S3 lifecycle check CKV_AWS_300 - [#4750](https://github.com/bridgecrewio/checkov/pull/4750)

### Platform

- **terraform:** external module from git fail - log warning - [#4755](https://github.com/bridgecrewio/checkov/pull/4755)

### Documentation

- **terraform:** Document no private registry - [#4745](https://github.com/bridgecrewio/checkov/pull/4745)

## [2.3.115](https://github.com/bridgecrewio/checkov/compare/2.3.114...2.3.115) - 2023-03-24

### Bug Fix

- **general:** fix default log levels for support stream - [#4741](https://github.com/bridgecrewio/checkov/pull/4741)

## [2.3.114](https://github.com/bridgecrewio/checkov/compare/2.3.110...2.3.114) - 2023-03-23

### Feature

- **ansible:** Ansible panos int mgmt checks - [#4683](https://github.com/bridgecrewio/checkov/pull/4683)
- **terraform:** api gateway ensure api cache is encrypted - [#4681](https://github.com/bridgecrewio/checkov/pull/4681)
- **terraform:** AWS ensure Sagemaker Notebook users are not Root - [#4676](https://github.com/bridgecrewio/checkov/pull/4676)
- **terraform:** Sagemaker Notebook In Custom VPC - [#4675](https://github.com/bridgecrewio/checkov/pull/4675)
- **terraform:** Terraform runner with the new TF parser - [#4728](https://github.com/bridgecrewio/checkov/pull/4728)

### Bug Fix

- **gitlab:**  fixing include scope that predominant all others - [#4735](https://github.com/bridgecrewio/checkov/pull/4735)

### Documentation

- **general:** fix small typo - [#4725](https://github.com/bridgecrewio/checkov/pull/4725)

## [2.3.110](https://github.com/bridgecrewio/checkov/compare/2.3.108...2.3.110) - 2023-03-22

### Bug Fix

- **graph:** Fix an issue in and connection solver - [#4719](https://github.com/bridgecrewio/checkov/pull/4719)

## [2.3.108](https://github.com/bridgecrewio/checkov/compare/2.3.105...2.3.108) - 2023-03-21

### Feature

- **secrets:** add option to get and set the secret store - [#4707](https://github.com/bridgecrewio/checkov/pull/4707)

### Platform

- **graph:** Ignore SyntaxWarning in variable rendering - [#4718](https://github.com/bridgecrewio/checkov/pull/4718)

## [2.3.105](https://github.com/bridgecrewio/checkov/compare/2.3.102...2.3.105) - 2023-03-20

### Feature

- **general:** add flag to skip cert verification - [#4641](https://github.com/bridgecrewio/checkov/pull/4641)
- **secrets:** Override secrets validation flag with tenant config - [#4701](https://github.com/bridgecrewio/checkov/pull/4701)

## [2.3.102](https://github.com/bridgecrewio/checkov/compare/2.3.96...2.3.102) - 2023-03-19

### Feature

- **terraform:** AWS Ensure cloudfront has a default root - [#4673](https://github.com/bridgecrewio/checkov/pull/4673)
- **terraform:** AWS ensure secret rotation is less than 90 days - [#4672](https://github.com/bridgecrewio/checkov/pull/4672)
- **terraform:** AWS Secrets are rotated - [#4671](https://github.com/bridgecrewio/checkov/pull/4671)
- **terraform:** ensure DB snapshots arent public - [#4667](https://github.com/bridgecrewio/checkov/pull/4667)
- **terraform:** ensure SSM docs are private - [#4668](https://github.com/bridgecrewio/checkov/pull/4668)
- **terraform:** lambda permission is not public - [#4666](https://github.com/bridgecrewio/checkov/pull/4666)

### Bug Fix

- **general:** Custom policies integration correct check IDs filtering - [#4700](https://github.com/bridgecrewio/checkov/pull/4700)
- **sca:** return empty result when using BC API key in IDE - [#4694](https://github.com/bridgecrewio/checkov/pull/4694)
- **terraform:** add extra handling around private GitHub Terraform modules - [#4699](https://github.com/bridgecrewio/checkov/pull/4699)

## [2.3.96](https://github.com/bridgecrewio/checkov/compare/2.3.95...2.3.96) - 2023-03-16

### Feature

- **ansible:** Ansible panos security policy checks - [#4639](https://github.com/bridgecrewio/checkov/pull/4639)
- **terraform:** s3 bucket has event notifications - [#4660](https://github.com/bridgecrewio/checkov/pull/4660)
- **terraform:** s3 ensure failed uploads are deleted id=300!!!! - [#4662](https://github.com/bridgecrewio/checkov/pull/4662)

### Bug Fix

- **gitlab:** index_out_of_range - [#4677](https://github.com/bridgecrewio/checkov/pull/4677)
- **terraform:** Revert "feat(terraform): support provider blocks yaml policy checks (… - [#4680](https://github.com/bridgecrewio/checkov/pull/4680)

## [2.3.95](https://github.com/bridgecrewio/checkov/compare/2.3.92...2.3.95) - 2023-03-15

### Feature

- **sca:** filter twistcli results with empty package name and version - [#4670](https://github.com/bridgecrewio/checkov/pull/4670)
- **terraform:** Support new TFParser in the local graph (under env var) - [#4664](https://github.com/bridgecrewio/checkov/pull/4664)
- **terraform:** support provider blocks yaml policy checks - [#4656](https://github.com/bridgecrewio/checkov/pull/4656)

## [2.3.92](https://github.com/bridgecrewio/checkov/compare/2.3.85...2.3.92) - 2023-03-14

### Feature

- **sca:** fix unexpected maven packageName - cycloneDX - [#4663](https://github.com/bridgecrewio/checkov/pull/4663)
- **sca:** skipping finding IsPrivateFixVersion by default - [#4648](https://github.com/bridgecrewio/checkov/pull/4648)
- **sca:** support inline CVE suppression in requirements.txt - [#4630](https://github.com/bridgecrewio/checkov/pull/4630)
- **secrets:** allow scanning just partial history of commits - [#4659](https://github.com/bridgecrewio/checkov/pull/4659)
- **terraform:** Refactor Module mapping objects - [#4661](https://github.com/bridgecrewio/checkov/pull/4661)
- **terraform:** s3 to have lifecycle policy - [#4658](https://github.com/bridgecrewio/checkov/pull/4658)

### Bug Fix

- **secrets:** fix git history partial scan - [#4665](https://github.com/bridgecrewio/checkov/pull/4665)

## [2.3.85](https://github.com/bridgecrewio/checkov/compare/2.3.79...2.3.85) - 2023-03-13

### Feature

- **secrets:** support git history scan in multiline parsers - [#4637](https://github.com/bridgecrewio/checkov/pull/4637)
- **terraform:** Definitions serialization with new definitions key/module objects - [#4655](https://github.com/bridgecrewio/checkov/pull/4655)
- **terraform:** support variable rendering for default objects in vars - [#4650](https://github.com/bridgecrewio/checkov/pull/4650)

### Bug Fix

- **arm:** Fix resource type check in SQLServerAuditingRetention90Days - [#4657](https://github.com/bridgecrewio/checkov/pull/4657)
- **general:** check suppression id instead of policy id - [#4646](https://github.com/bridgecrewio/checkov/pull/4646)
- **gitlab:** Modify GitLab CI resource ids - [#4647](https://github.com/bridgecrewio/checkov/pull/4647)

## [2.3.79](https://github.com/bridgecrewio/checkov/compare/2.3.75...2.3.79) - 2023-03-12

### Feature

- **terraform:** Fix for foreach subgraph rendering - [#4649](https://github.com/bridgecrewio/checkov/pull/4649)
- **terraform:** new checks on new resources - [#4491](https://github.com/bridgecrewio/checkov/pull/4491)

### Platform

- **general:** skip uploading repo for VSCode source - [#4643](https://github.com/bridgecrewio/checkov/pull/4643)

## [2.3.75](https://github.com/bridgecrewio/checkov/compare/2.3.71...2.3.75) - 2023-03-09

### Feature

- **general:** add Terraform JSON support - [#4626](https://github.com/bridgecrewio/checkov/pull/4626)
- **terraform:** Adding yaml based build time policies for corresponding PC runtime policies - [#4605](https://github.com/bridgecrewio/checkov/pull/4605)

### Bug Fix

- **arm:** ignore incomplete resource in ARM templates - [#4636](https://github.com/bridgecrewio/checkov/pull/4636)
- **terraform:** stop handle resource `for_each` as dynamic attribute - [#4632](https://github.com/bridgecrewio/checkov/pull/4632)

## [2.3.71](https://github.com/bridgecrewio/checkov/compare/2.3.70...2.3.71) - 2023-03-08

### Bug Fix

- **terraform:** v2 settings valid  for windows and linux web apps - [#4628](https://github.com/bridgecrewio/checkov/pull/4628)

## [2.3.70](https://github.com/bridgecrewio/checkov/compare/2.3.66...2.3.70) - 2023-03-07

### Feature

- **ansible:** add Ansible check for CKV_PAN_4 for PAN-OS DSRI - [#4608](https://github.com/bridgecrewio/checkov/pull/4608)
- **dockerfile:** Add tdnf support for CKV2_DOCKER_9 - [#4620](https://github.com/bridgecrewio/checkov/pull/4620)
- **terraform:** Check added for AWS Database instance deletion protection - [#4616](https://github.com/bridgecrewio/checkov/pull/4616)
- **terraform:** CloudtrailEventDataStoreUsesCMK  - [#4621](https://github.com/bridgecrewio/checkov/pull/4621)

### Bug Fix

- **bicep:** handle malformed files in bicep parser - [#4629](https://github.com/bridgecrewio/checkov/pull/4629)
- **cloudformation:** KMSKeyWildCardPrincipal modification - Check for wildcards inside of lists - [#4590](https://github.com/bridgecrewio/checkov/pull/4590)
- **terraform:** in sg rules ignore self referencing - [#4603](https://github.com/bridgecrewio/checkov/pull/4603)

## [2.3.66](https://github.com/bridgecrewio/checkov/compare/2.3.59...2.3.66) - 2023-03-06

### Feature

- **gitlab:** fix wrong resource in gitlab-ci - [#4610](https://github.com/bridgecrewio/checkov/pull/4610)
- **terraform:** Support the -1 protocol on SG checks - [#4611](https://github.com/bridgecrewio/checkov/pull/4611)
- **terraform:** TF Parser support of new modules keys - [#4601](https://github.com/bridgecrewio/checkov/pull/4601)

### Bug Fix

- **bicep:** extend CKV_AZURE_4 to consider omsAgent to be written in camelCase - [#4614](https://github.com/bridgecrewio/checkov/pull/4614)
- **general:** refactor SARIF output - [#4606](https://github.com/bridgecrewio/checkov/pull/4606)
- **general:** skip scanning invalid resources - [#4617](https://github.com/bridgecrewio/checkov/pull/4617)
- **sca:** Added an error log for Twistcli failures - [#4613](https://github.com/bridgecrewio/checkov/pull/4613)
- **terraform:** stop evaluating a string ... to the Ellipsis object - [#4623](https://github.com/bridgecrewio/checkov/pull/4623)

## [2.3.59](https://github.com/bridgecrewio/checkov/compare/2.3.57...2.3.59) - 2023-03-05

### Bug Fix

- **general:** do not stop getting fixes if one attempt results in a 403 - [#4607](https://github.com/bridgecrewio/checkov/pull/4607)
- **gha:** skip schema validity check if parsing returned None - [#4609](https://github.com/bridgecrewio/checkov/pull/4609)
- **secrets:** Adjust output to include the additional Git History info - [#4566](https://github.com/bridgecrewio/checkov/pull/4566)

## [2.3.57](https://github.com/bridgecrewio/checkov/compare/2.3.53...2.3.57) - 2023-03-02

### Feature

- **ansible:** Add checks for the ansible builtin dnf module - [#4570](https://github.com/bridgecrewio/checkov/pull/4570)
- **dockerfile:** Add new dockerfile checks - [#4569](https://github.com/bridgecrewio/checkov/pull/4569)
- **terraform:** Create a new TF parser - [#4584](https://github.com/bridgecrewio/checkov/pull/4584)

### Bug Fix

- **secrets:** only check secrets framework when scanning history - [#4592](https://github.com/bridgecrewio/checkov/pull/4592)
- **terraform:** AWS - there's a new sg vpc ingress rule - [#4575](https://github.com/bridgecrewio/checkov/pull/4575)
- **terraform:** Azurerm NSG UDP check should work for old style but still valid tf - [#4454](https://github.com/bridgecrewio/checkov/pull/4454)

## [2.3.53](https://github.com/bridgecrewio/checkov/compare/2.3.50...2.3.53) - 2023-03-01

### Feature

- **terraform:** Add foreach_attrs in saved graph - [#4587](https://github.com/bridgecrewio/checkov/pull/4587)
- **terraform:** Set foreach_attrs directly under the block - [#4586](https://github.com/bridgecrewio/checkov/pull/4586)
- **terraform:** TF foreach - Support updating each.value in nested dict - [#4588](https://github.com/bridgecrewio/checkov/pull/4588)

### Bug Fix

- **sca:** Set prisma token and scan packages by v2 for IDE scans - [#4580](https://github.com/bridgecrewio/checkov/pull/4580)
- **terraform:** fix CKV_AWS_70 test and add graph for coverage of data source - [#4542](https://github.com/bridgecrewio/checkov/pull/4542)
- **terraform:** TF foreach - Avoid rendering in static statements - [#4583](https://github.com/bridgecrewio/checkov/pull/4583)

### Documentation

- **ansible:** add Ansible policy docs generation - [#4582](https://github.com/bridgecrewio/checkov/pull/4582)

## [2.3.50](https://github.com/bridgecrewio/checkov/compare/2.3.48...2.3.50) - 2023-02-28

### Bug Fix

- **terraform:** add not exists conditional to CKV2_AWS_16 to account for defaults - [#4578](https://github.com/bridgecrewio/checkov/pull/4578)

## [2.3.48](https://github.com/bridgecrewio/checkov/compare/2.3.44...2.3.48) - 2023-02-27

### Feature

- **secrets:** track complete file deletion and renaming - [#4551](https://github.com/bridgecrewio/checkov/pull/4551)
- **terraform:** Adding yaml based build time policies for corresponding PC runtime policies - [#4529](https://github.com/bridgecrewio/checkov/pull/4529)

### Bug Fix

- **ansible:** support skip check for Ansible Python-based checks - [#4556](https://github.com/bridgecrewio/checkov/pull/4556)
- **terraform:** Handle unescaped lookup values - [#4565](https://github.com/bridgecrewio/checkov/pull/4565)

## [2.3.44](https://github.com/bridgecrewio/checkov/compare/2.3.39...2.3.44) - 2023-02-26

### Feature

- **dockerfile:** Add check for the environment variable NPM_CONFIG_STRICT_SSL - [#4553](https://github.com/bridgecrewio/checkov/pull/4553)
- **terraform:** TF Parser  - Move funcs and consts to utils file - [#4550](https://github.com/bridgecrewio/checkov/pull/4550)

### Bug Fix

- **terraform_plan:** Fix tf plan nested modules - [#4562](https://github.com/bridgecrewio/checkov/pull/4562)
- **terraform:** fix for #4518 - [#4528](https://github.com/bridgecrewio/checkov/pull/4528)
- **terraform:** Move get_module back to parser - [#4560](https://github.com/bridgecrewio/checkov/pull/4560)
- **terraform:** remove dynamic warning exc_info - [#4563](https://github.com/bridgecrewio/checkov/pull/4563)

## [2.3.39](https://github.com/bridgecrewio/checkov/compare/2.3.36...2.3.39) - 2023-02-23

### Feature

- **dockerfile:** Add checks for disabling signature checks for apk, apt-get, rpm, yum, dnf - [#4404](https://github.com/bridgecrewio/checkov/pull/4404)
- **terraform:** New classes for the TF module model - [#4546](https://github.com/bridgecrewio/checkov/pull/4546)

### Bug Fix

- **gha:** Align GHA resource ids (Graph vs Python checks) - [#4549](https://github.com/bridgecrewio/checkov/pull/4549)

## [2.3.36](https://github.com/bridgecrewio/checkov/compare/2.3.33...2.3.36) - 2023-02-22

### Feature

- **arm:** add graph capabilities to ARM framework - [#4526](https://github.com/bridgecrewio/checkov/pull/4526)
- **secrets:** add timeout for scan history checks - [#4523](https://github.com/bridgecrewio/checkov/pull/4523)
- **secrets:** Support secret findings in git history - [#4525](https://github.com/bridgecrewio/checkov/pull/4525)

## [2.3.33](https://github.com/bridgecrewio/checkov/compare/2.3.29...2.3.33) - 2023-02-21

### Feature

- **gitlab:** fix gitlab ci yaml file processing - [#4536](https://github.com/bridgecrewio/checkov/pull/4536)
- **sca:** adding is_registry_url and printing in the cyclonedx only private registries urls - [#4533](https://github.com/bridgecrewio/checkov/pull/4533)
- **sca:** support also the key "registryUrl" when extracting registry_url for the report - [#4535](https://github.com/bridgecrewio/checkov/pull/4535)

### Bug Fix

- **terraform:** Optional module content path - [#4537](https://github.com/bridgecrewio/checkov/pull/4537)

## [2.3.29](https://github.com/bridgecrewio/checkov/compare/2.3.28...2.3.29) - 2023-02-20

### Bug Fix

- **cloudformation:** Update CKV_AWS_46 to handle base64 encoded userdata - [#4530](https://github.com/bridgecrewio/checkov/pull/4530)

## [2.3.28](https://github.com/bridgecrewio/checkov/compare/2.3.23...2.3.28) - 2023-02-19

### Feature

- **secrets:** add flag for scan secrets history - [#4513](https://github.com/bridgecrewio/checkov/pull/4513)
- **terraform:** Used parentheses in key for foreach attributes but not count - [#4520](https://github.com/bridgecrewio/checkov/pull/4520)

### Bug Fix

- **gha:** fix output flag for usage in checkov-action - [#4517](https://github.com/bridgecrewio/checkov/pull/4517)
- **terraform:** add datasource option for headers check - [#4496](https://github.com/bridgecrewio/checkov/pull/4496)
- **terraform:** optimize check CKV2_AWS_60 - [#4512](https://github.com/bridgecrewio/checkov/pull/4512)

### Platform

- **general:** Use new enforcement categories (#4456) - [#4519](https://github.com/bridgecrewio/checkov/pull/4519)

## [2.3.23](https://github.com/bridgecrewio/checkov/compare/2.3.22...2.3.23) - 2023-02-18

### Feature

- **ansible:** Add checks for the ansible builtin apt module - [#4500](https://github.com/bridgecrewio/checkov/pull/4500)

### Bug Fix

- **gha:** now looks for GHA on windows - [#4515](https://github.com/bridgecrewio/checkov/pull/4515)

## [2.3.22](https://github.com/bridgecrewio/checkov/compare/2.3.18...2.3.22) - 2023-02-16

### Feature

- **sca:** adding registry-url to the cyclonedx output report - [#4511](https://github.com/bridgecrewio/checkov/pull/4511)
- **secrets:**  Add capability to iterate over git history - [#4469](https://github.com/bridgecrewio/checkov/pull/4469)
- **terraform:** Adding yaml based build time policies for corresponding PC run time policies - [#4425](https://github.com/bridgecrewio/checkov/pull/4425)

### Bug Fix

- **secrets:**  import git - [#4514](https://github.com/bridgecrewio/checkov/pull/4514)

## [2.3.18](https://github.com/bridgecrewio/checkov/compare/2.3.14...2.3.18) - 2023-02-15

### Feature

- **sca:** add registry urls and description to the output report and to the csv report - [#4485](https://github.com/bridgecrewio/checkov/pull/4485)

### Bug Fix

- **ansible:** skip unsupported Ansible resources - [#4504](https://github.com/bridgecrewio/checkov/pull/4504)
- **terraform:** Fix an str split edge case in function - [#4507](https://github.com/bridgecrewio/checkov/pull/4507)
- **terraform:** fix enforcement rules mapping - [#4509](https://github.com/bridgecrewio/checkov/pull/4509)

## [2.3.14](https://github.com/bridgecrewio/checkov/compare/2.3.7...2.3.14) - 2023-02-14

### Feature

- **secrets:** log and filter potential uuid case - [#4486](https://github.com/bridgecrewio/checkov/pull/4486)
- **terraform:** Assign/override main vertices by the first new vertice. - [#4493](https://github.com/bridgecrewio/checkov/pull/4493)
- **terraform:** Support for loops in foreach statements - [#4483](https://github.com/bridgecrewio/checkov/pull/4483)

### Bug Fix

- **terraform:** Handle KeyError in hadle_for_loop func - [#4501](https://github.com/bridgecrewio/checkov/pull/4501)
- **terraform:** Handle type error in `_handle_for_loop_in_dict` - [#4495](https://github.com/bridgecrewio/checkov/pull/4495)
- **terraform:** skip loading module that calls to the same dir - [#4499](https://github.com/bridgecrewio/checkov/pull/4499)

### Platform

- **general:** Use new enforcement categories - [#4456](https://github.com/bridgecrewio/checkov/pull/4456)

### Documentation

- **general:** update installation on Alpine docs - [#4474](https://github.com/bridgecrewio/checkov/pull/4474)

## [2.3.7](https://github.com/bridgecrewio/checkov/compare/2.3.3...2.3.7) - 2023-02-13

### Feature

- **graph:** Add UT as an example of not-exists for the nested list. - [#4484](https://github.com/bridgecrewio/checkov/pull/4484)
- **secrets:** Save secrets line number - [#4488](https://github.com/bridgecrewio/checkov/pull/4488)
- **terraform:** AWS:check global DocDB cluster is encrypted - [#4405](https://github.com/bridgecrewio/checkov/pull/4405)
- **terraform:** check msk nodes are private - [#4392](https://github.com/bridgecrewio/checkov/pull/4392)
- **terraform:** support more json encoded objects as part of terraform resource and fix evaluation of true/false in json - [#4487](https://github.com/bridgecrewio/checkov/pull/4487)

### Bug Fix

- **ansible:** support nested blocks and empty module values - [#4479](https://github.com/bridgecrewio/checkov/pull/4479)
- **cloudformation:** Updated AWS_CKV_7 to not require rotation on asymmetric keys - [#4476](https://github.com/bridgecrewio/checkov/pull/4476)

## [2.3.3](https://github.com/bridgecrewio/checkov/compare/2.3.0...2.3.3) - 2023-02-09

### Feature

- **secrets:** limit multiline regex detector run - [#4453](https://github.com/bridgecrewio/checkov/pull/4453)
- **terraform:** Add foreach_attrs to config objects + UTs - [#4463](https://github.com/bridgecrewio/checkov/pull/4463)
- **terraform:** GCP: Ensure Basic role are not used at Org/Folder/Project level (CKV_GCP_115, CKV_GCP_116, CKV_GCP_117) - [#4390](https://github.com/bridgecrewio/checkov/pull/4390)

### Bug Fix

- **kustomize:** fix kustomize file path cli - [#4466](https://github.com/bridgecrewio/checkov/pull/4466)
- **terraform:** Allow different type of value in BaseResourceValueCheck - [#4470](https://github.com/bridgecrewio/checkov/pull/4470)
- **terraform:** deny statements with wildcards are valid - [#4440](https://github.com/bridgecrewio/checkov/pull/4440)

## [2.3.0](https://github.com/bridgecrewio/checkov/compare/2.2.356...2.3.0) - 2023-02-09

### Breaking Change

- **gha:** adjust the attribute reference for GitHub Actions graph checks - [#4445](https://github.com/bridgecrewio/checkov/pull/4445)
- **terraform:** enable nested modules by default - [#4448](https://github.com/bridgecrewio/checkov/pull/4448)

### Feature

- **general:** Create 3d combinations post runner - [#4353](https://github.com/bridgecrewio/checkov/pull/4353)

### Bug Fix

- **gha:** fix GHA _get_jobs edge case (string step) - [#4444](https://github.com/bridgecrewio/checkov/pull/4444)
- **graph:** added graph init to igraph db connector - [#4455](https://github.com/bridgecrewio/checkov/pull/4455)

## [2.2.356](https://github.com/bridgecrewio/checkov/compare/2.2.348...2.2.356) - 2023-02-08

### Feature

- **sca:** Add support for Dotnet files - [#4189](https://github.com/bridgecrewio/checkov/pull/4189)
- **terraform:** Create new resources for count/foreach resources - [#4427](https://github.com/bridgecrewio/checkov/pull/4427)
- **terraform:** extend CKV2_AWS_5 to support aws_ec2_spot_fleet_request - [#4438](https://github.com/bridgecrewio/checkov/pull/4438)

### Bug Fix

- **general:** Correct BigQueryDatasetEncryptedWithCMK name field - [#4443](https://github.com/bridgecrewio/checkov/pull/4443)
- **kubernetes:** Fix empty spec in k8s file - [#4452](https://github.com/bridgecrewio/checkov/pull/4452)
- **kustomize:** Fix kustomize cli file path - [#4447](https://github.com/bridgecrewio/checkov/pull/4447)
- **secrets:** remove CKV_SECRET_78 from SECRET_TYPE_TO_ID - [#4446](https://github.com/bridgecrewio/checkov/pull/4446)
- **terraform:** change module index separator in full path - [#4437](https://github.com/bridgecrewio/checkov/pull/4437)

## [2.2.348](https://github.com/bridgecrewio/checkov/compare/2.2.341...2.2.348) - 2023-02-07

### Feature

- **cloudformation:** support new default s3 encryption - [#4429](https://github.com/bridgecrewio/checkov/pull/4429)
- **graph:** added indices to igraph nodes - [#4433](https://github.com/bridgecrewio/checkov/pull/4433)
- **secrets:** Add args to analyze line is added and is removed for git history scan - [#4426](https://github.com/bridgecrewio/checkov/pull/4426)

### Bug Fix

- **secrets:** Comment out checkob multiline regex detectors - [#4441](https://github.com/bridgecrewio/checkov/pull/4441)
- **terraform:** Fix updating resource config - [#4432](https://github.com/bridgecrewio/checkov/pull/4432)

### Platform

- **secrets:** Add secrets custom regex on file - [#4430](https://github.com/bridgecrewio/checkov/pull/4430)

## [2.2.341](https://github.com/bridgecrewio/checkov/compare/2.2.335...2.2.341) - 2023-02-06

### Feature

- **ansible:** add support for Ansible blocks - [#4419](https://github.com/bridgecrewio/checkov/pull/4419)
- **general:** Control check failure logging level - [#4431](https://github.com/bridgecrewio/checkov/pull/4431)
- **graph:** add validation for graph checks - [#4352](https://github.com/bridgecrewio/checkov/pull/4352)
- **kubernetes:** support inline skips for Kubernetes graph checks - [#4412](https://github.com/bridgecrewio/checkov/pull/4412)
- **secrets:** remove secrets dependency in generic record - [#4424](https://github.com/bridgecrewio/checkov/pull/4424)

### Bug Fix

- **kustomize:** remove redundant error in kustomize runner - [#4428](https://github.com/bridgecrewio/checkov/pull/4428)

### Documentation

- **general:** fix graph check link in docs - [#4420](https://github.com/bridgecrewio/checkov/pull/4420)

## [2.2.335](https://github.com/bridgecrewio/checkov/compare/2.2.332...2.2.335) - 2023-02-05

### Feature

- **kustomize:** support kustomize v5 - [#4411](https://github.com/bridgecrewio/checkov/pull/4411)
- **terraform:** [Foreach/Count Handling] Render dynamic foreach/count statement - [#4398](https://github.com/bridgecrewio/checkov/pull/4398)

### Bug Fix

- **general:** Checks edge-cases fixes in terraform and openapi - [#4414](https://github.com/bridgecrewio/checkov/pull/4414)
- **general:** Skip resources with no 'Type' defined + Checks containing wildcards for resource types leads to crash - [#4408](https://github.com/bridgecrewio/checkov/pull/4408)
- **terraform:** fix getting the module for resource named 'module' - [#4418](https://github.com/bridgecrewio/checkov/pull/4418)
- **terraform:** retire CKV_AWS_128 in favour of CKV_AWS_162 - [#4350](https://github.com/bridgecrewio/checkov/pull/4350)
- **terraform:** SQS check was all types of wrong - [#4382](https://github.com/bridgecrewio/checkov/pull/4382)

## [2.2.332](https://github.com/bridgecrewio/checkov/compare/2.2.331...2.2.332) - 2023-02-04

### Bug Fix

- **cloudformation:** Don't fail Aurora instances for MultiAZ not being set - [#4316](https://github.com/bridgecrewio/checkov/pull/4316)

## [2.2.331](https://github.com/bridgecrewio/checkov/compare/2.2.330...2.2.331) - 2023-02-03

### Bug Fix

- **general:** fix compact json output - [#4406](https://github.com/bridgecrewio/checkov/pull/4406)

## [2.2.330](https://github.com/bridgecrewio/checkov/compare/2.2.327...2.2.330) - 2023-02-02

### Feature

- **sca:** Add a --support flag   - [#4397](https://github.com/bridgecrewio/checkov/pull/4397)
- **sca:** Add a --support flag --revert - [#4396](https://github.com/bridgecrewio/checkov/pull/4396)
- **secrets:** add workdir info to secrets scanner - [#4400](https://github.com/bridgecrewio/checkov/pull/4400)
- **secrets:** extract new detector_utils file from entropy keyword combinator - [#4385](https://github.com/bridgecrewio/checkov/pull/4385)

### Bug Fix

- **general:** Remove empty links from GitLab SAST output - [#4393](https://github.com/bridgecrewio/checkov/pull/4393)

## [2.2.327](https://github.com/bridgecrewio/checkov/compare/2.2.320...2.2.327) - 2023-02-01

### Feature

- **gha:** add gha permissions lines - [#4372](https://github.com/bridgecrewio/checkov/pull/4372)
- **sca:** add extract nodes igraph - [#4359](https://github.com/bridgecrewio/checkov/pull/4359)
- **sca:** create bom report when extra_resources is not empty - [#4388](https://github.com/bridgecrewio/checkov/pull/4388)
- **secrets:** add support for runnable secrets plugins - [#4368](https://github.com/bridgecrewio/checkov/pull/4368)
- **terraform:** add CKV_GCP_114 to ensure that Public Access Prevention is enforced on GoogleCloudStorage bucket. - [#4347](https://github.com/bridgecrewio/checkov/pull/4347)
- **terraform:** Add cloudsplaining checks to tf aws_iam_policy CKV_AWS_287-290 - [#4386](https://github.com/bridgecrewio/checkov/pull/4386)
- **terraform:** get static foreach/count values of resources - [#4374](https://github.com/bridgecrewio/checkov/pull/4374)

## [2.2.320](https://github.com/bridgecrewio/checkov/compare/2.2.316...2.2.320) - 2023-01-31

### Feature

- **sca:** Add a --support flag - [#4323](https://github.com/bridgecrewio/checkov/pull/4323)
- **sca:** added extra supported package files to find_scannable_files - [#4378](https://github.com/bridgecrewio/checkov/pull/4378)
- **terraform:** add reset edges function to terraform local graph - [#4373](https://github.com/bridgecrewio/checkov/pull/4373)
- **terraform:** Added base class for cloudsplaining iam checks to be integrated between data and resource objects - [#4338](https://github.com/bridgecrewio/checkov/pull/4338)
- **terraform:** Added basic check with test for tf resource with IAM privilege escalation - [#4376](https://github.com/bridgecrewio/checkov/pull/4376)

### Bug Fix

- **cloudformation:** Skip SAM Global Tags propagation - [#4383](https://github.com/bridgecrewio/checkov/pull/4383)
- **sca:** extend image name validation - [#4377](https://github.com/bridgecrewio/checkov/pull/4377)
- **terraform:** simple check naming fix - [#4371](https://github.com/bridgecrewio/checkov/pull/4371)

## [2.2.316](https://github.com/bridgecrewio/checkov/compare/2.2.312...2.2.316) - 2023-01-30

### Feature

- **sca:** ignore package.json file when yarn.lock exists - [#4370](https://github.com/bridgecrewio/checkov/pull/4370)
- **terraform:** GCP check kms policy does not define public access - [#4190](https://github.com/bridgecrewio/checkov/pull/4190)
- **terraform:** GCP check policy isn't public - [#4194](https://github.com/bridgecrewio/checkov/pull/4194)

### Bug Fix

- **sca:** support BC_VUL_X IDs in GitLab SAST output - [#4360](https://github.com/bridgecrewio/checkov/pull/4360)

## [2.2.312](https://github.com/bridgecrewio/checkov/compare/2.2.305...2.2.312) - 2023-01-29

### Feature

- **azure:** fix container latest tag missing results - [#4337](https://github.com/bridgecrewio/checkov/pull/4337)

### Bug Fix

- **azure:** Add `.*.` in azure checks to check in lists as well - [#4355](https://github.com/bridgecrewio/checkov/pull/4355)
- **azure:** Azure checks fixes - [#4342](https://github.com/bridgecrewio/checkov/pull/4342)
- **azure:** Azure checks fixes - [#4354](https://github.com/bridgecrewio/checkov/pull/4354)
- **azure:** Support string function_app min_tls_version as well - [#4357](https://github.com/bridgecrewio/checkov/pull/4357)
- **kubernetes:** k8s checks fixes - [#4343](https://github.com/bridgecrewio/checkov/pull/4343)
- **sca:** Fix multiple issues related to IR - [#4358](https://github.com/bridgecrewio/checkov/pull/4358)
- **terraform:** Terraform checks fixes - [#4344](https://github.com/bridgecrewio/checkov/pull/4344)

## [2.2.305](https://github.com/bridgecrewio/checkov/compare/2.2.304...2.2.305) - 2023-01-28

### Feature

- **general:** Add GitLab SAST output - [#4315](https://github.com/bridgecrewio/checkov/pull/4315)

## [2.2.304](https://github.com/bridgecrewio/checkov/compare/2.2.302...2.2.304) - 2023-01-26

### Bug Fix

- **kubernetes:** skip extracting pods for custom resources - [#4334](https://github.com/bridgecrewio/checkov/pull/4334)
- **sca:** require requests 2.27.0 - [#4339](https://github.com/bridgecrewio/checkov/pull/4339)

### Documentation

- **general:** fix env var name to `CKV_IGNORE_HIDDEN_DIRECTORIES` - [#4335](https://github.com/bridgecrewio/checkov/pull/4335)

## [2.2.302](https://github.com/bridgecrewio/checkov/compare/2.2.299...2.2.302) - 2023-01-25

### Feature

- **general:** igraph library support - [#4327](https://github.com/bridgecrewio/checkov/pull/4327)

### Bug Fix

- **general:** add missing header in --list output - [#4329](https://github.com/bridgecrewio/checkov/pull/4329)
- **kubernetes:** extract pods only for supported resources - [#4330](https://github.com/bridgecrewio/checkov/pull/4330)
- **sca:** catch exceptional error during SCA results polling - [#4331](https://github.com/bridgecrewio/checkov/pull/4331)
- **terraform:** change terraform nested modules path separators - [#4319](https://github.com/bridgecrewio/checkov/pull/4319)
- **terraform:** handle unexpected container definition type - [#4328](https://github.com/bridgecrewio/checkov/pull/4328)

## [2.2.299](https://github.com/bridgecrewio/checkov/compare/2.2.292...2.2.299) - 2023-01-24

### Feature

- **azure:** change detect image source - [#4320](https://github.com/bridgecrewio/checkov/pull/4320)
- **general:** add empty azure image check - [#4308](https://github.com/bridgecrewio/checkov/pull/4308)
- **general:** add logs for async license and image retrieval  - [#4317](https://github.com/bridgecrewio/checkov/pull/4317)
- **sca:** Support the new --image flag along the --docker-image flag  - [#4314](https://github.com/bridgecrewio/checkov/pull/4314)

### Bug Fix

- **general:** ignore repo_id setting when list flag is set - [#4313](https://github.com/bridgecrewio/checkov/pull/4313)
- **kubernetes:** handle k8s resource with missing required data - [#4318](https://github.com/bridgecrewio/checkov/pull/4318)
- **secrets:** Change s3 path for enriched secrets upload - [#4275](https://github.com/bridgecrewio/checkov/pull/4275)
- **terraform:** handle unexpected container type - [#4311](https://github.com/bridgecrewio/checkov/pull/4311)

### Documentation

- **general:** Update README for supported Python versions - [#4305](https://github.com/bridgecrewio/checkov/pull/4305)

## [2.2.292](https://github.com/bridgecrewio/checkov/compare/2.2.289...2.2.292) - 2023-01-23

### Feature

- **terraform:** new app service checks for azurerm - [#4072](https://github.com/bridgecrewio/checkov/pull/4072)

### Bug Fix

- **general:** In case of a non-JSON response, log the response - [#4304](https://github.com/bridgecrewio/checkov/pull/4304)
- **terraform_plan:** fix in deep analysis - [#4306](https://github.com/bridgecrewio/checkov/pull/4306)
- **terraform:** fix default behaviour of CKV_GCP_19 - [#4289](https://github.com/bridgecrewio/checkov/pull/4289)

## [2.2.289](https://github.com/bridgecrewio/checkov/compare/2.2.281...2.2.289) - 2023-01-22

### Feature

- **general:** add Ansible framework - [#4244](https://github.com/bridgecrewio/checkov/pull/4244)
- **general:** Allow using `--repo-root-for-plan-enrichment` flag in GitHub Actions - [#4292](https://github.com/bridgecrewio/checkov/pull/4292)
- **secrets:** add new sanity test files for base64 entropy detector - [#4298](https://github.com/bridgecrewio/checkov/pull/4298)
- **terraform:** Adding yaml based build time policies for corresponding PC run time policies - [#4265](https://github.com/bridgecrewio/checkov/pull/4265)

### Bug Fix

- **sca:** fix dependency tree cli print - [#4282](https://github.com/bridgecrewio/checkov/pull/4282)
- **terraform:** fix Exception in image ref - [#4297](https://github.com/bridgecrewio/checkov/pull/4297)
- **terraform:** fix in variable rendering - [#4296](https://github.com/bridgecrewio/checkov/pull/4296)
- **terraform:** Fix policy str in graph checks - [#4286](https://github.com/bridgecrewio/checkov/pull/4286)

## [2.2.281](https://github.com/bridgecrewio/checkov/compare/2.2.278...2.2.281) - 2023-01-19

### Feature

- **general:** add Image referencer igraph support - [#4277](https://github.com/bridgecrewio/checkov/pull/4277)
- **general:** Support aiohttp for IR API calls - [#4274](https://github.com/bridgecrewio/checkov/pull/4274)

### Bug Fix

- **general:** Enable running cloned policies in case the OOTB policy is suppressed - [#4281](https://github.com/bridgecrewio/checkov/pull/4281)
- **secrets:** change default secret validation status to unavailable - [#4284](https://github.com/bridgecrewio/checkov/pull/4284)
- **terraform:** fix error for push_skipped_checks_down with definition that not in the definition context - [#4272](https://github.com/bridgecrewio/checkov/pull/4272)

## [2.2.278](https://github.com/bridgecrewio/checkov/compare/2.2.274...2.2.278) - 2023-01-18

### Feature

- **azure:** Add image referencer in azure pipelines - [#4234](https://github.com/bridgecrewio/checkov/pull/4234)
- **gha:** fix yaml parsing of multi files - [#4270](https://github.com/bridgecrewio/checkov/pull/4270)
- **secrets:** fix to keyword combinator to reduce FPs - [#4260](https://github.com/bridgecrewio/checkov/pull/4260)

### Bug Fix

- **secrets:** add guideline and severity to custom secret check metadata - [#4276](https://github.com/bridgecrewio/checkov/pull/4276)

## [2.2.274](https://github.com/bridgecrewio/checkov/compare/2.2.271...2.2.274) - 2023-01-17

### Feature

- **gha:** fix failing image retrieval in GHA IR - [#4268](https://github.com/bridgecrewio/checkov/pull/4268)

### Bug Fix

- **cloudformation:** fix CloudFormation checks related to number values - [#4243](https://github.com/bridgecrewio/checkov/pull/4243)
- **general:** Add normalization to change the name of nuget to dotNet lang - [#4271](https://github.com/bridgecrewio/checkov/pull/4271)

## [2.2.271](https://github.com/bridgecrewio/checkov/compare/2.2.264...2.2.271) - 2023-01-16

### Feature

- **dockerfile:** Add checks for PYTHONHTTPSVERIFY and NODE_TLS_REJECT_UNAUTHORIZED - [#4223](https://github.com/bridgecrewio/checkov/pull/4223)
- **secrets:** Skip invalid secrets checks + soft/hard fails - [#4247](https://github.com/bridgecrewio/checkov/pull/4247)
- **terraform:** Azure search service checks - [#4064](https://github.com/bridgecrewio/checkov/pull/4064)
- **terraform:** GCP checks for definition of a firewall resource for a network - [#4188](https://github.com/bridgecrewio/checkov/pull/4188)

### Bug Fix

- **general:** Support encoding of function object - [#4259](https://github.com/bridgecrewio/checkov/pull/4259)
- **kubernetes:** handle missing subjects in k8s cluster role binding - [#4262](https://github.com/bridgecrewio/checkov/pull/4262)
- **kubernetes:** handle resources with incompatible selector - [#4257](https://github.com/bridgecrewio/checkov/pull/4257)
- **secrets:** Change secret validation status message - [#4250](https://github.com/bridgecrewio/checkov/pull/4250)
- **terraform:** default value for CKV_AZURE_5 - [#4237](https://github.com/bridgecrewio/checkov/pull/4237)
- **terraform:** fix get_current_module_index for path that contain .tf in them - [#4261](https://github.com/bridgecrewio/checkov/pull/4261)

## [2.2.264](https://github.com/bridgecrewio/checkov/compare/2.2.258...2.2.264) - 2023-01-15

### Feature

- **general:** fix circleci crash when cannot find image - [#4249](https://github.com/bridgecrewio/checkov/pull/4249)
- **general:** fix circleci yaml-doc - [#4246](https://github.com/bridgecrewio/checkov/pull/4246)
- **kubernetes:** set default k8s graph env vars to true - [#4225](https://github.com/bridgecrewio/checkov/pull/4225)
- **terraform:** Add new checks for ensuring execution history logging and Xray for State Machine is enabled  - [#4240](https://github.com/bridgecrewio/checkov/pull/4240)

### Bug Fix

- **cloudformation:** Fix edge-cases in checks - [#4251](https://github.com/bridgecrewio/checkov/pull/4251)
- **kubernetes:** removed env vars from tests - [#4252](https://github.com/bridgecrewio/checkov/pull/4252)
- **secrets:** Change secret validation status message - [#4238](https://github.com/bridgecrewio/checkov/pull/4238)
- **secrets:** Revert "fix(secrets): Change secret validation status message" - [#4248](https://github.com/bridgecrewio/checkov/pull/4248)

## [2.2.258](https://github.com/bridgecrewio/checkov/compare/2.2.257...2.2.258) - 2023-01-12

### Feature

- **terraform:** PC-Policy-Team - GCP PostgreSQL Instance Database Policies - [#4090](https://github.com/bridgecrewio/checkov/pull/4090)

## [2.2.257](https://github.com/bridgecrewio/checkov/compare/2.2.254...2.2.257) - 2023-01-11

### Bug Fix

- **secrets:** Change verify secrets key to include relative path - [#4232](https://github.com/bridgecrewio/checkov/pull/4232)
- **terraform:** improve cross-variable edges performance - [#4231](https://github.com/bridgecrewio/checkov/pull/4231)

## [2.2.254](https://github.com/bridgecrewio/checkov/compare/2.2.252...2.2.254) - 2023-01-10

### Feature

- **general:** Add resource attributes to omit arg - [#4193](https://github.com/bridgecrewio/checkov/pull/4193)
- **terraform:** enable cross variable edges - [#4224](https://github.com/bridgecrewio/checkov/pull/4224)

### Bug Fix

- **secrets:** add function to add the custom policies to the metadata integration not in the multiprocess - [#4221](https://github.com/bridgecrewio/checkov/pull/4221)

## [2.2.252](https://github.com/bridgecrewio/checkov/compare/2.2.246...2.2.252) - 2023-01-09

### Feature

- **kubernetes:** support more types of k8s pod template containers - [#4208](https://github.com/bridgecrewio/checkov/pull/4208)
- **secrets:** Add secret validation status to reduced report - [#4219](https://github.com/bridgecrewio/checkov/pull/4219)
- **secrets:** fix unquoted secret value - [#4214](https://github.com/bridgecrewio/checkov/pull/4214)
- **terraform_plan:** support multiple references in one resource - [#4206](https://github.com/bridgecrewio/checkov/pull/4206)

### Bug Fix

- **kubernetes:** allow filtering of custom with built-in Kubernetes check IDs - [#4204](https://github.com/bridgecrewio/checkov/pull/4204)
- **secrets:** add long to see metadata_integration - [#4220](https://github.com/bridgecrewio/checkov/pull/4220)
- **terraform_plan:** fix module resources ids - [#4211](https://github.com/bridgecrewio/checkov/pull/4211)

## [2.2.246](https://github.com/bridgecrewio/checkov/compare/2.2.239...2.2.246) - 2023-01-08

### Feature

- **dockerfile:** Add checks for unsafe wget and pip usages - [#4202](https://github.com/bridgecrewio/checkov/pull/4202)
- **secrets:** Implement lower entropy threshold on a line with keyword - [#4210](https://github.com/bridgecrewio/checkov/pull/4210)
- **terraform:** add CKV2_AWS_51 to Ensure AWS Managed IAMFullAccess IAM policy is not used. - [#4174](https://github.com/bridgecrewio/checkov/pull/4174)
- **terraform:** CDN and service bus checks for azure - [#4059](https://github.com/bridgecrewio/checkov/pull/4059)

### Bug Fix

- **secrets:** add logs - [#4215](https://github.com/bridgecrewio/checkov/pull/4215)
- **secrets:** add logs to secrets - [#4213](https://github.com/bridgecrewio/checkov/pull/4213)
- **secrets:** Disable verify secrets if skip_download is specified - [#4209](https://github.com/bridgecrewio/checkov/pull/4209)
- **secrets:** fix relative file path in secrets saved to coordinator - [#4212](https://github.com/bridgecrewio/checkov/pull/4212)

## [2.2.239](https://github.com/bridgecrewio/checkov/compare/2.2.238...2.2.239) - 2023-01-06

### Bug Fix

- **general:** fix incorrect billing message when frameworks are removed from --framework list - [#4201](https://github.com/bridgecrewio/checkov/pull/4201)

## [2.2.238](https://github.com/bridgecrewio/checkov/compare/2.2.234...2.2.238) - 2023-01-05

### Feature

- **dockerfile:** Add check for unsafe curl usages - [#4186](https://github.com/bridgecrewio/checkov/pull/4186)
- **general:** add logic to vcs scanning to prevent empty repo collabs failing check - [#4199](https://github.com/bridgecrewio/checkov/pull/4199)
- **terraform:** Adding yaml based build time policies for corresponding PC run time policies - [#4113](https://github.com/bridgecrewio/checkov/pull/4113)

### Bug Fix

- **general:** handle variable dependent values in policy - [#4200](https://github.com/bridgecrewio/checkov/pull/4200)
- **secrets:** Fix api key condition in verify_secrets - [#4195](https://github.com/bridgecrewio/checkov/pull/4195)
- **secrets:** Remove raw string modifier from re.compile - [#4197](https://github.com/bridgecrewio/checkov/pull/4197)

## [2.2.234](https://github.com/bridgecrewio/checkov/compare/2.2.230...2.2.234) - 2023-01-04

### Feature

- **sca:** enable CHECKOV_RUN_SCA_PACKAGE_SCAN_V2 env var - [#4192](https://github.com/bridgecrewio/checkov/pull/4192)
- **secrets:** Call secrets verify API - [#4181](https://github.com/bridgecrewio/checkov/pull/4181)

### Bug Fix

- **general:** set newer jsonschema dependency bound-  solves #2227 - [#4183](https://github.com/bridgecrewio/checkov/pull/4183)
- **general:** Update exclude-patterns.txt - [#4187](https://github.com/bridgecrewio/checkov/pull/4187)

### Documentation

- **general:** fix links in contributing docs - [#4184](https://github.com/bridgecrewio/checkov/pull/4184)

## [2.2.230](https://github.com/bridgecrewio/checkov/compare/2.2.229...2.2.230) - 2023-01-03

### Feature

- **general:** Skip check in json file - [#4172](https://github.com/bridgecrewio/checkov/pull/4172)

## [2.2.229](https://github.com/bridgecrewio/checkov/compare/2.2.220...2.2.229) - 2023-01-01

### Feature

- **gha:** add support for gha existing graph - [#4175](https://github.com/bridgecrewio/checkov/pull/4175)
- **secrets:** change secretsCoordinator to dict format - [#4169](https://github.com/bridgecrewio/checkov/pull/4169)
- **terraform:** added aws_ssoadmin_managed_policy_attachment resource to CKV_AWS_274 - [#4173](https://github.com/bridgecrewio/checkov/pull/4173)

### Bug Fix

- **general:** add link to BaseGraphRegistry checks - [#4177](https://github.com/bridgecrewio/checkov/pull/4177)
- **general:** change CODE_LINK_BASE from master to main - [#4178](https://github.com/bridgecrewio/checkov/pull/4178)
- **kubernetes:** remove unneeded context check - [#4171](https://github.com/bridgecrewio/checkov/pull/4171)
- **kustomize:** fixed kustomize abs_file_path - [#4159](https://github.com/bridgecrewio/checkov/pull/4159)
- **terraform:** out of range error by checking if list is empty - [#4176](https://github.com/bridgecrewio/checkov/pull/4176)

## [2.2.220](https://github.com/bridgecrewio/checkov/compare/2.2.217...2.2.220) - 2022-12-29

### Feature

- **sca:** remove report_results from checkov, as it is not used at all - [#4161](https://github.com/bridgecrewio/checkov/pull/4161)

### Bug Fix

- **general:** fix f-string log message - [#4170](https://github.com/bridgecrewio/checkov/pull/4170)

### Documentation

- **general:** fix reference link in Contributing docs page - [#4164](https://github.com/bridgecrewio/checkov/pull/4164)

## [2.2.217](https://github.com/bridgecrewio/checkov/compare/2.2.212...2.2.217) - 2022-12-28

### Feature

- **general:** Make code blocks for json check results focused on the relevant part - [#4130](https://github.com/bridgecrewio/checkov/pull/4130)
- **openapi:** Add v2 openAPI new checks - [#4112](https://github.com/bridgecrewio/checkov/pull/4112)
- **terraform:** new azure storage checks - [#4021](https://github.com/bridgecrewio/checkov/pull/4021)

### Bug Fix

- **github:** Handle entity configurations of type list - [#4160](https://github.com/bridgecrewio/checkov/pull/4160)
- **sca:** Fix extra space in output of dependencies - [#4162](https://github.com/bridgecrewio/checkov/pull/4162)

## [2.2.212](https://github.com/bridgecrewio/checkov/compare/2.2.207...2.2.212) - 2022-12-27

### Feature

- **azure:** Add check - azure keyvalut public network access - [#4155](https://github.com/bridgecrewio/checkov/pull/4155)

### Bug Fix

- **terraform:** fix edge-case in CKV_AZURE_183 check - [#4154](https://github.com/bridgecrewio/checkov/pull/4154)
- **terraform:** fix graph checks nested modules - [#4157](https://github.com/bridgecrewio/checkov/pull/4157)
- **terraform:** fix or connection graph checks nested modules - [#4158](https://github.com/bridgecrewio/checkov/pull/4158)

## [2.2.207](https://github.com/bridgecrewio/checkov/compare/2.2.201...2.2.207) - 2022-12-26

### Feature

- **kubernetes:** Support graph edges for nested (related) Pod resources. - [#4100](https://github.com/bridgecrewio/checkov/pull/4100)
- **secrets:** Keep original secrets data in runtime for further validation - [#4144](https://github.com/bridgecrewio/checkov/pull/4144)
- **secrets:** Keep original secrets data in runtime for further validation - [#4149](https://github.com/bridgecrewio/checkov/pull/4149)

### Bug Fix

- **general:** fix excluded paths for path with special characters - [#4152](https://github.com/bridgecrewio/checkov/pull/4152)
- **terraform:** add test path to exclude-patterns - [#4150](https://github.com/bridgecrewio/checkov/pull/4150)
- **terraform:** fix edge-case in CKV_AZURE_37 check - [#4153](https://github.com/bridgecrewio/checkov/pull/4153)
- **terraform:** fix getting graph entity config in terraform runner - [#4146](https://github.com/bridgecrewio/checkov/pull/4146)
- **terraform:** remove redundant nested definitions - [#4147](https://github.com/bridgecrewio/checkov/pull/4147)

## [2.2.201](https://github.com/bridgecrewio/checkov/compare/2.2.199...2.2.201) - 2022-12-25

### Bug Fix

- **secrets:** add support to conditionQuery - [#4086](https://github.com/bridgecrewio/checkov/pull/4086)
- **terraform:** fix edge-case in CKV_AZURE_183 check - [#4145](https://github.com/bridgecrewio/checkov/pull/4145)

## [2.2.199](https://github.com/bridgecrewio/checkov/compare/2.2.191...2.2.199) - 2022-12-22

### Feature

- **gha:** support on directive in workflow files - [#4125](https://github.com/bridgecrewio/checkov/pull/4125)
- **sca:** run old package scanning for IDE scan  - [#4133](https://github.com/bridgecrewio/checkov/pull/4133)
- **secrets:** expose maximum 6 characters of secret values - [#4140](https://github.com/bridgecrewio/checkov/pull/4140)

### Bug Fix

- **circleci:** add resource to ir - [#4135](https://github.com/bridgecrewio/checkov/pull/4135)
- **general:** Reformat PR template - [#4139](https://github.com/bridgecrewio/checkov/pull/4139)
- **kubernetes:** move Kubernetes context error message - [#4132](https://github.com/bridgecrewio/checkov/pull/4132)
- **terraform:** add aws_transfer_server to CKV2_AWS_5 check - [#4137](https://github.com/bridgecrewio/checkov/pull/4137)
- **terraform:** Add some more supported keys to bigquery public acl check ignore list to avoid false positive - [#3969](https://github.com/bridgecrewio/checkov/pull/3969)
- **terraform:** fix azure network address invalid value - [#4131](https://github.com/bridgecrewio/checkov/pull/4131)

## [2.2.191](https://github.com/bridgecrewio/checkov/compare/2.2.186...2.2.191) - 2022-12-21

### Feature

- **general:** add the stack trace to the error message when caught by main.py - [#4121](https://github.com/bridgecrewio/checkov/pull/4121)
- **sca:** add GCP Terraform resources for Image Referencer - [#4094](https://github.com/bridgecrewio/checkov/pull/4094)
- **sca:** protecting checkov with try/catch wrapping - [#4104](https://github.com/bridgecrewio/checkov/pull/4104)

### Bug Fix

- **kubernetes:** removed obsolete error logging - [#4126](https://github.com/bridgecrewio/checkov/pull/4126)
- **terraform:** fix azure dns invalid ip - [#4128](https://github.com/bridgecrewio/checkov/pull/4128)

## [2.2.186](https://github.com/bridgecrewio/checkov/compare/2.2.180...2.2.186) - 2022-12-20

### Feature

- **general:** move the jsonpath try/catch up a level to catch more errors - [#3911](https://github.com/bridgecrewio/checkov/pull/3911)
- **sca:** returning exit code 2 in case of error for downloading twistcli - [#4105](https://github.com/bridgecrewio/checkov/pull/4105)

### Bug Fix

- **dockerfile:** adjust the file abs path for Dockerfile graph results - [#4118](https://github.com/bridgecrewio/checkov/pull/4118)
- **openapi:** fix an open API CKV_OPENAPI_6 check - [#4109](https://github.com/bridgecrewio/checkov/pull/4109)
- **sca:** fixing integration tests - [#4117](https://github.com/bridgecrewio/checkov/pull/4117)
- **terraform_plan:** use abs path for repo_root_for_plan_enrichment - [#4115](https://github.com/bridgecrewio/checkov/pull/4115)
- **terraform:** CKV2_AZURE_21 changed blob access type to private - [#3898](https://github.com/bridgecrewio/checkov/pull/3898)
- **terraform:** fix support for getting module-referenced resources context - [#4110](https://github.com/bridgecrewio/checkov/pull/4110)

### Platform

- **terraform:** add previous get_tf_definition_key function - [#4114](https://github.com/bridgecrewio/checkov/pull/4114)

## [2.2.180](https://github.com/bridgecrewio/checkov/compare/2.2.172...2.2.180) - 2022-12-19

### Feature

- **general:** Use --no-fail-on-crash to gracefully exit commit_repository and setup_bridgecrew_credentials - [#4099](https://github.com/bridgecrewio/checkov/pull/4099)
- **terraform_plan:** add check details to TF plan scan results - [#4091](https://github.com/bridgecrewio/checkov/pull/4091)
- **terraform:** new azurerm checks - App config - [#3988](https://github.com/bridgecrewio/checkov/pull/3988)
- **terraform:** Omit values from graph checks - [#4076](https://github.com/bridgecrewio/checkov/pull/4076)

### Bug Fix

- **general:** change env var name for no-fail-on-crash flag - [#4107](https://github.com/bridgecrewio/checkov/pull/4107)
- **github:** Fix GHA IR resource names in case of 2 identical images - [#4108](https://github.com/bridgecrewio/checkov/pull/4108)
- **terraform:** azurerm storage defaults - fix for storage case #3516 - [#4083](https://github.com/bridgecrewio/checkov/pull/4083)
- **terraform:** fix nested module resources ids in the report - [#4098](https://github.com/bridgecrewio/checkov/pull/4098)

## [2.2.172](https://github.com/bridgecrewio/checkov/compare/2.2.168...2.2.172) - 2022-12-18

### Feature

- **general:** Add no-fail-on-crash flag - [#4097](https://github.com/bridgecrewio/checkov/pull/4097)
- **gha:** add fix for gha graphs and UT - [#4084](https://github.com/bridgecrewio/checkov/pull/4084)
- **kubernetes:** inject k8s FF flags to instance instead of constructor - [#4096](https://github.com/bridgecrewio/checkov/pull/4096)

### Bug Fix

- **terraform:** add a method for get the entity definition path from the entity itself - [#4095](https://github.com/bridgecrewio/checkov/pull/4095)
- **terraform:** add address attribute to all scanned terraform blocks - [#4074](https://github.com/bridgecrewio/checkov/pull/4074)

## [2.2.168](https://github.com/bridgecrewio/checkov/compare/2.2.158...2.2.168) - 2022-12-15

### Feature

- **kubernetes:** Add kubernetes YAML checks to checkov packaging - [#4073](https://github.com/bridgecrewio/checkov/pull/4073)
- **kubernetes:** move whorf to dedicated repo - [#4062](https://github.com/bridgecrewio/checkov/pull/4062)
- **terraform_plan:** add Image Referencer for Terraform plan files - [#4063](https://github.com/bridgecrewio/checkov/pull/4063)
- **terraform:** add CKV NCP rules about AutoScalingGroup, Load Balancer - [#3821](https://github.com/bridgecrewio/checkov/pull/3821)
- **terraform:** add CKV NCP rules about Nat Gateways and Route - [#3854](https://github.com/bridgecrewio/checkov/pull/3854)
- **terraform:** combine tf plan and tf graphs for nested modules - [#4066](https://github.com/bridgecrewio/checkov/pull/4066)
- **terraform:** More azurerm checks for terraform - [#3970](https://github.com/bridgecrewio/checkov/pull/3970)

### Bug Fix

- **openapi:** Fix in PathSchemeDefineHTTP opeAPI check - [#4079](https://github.com/bridgecrewio/checkov/pull/4079)
- **terraform:** CKV_AZURE_43 add new test case - [#4082](https://github.com/bridgecrewio/checkov/pull/4082)

## [2.2.158](https://github.com/bridgecrewio/checkov/compare/2.2.155...2.2.158) - 2022-12-14

### Feature

- **github:** more CIS checks- part3  - [#4057](https://github.com/bridgecrewio/checkov/pull/4057)
- **terraform:** Adding yaml based build time policies for corresponding PC run time policies - [#3962](https://github.com/bridgecrewio/checkov/pull/3962)

### Bug Fix

- **secrets:** fix secrets crash when secret is non string - [#4077](https://github.com/bridgecrewio/checkov/pull/4077)

## [2.2.155](https://github.com/bridgecrewio/checkov/compare/2.2.148...2.2.155) - 2022-12-13

### Feature

- **github:**  more CIS checks- part2 - [#4017](https://github.com/bridgecrewio/checkov/pull/4017)
- **kubernetes:** added CKV2_K8S_EXAMPLE_1 only in tests as an example for k8s graph check for pod which is publicly accessible - [#4060](https://github.com/bridgecrewio/checkov/pull/4060)
- **kubernetes:** added deployment name to pod resource id - [#4040](https://github.com/bridgecrewio/checkov/pull/4040)
- **sca:** fix root packages fixed version - [#4070](https://github.com/bridgecrewio/checkov/pull/4070)

### Bug Fix

- **sca:** invoke packaging.Version instead of parse - [#4065](https://github.com/bridgecrewio/checkov/pull/4065)
- **secrets:** fix error when secret is None - [#4071](https://github.com/bridgecrewio/checkov/pull/4071)
- **terraform:** checkov fix as resource container_group modified - [#4061](https://github.com/bridgecrewio/checkov/pull/4061)
- **terraform:** fixed unexpected data for IAMPublicActionsPolicy - [#4067](https://github.com/bridgecrewio/checkov/pull/4067)
- **terraform:** fixed unexpected data for MonitorLogProfileRetentionDays - [#4068](https://github.com/bridgecrewio/checkov/pull/4068)

### Platform

- **general:** Apply licensing from platform - [#3961](https://github.com/bridgecrewio/checkov/pull/3961)

## [2.2.148](https://github.com/bridgecrewio/checkov/compare/2.2.139...2.2.148) - 2022-12-12

### Feature

- **gha:** Add gha graph infra - [#4058](https://github.com/bridgecrewio/checkov/pull/4058)
- **gha:** add infra for gha graphs - [#4052](https://github.com/bridgecrewio/checkov/pull/4052)
- **sca:**  fixed dependencies default value - [#4056](https://github.com/bridgecrewio/checkov/pull/4056)
- **sca:** added indirect cves fix versions - [#4023](https://github.com/bridgecrewio/checkov/pull/4023)
- **secrets:** Inject secrets omitter to runner registry - [#4054](https://github.com/bridgecrewio/checkov/pull/4054)
- **terraform_plan:** support jsonpath queries in AWS IAM policy strings for Terraform plan - [#4033](https://github.com/bridgecrewio/checkov/pull/4033)
- **terraform:** Extend secret attributes to omit mapping - [#4028](https://github.com/bridgecrewio/checkov/pull/4028)
- **terraform:** tf plan combine graphs pass params - [#4051](https://github.com/bridgecrewio/checkov/pull/4051)

### Bug Fix

- **terraform:** add missing resource aws_route53_resolver_endpoint #3968 - [#3995](https://github.com/bridgecrewio/checkov/pull/3995)
- **terraform:** fix getting local dest module path - [#4055](https://github.com/bridgecrewio/checkov/pull/4055)
- **terraform:** Fix some errors in Dynamic Blocks rendering - [#4050](https://github.com/bridgecrewio/checkov/pull/4050)

## [2.2.139](https://github.com/bridgecrewio/checkov/compare/2.2.130...2.2.139) - 2022-12-11

### Feature

- **graph:** Added `not_within` attribute solver for graph checks - [#4041](https://github.com/bridgecrewio/checkov/pull/4041)
- **kubernetes:** Add CKV2_K8S_2 graph check for potential privilege escalation in `nodes/proxy` or `pods/exec` with `create` permissions - [#4034](https://github.com/bridgecrewio/checkov/pull/4034)
- **kubernetes:** Add CKV2_K8S_3 no `impersonate` permissions for `ServiceAccount/Node` - [#4037](https://github.com/bridgecrewio/checkov/pull/4037)
- **kubernetes:** Added CKV2_K8S_4 check to not allow modifying of services/status - [#4038](https://github.com/bridgecrewio/checkov/pull/4038)
- **kubernetes:** Added CKV2_K8S_5 check that no service account or node can read all secrets - [#4042](https://github.com/bridgecrewio/checkov/pull/4042)
- **secrets:** Accepting json reports from bucket in secrets_omitter - [#4039](https://github.com/bridgecrewio/checkov/pull/4039)
- **terraform:** add CKV NCP rules about Route Table Association - [#3856](https://github.com/bridgecrewio/checkov/pull/3856)

### Bug Fix

- **kubernetes:** Corrected list format for yaml files in new k8s graph check tests - [#4035](https://github.com/bridgecrewio/checkov/pull/4035)
- **secrets:** custom secret add support for value str and not only list - [#4024](https://github.com/bridgecrewio/checkov/pull/4024)
- **terraform:** Fix in dot separator in the dynamic argument - [#4036](https://github.com/bridgecrewio/checkov/pull/4036)

## [2.2.130](https://github.com/bridgecrewio/checkov/compare/2.2.124...2.2.130) - 2022-12-08

### Feature

- **general:** Apply policy-level suppressions as skipped checks - [#4020](https://github.com/bridgecrewio/checkov/pull/4020)
- **github:** Add 3 CIS checks: 1.1.3, 1.1.8, 1.1.10 - [#4003](https://github.com/bridgecrewio/checkov/pull/4003)
- **kubernetes:** Added CKV2_K8S_1 to ensure RoleBinding do not allow privilege escalation to a ServiceAccount/Node - [#4004](https://github.com/bridgecrewio/checkov/pull/4004)
- **secrets:** Omit secrets from reports based on secrets reports - [#3991](https://github.com/bridgecrewio/checkov/pull/3991)
- **secrets:** Omit secrets from reports based on secrets reports - [#4015](https://github.com/bridgecrewio/checkov/pull/4015)

### Bug Fix

- **github:** remove secrets from schema example - [#4019](https://github.com/bridgecrewio/checkov/pull/4019)
- **terraform:** fix resource block address - [#4018](https://github.com/bridgecrewio/checkov/pull/4018)

## [2.2.124](https://github.com/bridgecrewio/checkov/compare/2.2.116...2.2.124) - 2022-12-07

### Feature

- **sca:** change sca packages output to include dependencies structure - [#3957](https://github.com/bridgecrewio/checkov/pull/3957)
- **secrets:** Adding check length for secret - [#3985](https://github.com/bridgecrewio/checkov/pull/3985)
- **terraform:** nested modules support in graph - [#3935](https://github.com/bridgecrewio/checkov/pull/3935)

### Bug Fix

- **circleci:** fix executors in resource_id - [#4008](https://github.com/bridgecrewio/checkov/pull/4008)
- **secrets:** Bump detect secrets version - [#3997](https://github.com/bridgecrewio/checkov/pull/3997)
- **terraform:** Fix an issue in dynamic blocks - [#4006](https://github.com/bridgecrewio/checkov/pull/4006)
- **terraform:** fix CKV_AWS_283 check - [#4005](https://github.com/bridgecrewio/checkov/pull/4005)
- **terraform:** Fix CKV_AZURE_168 check - [#4000](https://github.com/bridgecrewio/checkov/pull/4000)
- **terraform:** Fix some issues in dynamic blocks flow - [#4002](https://github.com/bridgecrewio/checkov/pull/4002)
- **terraform:** Fix TF checks crashes - [#3992](https://github.com/bridgecrewio/checkov/pull/3992)

## [2.2.116](https://github.com/bridgecrewio/checkov/compare/2.2.114...2.2.116) - 2022-12-06

### Feature

- **general:** Report failed attempts at reporting contributor metrics - [#3984](https://github.com/bridgecrewio/checkov/pull/3984)
- **kubernetes:** create simple resources id for pods; allow enabling k8s graph features using env vars - [#3975](https://github.com/bridgecrewio/checkov/pull/3975)
- **terraform:** check for insecure protocols - [#3958](https://github.com/bridgecrewio/checkov/pull/3958)
- **terraform:** Check resource-based policies for public access - [#3989](https://github.com/bridgecrewio/checkov/pull/3989)
- **terraform:** Dynamic Blocks support for loop in for_each attribute - [#3982](https://github.com/bridgecrewio/checkov/pull/3982)
- **terraform:** new aks checks for Azure - [#3951](https://github.com/bridgecrewio/checkov/pull/3951)

### Bug Fix

- **dockerfile:** fix Dockerfile inline skip handling - [#3976](https://github.com/bridgecrewio/checkov/pull/3976)
- **secrets:** fix_Record_code_block_secrets - [#3987](https://github.com/bridgecrewio/checkov/pull/3987)
- **terraform:** azurerm kusto cluster encryption - wrong attribute tested for - [#3972](https://github.com/bridgecrewio/checkov/pull/3972)

## [2.2.114](https://github.com/bridgecrewio/checkov/compare/2.2.112...2.2.114) - 2022-12-04

### Feature

- **terraform:** add CKV NCP rules about ncloud access control group rule - [#3860](https://github.com/bridgecrewio/checkov/pull/3860)

### Bug Fix

- **secrets:** fix Issue with 'NoneType' error in the custom detectors load_detectors - [#3973](https://github.com/bridgecrewio/checkov/pull/3973)

### Platform

- **terraform:** remove redundant exc_info for module without source - [#3974](https://github.com/bridgecrewio/checkov/pull/3974)

## [2.2.112](https://github.com/bridgecrewio/checkov/compare/2.2.106...2.2.112) - 2022-12-01

### Feature

- **dockerfile:** add graph to Dockerfile - [#3948](https://github.com/bridgecrewio/checkov/pull/3948)
- **terraform:** add CKV NCP rules about access control group Inbound rule. - [#3859](https://github.com/bridgecrewio/checkov/pull/3859)
- **terraform:** Implement relative file path standard for tf plan file runs - [#3918](https://github.com/bridgecrewio/checkov/pull/3918)

### Bug Fix

- **general:** fix doc links on windows - [#3959](https://github.com/bridgecrewio/checkov/pull/3959)
- **secrets:** Fix omitting of secrets that are json encoded - [#3964](https://github.com/bridgecrewio/checkov/pull/3964)
- **terraform_plan:** Fix k8s checks edgecases for terraform plan - [#3966](https://github.com/bridgecrewio/checkov/pull/3966)
- **terraform:** OCI Security Group Control Problem - [#3933](https://github.com/bridgecrewio/checkov/pull/3933)

### Platform

- **secrets:** remove the use of enable_secret_scan_all_files for custom secrets - [#3954](https://github.com/bridgecrewio/checkov/pull/3954)

### Documentation

- **terraform:** update Terraform modules docs - [#3965](https://github.com/bridgecrewio/checkov/pull/3965)

## [2.2.106](https://github.com/bridgecrewio/checkov/compare/2.2.105...2.2.106) - 2022-11-30

- no noteworthy changes

## [2.2.105](https://github.com/bridgecrewio/checkov/compare/2.2.99...2.2.105) - 2022-11-29

### Feature

- **terraform:** add CKV NCP rules about Load Balancer Listener Using HTTPS - [#3858](https://github.com/bridgecrewio/checkov/pull/3858)
- **terraform:** add CKV NCP rules about server instance and public IP - [#3857](https://github.com/bridgecrewio/checkov/pull/3857)
- **terraform:** azurerm ACR check for retention policy - [#3927](https://github.com/bridgecrewio/checkov/pull/3927)

## [2.2.99](https://github.com/bridgecrewio/checkov/compare/2.2.96...2.2.99) - 2022-11-27

### Feature

- **github:** add CIS checks part 1.  Most of the 1.1.x - [#3937](https://github.com/bridgecrewio/checkov/pull/3937)
- **terraform:** Azure ACR Enable Image Quarantine - [#3925](https://github.com/bridgecrewio/checkov/pull/3925)
- **terraform:** Azure use signed image in ACR - [#3923](https://github.com/bridgecrewio/checkov/pull/3923)

### Bug Fix

- **bicep:** ignore unresolvable properties for Bicep storage account checks - [#3946](https://github.com/bridgecrewio/checkov/pull/3946)
- **gha:** added test for step with no step name - [#3945](https://github.com/bridgecrewio/checkov/pull/3945)

## [2.2.96](https://github.com/bridgecrewio/checkov/compare/2.2.95...2.2.96) - 2022-11-26

- no noteworthy changes

## [2.2.95](https://github.com/bridgecrewio/checkov/compare/2.2.86...2.2.95) - 2022-11-24

### Feature

- **circleci:** add check for detecting images without check resource - [#3930](https://github.com/bridgecrewio/checkov/pull/3930)
- **terraform:** ACR container scanning - [#3922](https://github.com/bridgecrewio/checkov/pull/3922)
- **terraform:** add CKV NCP check about NKS(kubernetes) logging - [#3855](https://github.com/bridgecrewio/checkov/pull/3855)
- **terraform:** Adding yaml based build time policies for corresponding PC run time policies - [#3900](https://github.com/bridgecrewio/checkov/pull/3900)

### Bug Fix

- **general:** update checks_metadata structure - [#3929](https://github.com/bridgecrewio/checkov/pull/3929)
- **gha:** and circleci resource names  - [#3914](https://github.com/bridgecrewio/checkov/pull/3914)
- **kubernetes:** Handle invalid helm chart meta - [#3939](https://github.com/bridgecrewio/checkov/pull/3939)
- **sca:** fix related resource id for helm and kustomize - [#3931](https://github.com/bridgecrewio/checkov/pull/3931)
- **terraform:** better check names to avoid confusion - addresses #3912 - [#3921](https://github.com/bridgecrewio/checkov/pull/3921)
- **terraform:** CKV_AZURE_144 passes on defaults - [#3938](https://github.com/bridgecrewio/checkov/pull/3938)
- **terraform:** Removed duplicate check CKV_AZURE_60 - [#3928](https://github.com/bridgecrewio/checkov/pull/3928)

### Platform

- **secrets:** Support custom detectors from the platform - [#3926](https://github.com/bridgecrewio/checkov/pull/3926)

## [2.2.86](https://github.com/bridgecrewio/checkov/compare/2.2.84...2.2.86) - 2022-11-23

### Feature

- **terraform:** add CKV_AWS_282 to ensure that Redshift Serverless namespace is encrypted by KMS - [#3915](https://github.com/bridgecrewio/checkov/pull/3915)

### Bug Fix

- **terraform:** Remove cross variables edges duplications - [#3920](https://github.com/bridgecrewio/checkov/pull/3920)

## [2.2.84](https://github.com/bridgecrewio/checkov/compare/2.2.80...2.2.84) - 2022-11-22

### Feature

- **general:** sign and push checkov image to GitHub registry - [#3906](https://github.com/bridgecrewio/checkov/pull/3906)
- **secrets:** Add Terraform multiline secrets handling - [#3907](https://github.com/bridgecrewio/checkov/pull/3907)
- **terraform:** ensure snapshots use encryption - [#3899](https://github.com/bridgecrewio/checkov/pull/3899)
- **terraform:** support cross-modules edges - [#3909](https://github.com/bridgecrewio/checkov/pull/3909)

## [2.2.80](https://github.com/bridgecrewio/checkov/compare/2.2.78...2.2.80) - 2022-11-21

### Feature

- **terraform:** add nested module address attribute - [#3904](https://github.com/bridgecrewio/checkov/pull/3904)

## [2.2.78](https://github.com/bridgecrewio/checkov/compare/2.2.75...2.2.78) - 2022-11-20

### Feature

- **general:** add output format cyclonedx_json - [#3902](https://github.com/bridgecrewio/checkov/pull/3902)
- **general:** add source to contributor metrics report - [#3905](https://github.com/bridgecrewio/checkov/pull/3905)

### Bug Fix

- **terraform:** Fix an edge case in AbsRDSParameter check  - [#3903](https://github.com/bridgecrewio/checkov/pull/3903)

## [2.2.75](https://github.com/bridgecrewio/checkov/compare/2.2.72...2.2.75) - 2022-11-17

### Feature

- **github:** add output-file-path flag to checkov-action - [#3897](https://github.com/bridgecrewio/checkov/pull/3897)

### Bug Fix

- **terraform:** Dynamic blocks - added support for lookup null/true/false values - [#3893](https://github.com/bridgecrewio/checkov/pull/3893)

### Platform

- **sca:** added dependency tree format  - [#3892](https://github.com/bridgecrewio/checkov/pull/3892)

## [2.2.72](https://github.com/bridgecrewio/checkov/compare/2.2.65...2.2.72) - 2022-11-16

### Feature

- **terraform:** add CKV NCP rules about NKSPublicAccess - [#3822](https://github.com/bridgecrewio/checkov/pull/3822)
- **terraform:** Censor secrets from tfplan graph - [#3894](https://github.com/bridgecrewio/checkov/pull/3894)
- **terraform:** create cross-variable edges between resources from the same module - [#3881](https://github.com/bridgecrewio/checkov/pull/3881)

### Bug Fix

- **general:** remove filter value validation - [#3896](https://github.com/bridgecrewio/checkov/pull/3896)
- **terraform:** Fix dynamic blocks nested module - [#3890](https://github.com/bridgecrewio/checkov/pull/3890)
- **terraform:** handle empty enabled_cluster_log_types list - [#3891](https://github.com/bridgecrewio/checkov/pull/3891)

### Platform

- **sca:** add scaCliScanId parameter - [#3789](https://github.com/bridgecrewio/checkov/pull/3789)

## [2.2.65](https://github.com/bridgecrewio/checkov/compare/2.2.58...2.2.65) - 2022-11-15

### Feature

- **terraform:** test checks for any port access - [#3882](https://github.com/bridgecrewio/checkov/pull/3882)

### Bug Fix

- **terraform:** Fixing some broke flow in dynamic blocks rendering - [#3879](https://github.com/bridgecrewio/checkov/pull/3879)
- **terraform:** Not adding dynamic blocks attributes to attributes - [#3872](https://github.com/bridgecrewio/checkov/pull/3872)

### Platform

- **general:** Support s3 client config for govcloud - [#3880](https://github.com/bridgecrewio/checkov/pull/3880)
- **sca:** Add repoId to GET request - [#3876](https://github.com/bridgecrewio/checkov/pull/3876)
- **sca:** Fix bom report - [#3867](https://github.com/bridgecrewio/checkov/pull/3867)
- **sca:** Poll sca scan results using Polling API - [#3841](https://github.com/bridgecrewio/checkov/pull/3841)
- **sca:** remove src from repo path - [#3884](https://github.com/bridgecrewio/checkov/pull/3884)

## [2.2.58](https://github.com/bridgecrewio/checkov/compare/2.2.50...2.2.58) - 2022-11-14

### Feature

- **general:** number of words larger/less than or equal operators - [#3827](https://github.com/bridgecrewio/checkov/pull/3827)
- **general:** remove env var for running contributor metrics report and add logs - [#3873](https://github.com/bridgecrewio/checkov/pull/3873)
- **terraform:** add CKV NCP rules about Load Balancer Exposed to Internet - [#3819](https://github.com/bridgecrewio/checkov/pull/3819)
- **terraform:** Mask secret values in Terraform plan file reports by resource - [#3868](https://github.com/bridgecrewio/checkov/pull/3868)
- **terraform:** Support dynamic blocks with nested attributes - [#3869](https://github.com/bridgecrewio/checkov/pull/3869)

### Bug Fix

- **general:** Fixed operator name for number_of_words_derivaties - [#3875](https://github.com/bridgecrewio/checkov/pull/3875)
- **terraform:** Fix dynamic attributes override each other - [#3866](https://github.com/bridgecrewio/checkov/pull/3866)

## [2.2.50](https://github.com/bridgecrewio/checkov/compare/2.2.44...2.2.50) - 2022-11-13

### Feature

- **general:** add reporting contributor metrics - [#3823](https://github.com/bridgecrewio/checkov/pull/3823)
- **terraform:** add CKV NCP rules about access key hard coding - [#3820](https://github.com/bridgecrewio/checkov/pull/3820)
- **terraform:** NSGRulePortAccessRestricted - Remove the condition for dynamic blocks - [#3862](https://github.com/bridgecrewio/checkov/pull/3862)

### Bug Fix

- **kubernetes:** handle empty spec object in k8s templates - [#3865](https://github.com/bridgecrewio/checkov/pull/3865)
- **openapi:** fixed error in invalid openapi template - [#3863](https://github.com/bridgecrewio/checkov/pull/3863)
- **terraform:** app_service Upgrade tests and add web app resources - [#3838](https://github.com/bridgecrewio/checkov/pull/3838)
- **terraform:** Handled nested unrendered vars - [#3853](https://github.com/bridgecrewio/checkov/pull/3853)

## [2.2.44](https://github.com/bridgecrewio/checkov/compare/2.2.43...2.2.44) - 2022-11-11

### Bug Fix

- **terraform:** fix an issue with dynamics replacing a whole block - [#3846](https://github.com/bridgecrewio/checkov/pull/3846)

## [2.2.43](https://github.com/bridgecrewio/checkov/compare/2.2.38...2.2.43) - 2022-11-10

### Feature

- **terraform:** Wrap render dynamic blocks flow with try except - [#3837](https://github.com/bridgecrewio/checkov/pull/3837)

### Bug Fix

- **bicep:** make ARM AKS checks compatible with Bicep - [#3836](https://github.com/bridgecrewio/checkov/pull/3836)
- **cloudformation:** only parse valid tag key-pairs in CloudFormation - [#3835](https://github.com/bridgecrewio/checkov/pull/3835)
- **general:** Clear details before next check run to avoid duplications in output - [#3711](https://github.com/bridgecrewio/checkov/pull/3711)

## [2.2.38](https://github.com/bridgecrewio/checkov/compare/2.2.35...2.2.38) - 2022-11-09

### Feature

- **secrets:** add abstract multiline parser + implement multiline json parser - [#3799](https://github.com/bridgecrewio/checkov/pull/3799)
- **terraform:** Support for nested dynamic modules - [#3813](https://github.com/bridgecrewio/checkov/pull/3813)

### Bug Fix

- **kubernetes:** fixed unexpected list object - [#3833](https://github.com/bridgecrewio/checkov/pull/3833)

## [2.2.35](https://github.com/bridgecrewio/checkov/compare/2.2.31...2.2.35) - 2022-11-08

### Feature

- **general:** Added Number of Words operator - [#3801](https://github.com/bridgecrewio/checkov/pull/3801)
- **terraform:** add CKV NCP rules about LBTargetGroupUsingHTTPS - [#3797](https://github.com/bridgecrewio/checkov/pull/3797)
- **terraform:** add CKV NCP rules about NASEncrytionEnabled - [#3796](https://github.com/bridgecrewio/checkov/pull/3796)
- **terraform:** Add Env Var for rendering Dynamic Blocks - [#3816](https://github.com/bridgecrewio/checkov/pull/3816)
- **terraform:** Dynamic blocks breadcrumbs support - [#3814](https://github.com/bridgecrewio/checkov/pull/3814)
- **terraform:** PC Policy Team Yaml Policies Check-in - [#3785](https://github.com/bridgecrewio/checkov/pull/3785)
- **terraform:** PC-Policy-Team: Ensure GCP compute firewall ingress does not allow unrestricted access to all ports - [#3786](https://github.com/bridgecrewio/checkov/pull/3786)

### Platform

- **sca:** Run package scan using API - [#3812](https://github.com/bridgecrewio/checkov/pull/3812)

## [2.2.31](https://github.com/bridgecrewio/checkov/compare/2.2.22...2.2.31) - 2022-11-07

### Feature

- **azure:** Add get resource names for azure_pipelines - [#3798](https://github.com/bridgecrewio/checkov/pull/3798)
- **github:** add graph to GitHub Actions - [#3672](https://github.com/bridgecrewio/checkov/pull/3672)
- **terraform:** add CKV NCP rules about LBListenerUsesSecureProtocols - [#3782](https://github.com/bridgecrewio/checkov/pull/3782)
- **terraform:** Dynamic Modules Support map type - [#3800](https://github.com/bridgecrewio/checkov/pull/3800)
- **terraform:** include pods of kubernetes_deployment in kubernetes_pod checks (1/4) - [#3691](https://github.com/bridgecrewio/checkov/pull/3691)
- **terraform:** include pods of kubernetes_deployment in kubernetes_pod checks (2/4) - [#3702](https://github.com/bridgecrewio/checkov/pull/3702)
- **terraform:** include pods of kubernetes_deployment in kubernetes_pod checks (3/4) - [#3703](https://github.com/bridgecrewio/checkov/pull/3703)
- **terraform:** include pods of kubernetes_deployment in kubernetes_pod checks (4/4) - [#3738](https://github.com/bridgecrewio/checkov/pull/3738)

### Bug Fix

- **arm:** CKV_AZURE_9 & CKV_AZURE_10 - Scan fails if protocol value is a wildcard - [#3750](https://github.com/bridgecrewio/checkov/pull/3750)
- **azure:** Remove redundant file path from resource name in azure pipelines - [#3818](https://github.com/bridgecrewio/checkov/pull/3818)
- **secrets:** fix slow secrets scan in yaml files - [#3803](https://github.com/bridgecrewio/checkov/pull/3803)
- **secrets:** fixed path of secrets tests to exclude - [#3817](https://github.com/bridgecrewio/checkov/pull/3817)
- **terraform:** fix gke resource name not string - [#3811](https://github.com/bridgecrewio/checkov/pull/3811)

### Platform

- **general:** rationalize policy metadata error handling behavior - [#3795](https://github.com/bridgecrewio/checkov/pull/3795)
- **sca:** add new sca package scan - [#3802](https://github.com/bridgecrewio/checkov/pull/3802)
- **sca:** Extract checkov check links - [#3790](https://github.com/bridgecrewio/checkov/pull/3790)

## [2.2.22](https://github.com/bridgecrewio/checkov/compare/2.2.21...2.2.22) - 2022-11-06

### Feature

- **kubernetes:** Create keyword and network policy edge builders - [#3763](https://github.com/bridgecrewio/checkov/pull/3763)

## [2.2.21](https://github.com/bridgecrewio/checkov/compare/2.2.17...2.2.21) - 2022-11-03

### Feature

- **general:** add range_includes and inverted operator - [#3752](https://github.com/bridgecrewio/checkov/pull/3752)
- **secrets:** Add multiline detection to entropy keyword combinator - [#3788](https://github.com/bridgecrewio/checkov/pull/3788)

### Bug Fix

- **terraform:** render list entries via modules correctly - [#3781](https://github.com/bridgecrewio/checkov/pull/3781)

## [2.2.17](https://github.com/bridgecrewio/checkov/compare/2.2.15...2.2.17) - 2022-11-02

### Feature

- **terraform:** Add CKV_AWS_276 to ensure that API Gateway Method Settings data_trace_enabled is not set to True - [#3761](https://github.com/bridgecrewio/checkov/pull/3761)

### Bug Fix

- **terraform:** Fix `related_resource_id` for ImageReferencer in `external_module` - [#3780](https://github.com/bridgecrewio/checkov/pull/3780)

### Documentation

- **general:** Fix typo in docs - [#3694](https://github.com/bridgecrewio/checkov/pull/3694)

## [2.2.15](https://github.com/bridgecrewio/checkov/compare/2.2.8...2.2.15) - 2022-10-31

### Feature

- **github:** split repo and org webhooks to separate files - [#3764](https://github.com/bridgecrewio/checkov/pull/3764)
- **gitlab:** Adding image detection check to gitlab ci - [#3774](https://github.com/bridgecrewio/checkov/pull/3774)
- **openapi:** pre-validate OpenAPI JSON files - [#3760](https://github.com/bridgecrewio/checkov/pull/3760)

### Bug Fix

- **azure:** Support .yaml extension - [#3767](https://github.com/bridgecrewio/checkov/pull/3767)
- **github:** print the result again in GHA - [#3751](https://github.com/bridgecrewio/checkov/pull/3751)
- **terraform:** reduce parsing time for large TF plan files - [#3757](https://github.com/bridgecrewio/checkov/pull/3757)

## [2.2.8](https://github.com/bridgecrewio/checkov/compare/2.2.5...2.2.8) - 2022-10-30

### Feature

- **terraform:** add CKV2_AWS_40 to Ensure AWS IAM policy does not allow full IAM privileges - [#3712](https://github.com/bridgecrewio/checkov/pull/3712)

### Platform

- **general:** Get resources from platform and filter taggable resources for policies - [#3621](https://github.com/bridgecrewio/checkov/pull/3621)

## [2.2.5](https://github.com/bridgecrewio/checkov/compare/2.2.0...2.2.5) - 2022-10-27

### Feature

- **graph:** add support for modules in graph checks - [#3635](https://github.com/bridgecrewio/checkov/pull/3635)
- **terraform:** add CKV NCP rules about Network ACL. - [#3668](https://github.com/bridgecrewio/checkov/pull/3668)
- **terraform:** TF Dynamic Blocks support - `for_each` lists type - [#3737](https://github.com/bridgecrewio/checkov/pull/3737)

### Bug Fix

- **terraform:** fix a TF plan issue with CKV_AWS_274 - [#3747](https://github.com/bridgecrewio/checkov/pull/3747)
- **terraform:** fix false positive for write ACL yaml check - [#3745](https://github.com/bridgecrewio/checkov/pull/3745)

### Documentation

- **general:** Update Jenkins page to use Checkov image - [#3725](https://github.com/bridgecrewio/checkov/pull/3725)

## [2.2.0](https://github.com/bridgecrewio/checkov/compare/2.1.294...2.2.0) - 2022-10-26

### Breaking Change

- **github:** Change github_failed_only output suffix to .md - [#3595](https://github.com/bridgecrewio/checkov/pull/3595)
- **terraform:** adjust the check result return for dependant variables to unknown in  Python based checks - [#3743](https://github.com/bridgecrewio/checkov/pull/3743)
- **terraform:** return UNKNOWN for unrendered values in graph checks - [#3689](https://github.com/bridgecrewio/checkov/pull/3689)

### Feature

- **terraform:** add CKV NCP rule about block storage encryption. - [#3628](https://github.com/bridgecrewio/checkov/pull/3628)
- **terraform:** add CKV NCP rule about vpc volume encryption. - [#3629](https://github.com/bridgecrewio/checkov/pull/3629)
- **terraform:** add CKV NCP rules about Network ACL. - [#3630](https://github.com/bridgecrewio/checkov/pull/3630)
- **terraform:** Create checks for aws managed admin policy - [#3741](https://github.com/bridgecrewio/checkov/pull/3741)

### Bug Fix

- **terraform:** local_authentication_disabled - cosmodb check to look at SQL Api only CKV_AZURE_140 - [#3648](https://github.com/bridgecrewio/checkov/pull/3648)

## [2.1.294](https://github.com/bridgecrewio/checkov/compare/2.1.290...2.1.294) - 2022-10-25

### Feature

- **kubernetes:** Create label selector edge builder - [#3715](https://github.com/bridgecrewio/checkov/pull/3715)
- **terraform:** add CKV NCP rules about access control group Inbound rule. - [#3627](https://github.com/bridgecrewio/checkov/pull/3627)
- **terraform:** add versioned kubernetes resources to terraform kubernetes checks (5/5) - [#3657](https://github.com/bridgecrewio/checkov/pull/3657)

### Bug Fix

- **general:** skip scanning VCS configuration if only files are passed in - [#3729](https://github.com/bridgecrewio/checkov/pull/3729)

## [2.1.290](https://github.com/bridgecrewio/checkov/compare/2.1.288...2.1.290) - 2022-10-24

### Feature

- **circleci:** CircleCI Image Reference using Mixin class - [#3707](https://github.com/bridgecrewio/checkov/pull/3707)

### Bug Fix

- **kubernetes:** fix in CPURequests check - [#3727](https://github.com/bridgecrewio/checkov/pull/3727)

## [2.1.288](https://github.com/bridgecrewio/checkov/compare/2.1.286...2.1.288) - 2022-10-24

### Bug Fix

- **github:** fix GITHUB_OUTPUT and GITHUB_ENV issues of checkov-action - [#3726](https://github.com/bridgecrewio/checkov/pull/3726)
- **gitlab:** Modify gitlab ci resource id - [#3706](https://github.com/bridgecrewio/checkov/pull/3706)

## [2.1.286](https://github.com/bridgecrewio/checkov/compare/2.1.282...2.1.286) - 2022-10-23

### Feature

- **graph:** equals/not_equals_ignore_case operators (solvers) - [#3698](https://github.com/bridgecrewio/checkov/pull/3698)

### Bug Fix

- **github:** Fix GHA off value error resulting in checkov hanging - [#3713](https://github.com/bridgecrewio/checkov/pull/3713)
- **gitlab:** vcs gitlab groups retrieval - [#3716](https://github.com/bridgecrewio/checkov/pull/3716)
- **kubernetes:** fix in ServiceAccountTokens check - [#3717](https://github.com/bridgecrewio/checkov/pull/3717)
- **terraform:** Add debug logs to yaml parsing logic - [#3718](https://github.com/bridgecrewio/checkov/pull/3718)

## [2.1.282](https://github.com/bridgecrewio/checkov/compare/2.1.277...2.1.282) - 2022-10-20

### Bug Fix

- **general:** Custom Policies integration must run before Suppresion integration - [#3701](https://github.com/bridgecrewio/checkov/pull/3701)
- **terraform:** Add or condition for TLS 1.3 policy, supporting CKV_AWS_103 - [#3700](https://github.com/bridgecrewio/checkov/pull/3700)
- **terraform:** Fix TF AbsGoogleComputeFirewallUnrestrictedIngress check - [#3704](https://github.com/bridgecrewio/checkov/pull/3704)

## [2.1.277](https://github.com/bridgecrewio/checkov/compare/2.1.273...2.1.277) - 2022-10-19

### Feature

- **terraform:** add CKV NCP rules about access control group outbound rule. - [#3624](https://github.com/bridgecrewio/checkov/pull/3624)
- **terraform:** add versioned kubernetes resources to terraform kubernetes checks (2/5) - [#3654](https://github.com/bridgecrewio/checkov/pull/3654)
- **terraform:** add versioned kubernetes resources to terraform kubernetes checks (3/5) - [#3655](https://github.com/bridgecrewio/checkov/pull/3655)
- **terraform:** add versioned kubernetes resources to terraform kubernetes checks (4/5) - [#3656](https://github.com/bridgecrewio/checkov/pull/3656)

### Bug Fix

- **cloudformation:** Fix ALBListenerTLS12 check - [#3697](https://github.com/bridgecrewio/checkov/pull/3697)
- **helm:** undo file_abs_path manipulation for helm files - [#3692](https://github.com/bridgecrewio/checkov/pull/3692)
- **kubernetes:** Couple of fixes in Checks - [#3686](https://github.com/bridgecrewio/checkov/pull/3686)
- **terraform:** Fix CloudArmorWAFACLCVE202144228 check - [#3696](https://github.com/bridgecrewio/checkov/pull/3696)

## [2.1.273](https://github.com/bridgecrewio/checkov/compare/2.1.270...2.1.273) - 2022-10-18

### Feature

- **kustomize:** stop kustomize run, if there is nothing to process - [#3681](https://github.com/bridgecrewio/checkov/pull/3681)
- **sca:** Enable multiple image referencer framework results in the same scan - [#3652](https://github.com/bridgecrewio/checkov/pull/3652)
- **terraform:** add versioned kubernetes resources to terraform kubernetes checks (1/5) - [#3653](https://github.com/bridgecrewio/checkov/pull/3653)

### Documentation

- **general:** Fix broken links - [#3685](https://github.com/bridgecrewio/checkov/pull/3685)

## [2.1.270](https://github.com/bridgecrewio/checkov/compare/2.1.269...2.1.270) - 2022-10-13

### Bug Fix

- **terraform:** Outdated check for google_container_cluster binary authorization - [#3612](https://github.com/bridgecrewio/checkov/pull/3612)

## [2.1.269](https://github.com/bridgecrewio/checkov/compare/2.1.266...2.1.269) - 2022-10-12

### Feature

- **terraform:** Added new Terraform-AWS python IAMUserNotUsedForAccess(CKV_AWS_273) policy - [#3574](https://github.com/bridgecrewio/checkov/pull/3574)

### Bug Fix

- **argo:** only scan Argo Workflows files - [#3644](https://github.com/bridgecrewio/checkov/pull/3644)
- **kubernetes:** minor fix for getting entity type from template - [#3645](https://github.com/bridgecrewio/checkov/pull/3645)
- **kustomize:** add --client=true to kubectl version command, to prevent checkov waiting for timeout if cluster is unreachable - [#3641](https://github.com/bridgecrewio/checkov/pull/3641)
- **terraform:** update CKV_AWS_213 to also cover AWS predefined security policies - [#3615](https://github.com/bridgecrewio/checkov/pull/3615)

## [2.1.266](https://github.com/bridgecrewio/checkov/compare/2.1.258...2.1.266) - 2022-10-11

### Feature

- **general:** add Azure Pipelines framework - [#3579](https://github.com/bridgecrewio/checkov/pull/3579)

### Bug Fix

- **dockerfile:** handle quoted absolute path in CKV_DOCKER_10  - [#3626](https://github.com/bridgecrewio/checkov/pull/3626)
- **kubernetes:** handled missing field secretKeyRef in template - [#3639](https://github.com/bridgecrewio/checkov/pull/3639)
- **kubernetes:** handled missing key in k8s templates - [#3640](https://github.com/bridgecrewio/checkov/pull/3640)
- **terraform:** extend CKV2_AWS_15 to support aws_lb_target_group - [#3617](https://github.com/bridgecrewio/checkov/pull/3617)
- **terraform:** handle unexpected value for enabled_cloudwatch_logs_exports - [#3638](https://github.com/bridgecrewio/checkov/pull/3638)

## [2.1.258](https://github.com/bridgecrewio/checkov/compare/2.1.255...2.1.258) - 2022-10-06

### Feature

- **dockerfile:** add Image Referencer for Dockerfile - [#3571](https://github.com/bridgecrewio/checkov/pull/3571)

### Bug Fix

- **cloudformation:** Fixed unexpected null properties for LaunchConfigurationEBSEncryption - [#3620](https://github.com/bridgecrewio/checkov/pull/3620)

## [2.1.255](https://github.com/bridgecrewio/checkov/compare/2.1.254...2.1.255) - 2022-10-04

### Feature

- **general:** allow file destination mapping via output-file-path flag - [#3593](https://github.com/bridgecrewio/checkov/pull/3593)

## [2.1.254](https://github.com/bridgecrewio/checkov/compare/2.1.247...2.1.254) - 2022-10-03

### Feature

- **github:** GHA Image Referencer using IR Mixin class - [#3583](https://github.com/bridgecrewio/checkov/pull/3583)
- **graph:** add support for guideline field to custom graph checks - [#3600](https://github.com/bridgecrewio/checkov/pull/3600)
- **sca:** Add root path references to shorten file paths in Image Referencer results - [#3609](https://github.com/bridgecrewio/checkov/pull/3609)
- **sca:** support Image referencer in CLI - [#3601](https://github.com/bridgecrewio/checkov/pull/3601)

### Bug Fix

- **github:** bug fixes in CKV_GITHUB_6, CKV_GITHUB_7, CKV_GITHUB_9 - [#3605](https://github.com/bridgecrewio/checkov/pull/3605)
- **github:** Fix resource id and file path for GHA IR - [#3610](https://github.com/bridgecrewio/checkov/pull/3610)
- **terraform:** extend check for google cloud functions 2nd generation - [#3607](https://github.com/bridgecrewio/checkov/pull/3607)
- **terraform:** fix port is bool ingress rule - [#3606](https://github.com/bridgecrewio/checkov/pull/3606)

## [2.1.247](https://github.com/bridgecrewio/checkov/compare/2.1.242...2.1.247) - 2022-10-02

### Feature

- **general:** added cli argument for extra resources in report - [#3588](https://github.com/bridgecrewio/checkov/pull/3588)
- **serverless:** added extra resources for serverless and dockerfile - [#3576](https://github.com/bridgecrewio/checkov/pull/3576)
- **terraform:** add CKV_NCP_1 about lb target group health check, CKV_NCP_2 about access control group description - [#3569](https://github.com/bridgecrewio/checkov/pull/3569)

### Bug Fix

- **cloudformation:** fix lc ebs encryption - [#3598](https://github.com/bridgecrewio/checkov/pull/3598)
- **github:** changed the schema to accept no description for org - [#3589](https://github.com/bridgecrewio/checkov/pull/3589)
- **secrets:** Skip secrets from files encoded with special codecs - [#3597](https://github.com/bridgecrewio/checkov/pull/3597)

## [2.1.242](https://github.com/bridgecrewio/checkov/compare/2.1.236...2.1.242) - 2022-09-29

### Breaking Change

- **general:** switch from black-list to block-list  - [#3581](https://github.com/bridgecrewio/checkov/pull/3581)

### Feature

- **kubernetes:** added resources mappings for roles objects - [#3582](https://github.com/bridgecrewio/checkov/pull/3582)

### Bug Fix

- **github:** fix variables initialization - [#3585](https://github.com/bridgecrewio/checkov/pull/3585)
- **kubernetes:** Handle templates without name for PeerClientCertAuthTrue check - [#3577](https://github.com/bridgecrewio/checkov/pull/3577)
- **openapi:** fix openapi schema bug - [#3587](https://github.com/bridgecrewio/checkov/pull/3587)
- **sca:** fix CycloneDX output for Docker images - [#3586](https://github.com/bridgecrewio/checkov/pull/3586)
- **secrets:** change entropy limit in Combinator plugin - [#3575](https://github.com/bridgecrewio/checkov/pull/3575)
- **terraform:** fix external modules ids in graph report - [#3584](https://github.com/bridgecrewio/checkov/pull/3584)
- **terraform:** Handle malformed database_flags for GCP DB checks - [#3578](https://github.com/bridgecrewio/checkov/pull/3578)

## [2.1.236](https://github.com/bridgecrewio/checkov/compare/2.1.229...2.1.236) - 2022-09-28

### Feature

- **general:** Add enforcement rules to entrypoint.sh - [#3573](https://github.com/bridgecrewio/checkov/pull/3573)
- **openapi:** add CKV_OPENAPI_7 to ensure http is not used in path definition - [#3547](https://github.com/bridgecrewio/checkov/pull/3547)
- **sca:** add Image Referencer for Kubernetes, Helm and Kustomize - [#3505](https://github.com/bridgecrewio/checkov/pull/3505)
- **terraform:** add CKV_AWS_272 to validate Lambda function code-signing - [#3556](https://github.com/bridgecrewio/checkov/pull/3556)
- **terraform:** add new gcp postgresql checks - [#3532](https://github.com/bridgecrewio/checkov/pull/3532)
- **terraform:** allow resources without values in TF plan - [#3563](https://github.com/bridgecrewio/checkov/pull/3563)

## [2.1.229](https://github.com/bridgecrewio/checkov/compare/2.1.228...2.1.229) - 2022-09-27

### Bug Fix

- **kubernetes:** [CKV_K8S_68] Remove unnecessary condition check from ApiServerAnonymousAuth.py - [#3543](https://github.com/bridgecrewio/checkov/pull/3543)

## [2.1.228](https://github.com/bridgecrewio/checkov/compare/2.1.227...2.1.228) - 2022-09-26

### Bug Fix

- **general:** use current branch name instead of master for the checkov-action  - [#3568](https://github.com/bridgecrewio/checkov/pull/3568)

## [2.1.227](https://github.com/bridgecrewio/checkov/compare/2.1.226...2.1.227) - 2022-09-23

### Documentation

- **general:** Multi skip docs - [#3561](https://github.com/bridgecrewio/checkov/pull/3561)

## [2.1.226](https://github.com/bridgecrewio/checkov/compare/2.1.223...2.1.226) - 2022-09-22

### Feature

- **gitlab:** GitlabCI ImageReferencer - [#3544](https://github.com/bridgecrewio/checkov/pull/3544)

### Bug Fix

- **secrets:** Bump bc-detect-secrets - [#3555](https://github.com/bridgecrewio/checkov/pull/3555)
- **terraform:** fix check CKV2_AZURE_8 - [#3554](https://github.com/bridgecrewio/checkov/pull/3554)

### Documentation

- **general:** Fix TOC rendering issue on checkov.io - [#3551](https://github.com/bridgecrewio/checkov/pull/3551)

## [2.1.223](https://github.com/bridgecrewio/checkov/compare/2.1.219...2.1.223) - 2022-09-21

### Feature

- **general:** Improve ComplexSolver run time - [#3548](https://github.com/bridgecrewio/checkov/pull/3548)
- **kubernetes:** create complex k8s vertices - [#3549](https://github.com/bridgecrewio/checkov/pull/3549)

### Bug Fix

- **general:** only add `helpUri` to SARIF if it is non-empty - [#3542](https://github.com/bridgecrewio/checkov/pull/3542)
- **kubernetes:** [CKV_K8S_140] Update ApiServerTlsCertAndKey.py to check RHS values  - [#3506](https://github.com/bridgecrewio/checkov/pull/3506)
- **kubernetes:** [CKV_K8S_90] Remove unnecessary condition check from ApiServerProfiling.py - [#3541](https://github.com/bridgecrewio/checkov/pull/3541)

## [2.1.219](https://github.com/bridgecrewio/checkov/compare/2.1.214...2.1.219) - 2022-09-20

### Feature

- **cloudformation:** add CKV_AWS_197 for CFN - [#3536](https://github.com/bridgecrewio/checkov/pull/3536)
- **sca:** Split `PRESENT_CACHED_RESULTS` env var to 2 feature flag like vars - [#3518](https://github.com/bridgecrewio/checkov/pull/3518)

### Bug Fix

- **general:** handle fixes for cloned OOTB policies - [#3535](https://github.com/bridgecrewio/checkov/pull/3535)
- **helm:** fix helm signal abort handler - [#3539](https://github.com/bridgecrewio/checkov/pull/3539)
- **terraform:** APIGatewayAuthorization check missing authorization - [#3545](https://github.com/bridgecrewio/checkov/pull/3545)
- **terraform:** fix tfvars rendering - [#3533](https://github.com/bridgecrewio/checkov/pull/3533)

## [2.1.214](https://github.com/bridgecrewio/checkov/compare/2.1.212...2.1.214) - 2022-09-19

### Feature

- **general:** leverage SARIF helpUri for guideline and SCA link - [#3492](https://github.com/bridgecrewio/checkov/pull/3492)
- **github:** Improving GHA schema validation - [#3513](https://github.com/bridgecrewio/checkov/pull/3513)
- **kubernetes:** added base class K8SEdgeBuilder - [#3530](https://github.com/bridgecrewio/checkov/pull/3530)
- **terraform:** GCP Cloud functions should not be public - [#3477](https://github.com/bridgecrewio/checkov/pull/3477)

### Bug Fix

- **github:** add missing schema files to distribution package - [#3537](https://github.com/bridgecrewio/checkov/pull/3537)
- **sca:** changes on cve suppressions to match package and image scan - [#3502](https://github.com/bridgecrewio/checkov/pull/3502)
- **sca:** send exception log when exceeded retries - [#3534](https://github.com/bridgecrewio/checkov/pull/3534)
- **terraform:**  make test case insensitive for CKV_ALI_35,CKV_ALI_36,CKV_ALI_37 - [#3507](https://github.com/bridgecrewio/checkov/pull/3507)
- **terraform:** do not evaluate OCI policy statements - [#3411](https://github.com/bridgecrewio/checkov/pull/3411)

## [2.1.212](https://github.com/bridgecrewio/checkov/compare/2.1.210...2.1.212) - 2022-09-18

### Bug Fix

- **helm:** helm add timeout to dependencies command - [#3525](https://github.com/bridgecrewio/checkov/pull/3525)
- **helm:** Helm fix logs - [#3524](https://github.com/bridgecrewio/checkov/pull/3524)

## [2.1.210](https://github.com/bridgecrewio/checkov/compare/2.1.207...2.1.210) - 2022-09-15

### Feature

- **sca:** add Image Referencer for CloudFormation - [#3501](https://github.com/bridgecrewio/checkov/pull/3501)

### Bug Fix

- **helm:** add try catch to helm cmd run - [#3508](https://github.com/bridgecrewio/checkov/pull/3508)

### Platform

- **general:** upload run metadata to S3 - [#3461](https://github.com/bridgecrewio/checkov/pull/3461)

## [2.1.207](https://github.com/bridgecrewio/checkov/compare/2.1.205...2.1.207) - 2022-09-14

### Feature

- **general:** fix format of cli command reference table - [#3504](https://github.com/bridgecrewio/checkov/pull/3504)

### Bug Fix

- **sca:** skip old CVE suppressions (without 'accountIds') - [#3503](https://github.com/bridgecrewio/checkov/pull/3503)

## [2.1.205](https://github.com/bridgecrewio/checkov/compare/2.1.204...2.1.205) - 2022-09-13

### Feature

- **general:** add flag for summary position - [#3497](https://github.com/bridgecrewio/checkov/pull/3497)

## [2.1.204](https://github.com/bridgecrewio/checkov/compare/2.1.201...2.1.204) - 2022-09-12

### Feature

- **sca:** licenses suppressions by type - [#3491](https://github.com/bridgecrewio/checkov/pull/3491)

### Bug Fix

- **arm:** unexpected data type in ACRAnonymousPullDisabled - [#3496](https://github.com/bridgecrewio/checkov/pull/3496)
- **general:** remove duplicated reports - [#3495](https://github.com/bridgecrewio/checkov/pull/3495)

## [2.1.201](https://github.com/bridgecrewio/checkov/compare/2.1.196...2.1.201) - 2022-09-08

### Feature

- **general:** `intersects/not_intersects` operators (solvers) - [#3482](https://github.com/bridgecrewio/checkov/pull/3482)

### Bug Fix

- **gha:** Gracefully handle bad GHA job definitions - [#3489](https://github.com/bridgecrewio/checkov/pull/3489)
- **sca:** do not skip the scan if BC_LIC is used with --check - [#3488](https://github.com/bridgecrewio/checkov/pull/3488)

## [2.1.196](https://github.com/bridgecrewio/checkov/compare/2.1.193...2.1.196) - 2022-09-07

### Bug Fix

- **kubernetes:** Validate k8s spec type - [#3483](https://github.com/bridgecrewio/checkov/pull/3483)
- **terraform:** removed duplicate check CKV_ALI_34 - [#3467](https://github.com/bridgecrewio/checkov/pull/3467)

## [2.1.193](https://github.com/bridgecrewio/checkov/compare/2.1.188...2.1.193) - 2022-09-06

### Bug Fix

- **cloudformation:** fix bug in cfn parser - [#3473](https://github.com/bridgecrewio/checkov/pull/3473)

### Platform

- **sca:** Add images data to image_cached_results for ImageReferencer scan - [#3468](https://github.com/bridgecrewio/checkov/pull/3468)
- **secrets:** modify checkov secrets scanner to scan all files based on ff - [#3474](https://github.com/bridgecrewio/checkov/pull/3474)

## [2.1.188](https://github.com/bridgecrewio/checkov/compare/2.1.184...2.1.188) - 2022-09-05

## Feature

- **cloudformation:** json parser support triple quote string - [#3463](https://github.com/bridgecrewio/checkov/pull/3463)

## Bug Fix

- **terraform:** gcp postgresql default values - [#3457](https://github.com/bridgecrewio/checkov/pull/3457)

## [2.1.184](https://github.com/bridgecrewio/checkov/compare/2.1.182...2.1.184) - 2022-09-04

## Platform

- **general:** trim API urls - [#3460](https://github.com/bridgecrewio/checkov/pull/3460)

## Documentation

- **general:** adjust example for custom check with guideline - [#3459](https://github.com/bridgecrewio/checkov/pull/3459)

## [2.1.182](https://github.com/bridgecrewio/checkov/compare/2.1.179...2.1.182) - 2022-09-02

## Feature

- **sca:** Added fix details to junitxml - [#3456](https://github.com/bridgecrewio/checkov/pull/3456)
- **terraform:** Added 5 python (CKV_AWS_267-271) and 2 yaml (CKV2_AWS_38-39) policies. - [#3438](https://github.com/bridgecrewio/checkov/pull/3438)

## [2.1.179](https://github.com/bridgecrewio/checkov/compare/2.1.176...2.1.179) - 2022-09-01

## Bug Fix

- **graph:** cache jsonpath attributes parser results - [#3451](https://github.com/bridgecrewio/checkov/pull/3451)

## Platform

- **general:** revert dropping checks metadata for empty reports - [#3453](https://github.com/bridgecrewio/checkov/pull/3453)
