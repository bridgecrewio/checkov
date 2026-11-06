---
layout: default
published: true
title: Pulumi
nav_order: 20
---

# Pulumi Scanning

Checkov scans the JSON output of a Pulumi preview or a stack export with the existing Terraform policies.
Pulumi's `aws`, `gcp` and `azure` providers are bridged from the Terraform providers, so their resources are
translated to the equivalent Terraform resources, ex. `aws:s3/bucket:Bucket` to `aws_s3_bucket`, before the
Terraform policies, including graph policies and custom policies, are evaluated.

Like a Terraform plan, a Pulumi preview can contain secrets, which are injected dynamically.
It is advised to run the scan in a secure CI/CD pipeline setting.

## Example

```shell
pulumi preview --json > preview.json

checkov -f preview.json --framework pulumi
```

The output would look like:

```
pulumi scan results:
Passed checks: 0, Failed checks: 1, Skipped checks: 0
Check: CKV_AWS_24: "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22"
	FAILED for resource: aws_security_group.openSg
	File: /preview.json:260-278
		261 |                 "inputs": {
		262 |                     "__defaults": [],
		263 |                     "description": "open ssh",
		264 |                     "ingress": [
		265 |                         {
		266 |                             "__defaults": [],
		267 |                             "cidrBlocks": [
		268 |                                 "0.0.0.0/0"
		269 |                             ],
```

Resources are reported with their Terraform type and Pulumi logical name, ex. `aws_security_group.openSg`.
The stack configuration of the providers, ex. `aws:region`, is scanned with the Terraform provider policies.

## Supported inputs

| Command                                                                       | Notes                                                                    |
|-------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| `pulumi preview --json`                                                       | Recommended                                                              |
| `pulumi stack export`                                                         | Scans the deployed resources of a stack                                  |
| `PULUMI_ENABLE_STREAMING_JSON_PREVIEW=true pulumi preview --json > preview.jsonl` | Doesn't contain resource dependencies, graph policies, which need connected resources, can fail |

Files with the extensions `.json`, `.jsonl` and `.ndjson` are scanned. Saving the streamed event log as `.jsonl` avoids
parsing errors of the other JSON based frameworks, when scanning a directory with `--framework all`.

## Supported providers

- `aws`
- `gcp`
- `azure`

Resources of other providers, ex. `azure-native` or `kubernetes`, and component resources are skipped.

Values, which are only known after the deployment, are omitted, the same as in a Terraform plan.
Dependencies between resources are used to connect them, ex. an `aws:s3:BucketPublicAccessBlock` with its
`aws:s3:Bucket`, so graph policies work like for a Terraform configuration.
