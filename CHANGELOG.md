# CHANGELOG

## [Unreleased](https://github.com/bridgecrewio/checkov/compare/2.1.277...HEAD)

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
