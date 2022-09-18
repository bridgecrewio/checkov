# CHANGELOG

## [Unreleased](https://github.com/bridgecrewio/checkov/compare/2.1.212...HEAD)

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
