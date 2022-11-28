# CHANGELOG

## [Unreleased](https://github.com/bridgecrewio/checkov/compare/2.2.99...HEAD)

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
