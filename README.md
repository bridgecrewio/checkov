# Checkov
![build status](https://github.com/bridgecrewio/terraform-static-analysis/workflows/build/badge.svg) ![code_coverage](coverage.svg)

Bridgecrew is a platform to programmatically author and govern cloud infrastructure policies.
When policies are defined as code, they become more maintainable, versionable, testable and collaborative.
Use bridgecrew static analysis to vet infrastructure as code modules.  

**Table of contents**
- [Getting started](#getting-started)
- [Beyond the horizon](#beyond-the-horizon)
- [Principles](#principles)
- [CLI](#cli)
- [Contributing](#contributing)
- []
- [Resource scans](#resource-scans)

## Getting started
Please visit the Checkov documentation for help with [installing checkov**TODO](), getting a [quick_start**TODO](), or a more complete [tutorial**TODO]().

Documentation of GitHub master (latest development branch): [ReadTheDocs Documentation**TODO]()
 
## Beyond the Horizon
Checkov **is not** runtime protection solution. It does not relay on running infrastucture at AWS/GCP/Azure. 
Checkov is not in the [Cloudcustodian](https://cloudcustodian.io/) or [StreamAlert](https://github.com/airbnb/streamalert) space.

It is more comparable to [Terrascan](https://github.com/cesar-rodriguez/terrascan) or [tfsec](https://github.com/liamg/tfsec). 

## Principles
- **Security-oriented**: Checkov scans are defines as code (Python), allowing security and devops engineers to write content easily. 
- **Extensible**: Easily define your own scans, suppressions and extend the library so that it fits the policy granularity that suits your environment.
- **Rich-data** Preform resource scans or complex dependency graph scans using the powerful dependency graph query package.

## CLI
###********TODO: List checks
###********TODO: Run Checks
###********TODO: Suppress Check
###********TODO: Output formats

## Contributing
Want to help build Checkov? Checkout our [contributing documentation ***TODO](***TODO)

## Who Maintains Checkov?
Checkov is the work of the [community](graphs/contributors), 
but the core committers/maintainers are responsible for reviewing and merging PRs as well as steering 
conversation around new feature requests. If you would like to become a maintainer, please review the Chekov 
committer requirements.


## Resource scans

|    | Resource                        | Policy                                                                              |
|----|---------------------------------|-------------------------------------------------------------------------------------|
|  0 | aws_s3_bucket                   | Ensure all data stored in the S3 bucket is securely encrypted at rest               |
|  1 | aws_s3_bucket                   | Ensure the S3 bucket has access logging enabled                                     |
|  2 | aws_s3_bucket                   | Ensure all data stored in the S3 bucket is securely encrypted at rest               |
|  3 | aws_s3_bucket                   | S3 Bucket has an ACL defined which allows public access.                            |
|  4 | aws_iam_account_password_policy | Ensure IAM password policy requires at least one lowercase letter                   |
|  5 | aws_iam_account_password_policy | Ensure IAM password policy requires at least one uppercase letter                   |
|  6 | aws_iam_account_password_policy | Ensure IAM password policy expires passwords within 90 days or less                 |
|  7 | aws_iam_account_password_policy | Ensure IAM password policy prevents password reuse                                  |
|  8 | aws_iam_account_password_policy | Ensure IAM password policy requires at least one number                             |
|  9 | aws_iam_account_password_policy | Ensure IAM password policy requires minimum length of 14 or greater                 |
| 10 | aws_iam_account_password_policy | Ensure IAM password policy requires at least one symbol                             |
| 11 | aws_elasticsearch_domain        | Ensure all data stored in the Elasticsearch is securely encrypted at rest           |
| 12 | aws_elasticsearch_domain        | Ensure all Elasticsearch has node-to-node encryption enabled                        |
| 13 | aws_security_group              | Ensure no security groups allow ingress from 0.0.0.0:0 to port 22                   |
| 14 | aws_security_group              | Ensure no security groups rule has a description                                    |
| 15 | aws_security_group              | Ensure no security groups allow ingress from 0.0.0.0:0 to port 3389                 |
| 16 | aws_sqs_queue                   | Ensure all data stored in the SQS queue  is encrypted                               |
| 17 | aws_sagemaker_notebook_instance | Ensure all data stored in the Sagemaker is securely encrypted at rest               |
| 18 | aws_security_group_rule         | Ensure no security groups rule has a description                                    |
| 19 | aws_db_security_group           | Ensure no security groups rule has a description                                    |
| 20 | aws_elasticache_security_group  | Ensure no security groups rule has a description                                    |
| 21 | aws_redshift_security_group     | Ensure no security groups rule has a description                                    |
| 22 | aws_db_instance                 | Ensure all data stored in the RDS bucket is not public accessible                   |
| 23 | aws_db_instance                 | Ensure all data stored in the RDS bucket is securely encrypted at rest              |
| 24 | aws_rds_cluster_instance        | Ensure all data stored in the RDS bucket is not public accessible                   |
| 25 | aws_alb_listener                | Ensure ALB protocol is HTTPS                                                        |
| 26 | aws_lb_listener                 | Ensure ALB protocol is HTTPS                                                        |
| 27 | aws_sns_topic                   | Ensure all data stored in the SNS topic is encrypted                                |
| 28 | aws_ebs_volume                  | Ensure all data stored in the EBS is securely encrypted                             |
| 29 | aws_iam_policy_document         | Ensure IAM policies that allow full "*-*" administrative privileges are not created |
| 30 | aws_kms_key                     | Ensure rotation for customer created CMKs is enabled                                |
| 31 | aws_launch_configuration        | Ensure all data stored in the Launch configuration EBS is securely encrypted        |
| 32 | aws_instance                    | Ensure all data stored in the Launch configuration EBS is securely encrypted        |
| 33 | aws_ebs_snapshot                | Ensure all data stored in the EBS Snapshot is securely encrypted                    |
| 34 | google_storage_bucket           | Ensure Google storage bucket have encryption enabled                                |
| 35 | google_compute_firewall         | Ensure Google compute firewall ingress does not allow unrestricted rdp access       |
| 36 | google_compute_firewall         | Ensure Google compute firewall ingress does not allow unrestricted ssh access       |
| 37 | google_compute_ssl_policy       | Ensure Google SSL policy minimal TLS version is TLS_1_2                             |
| 38 | azurerm_managed_disk            | Ensure Azure managed disk have encryption enabled                                   |
| 39 | azurerm_virtual_machine         | Ensure Azure Instance does not use basic authentication(Use SSH Key Instead)        |
| 40 | azurerm_storage_account         | Ensure that 'Secure transfer required' is set to 'Enabled'                          |
