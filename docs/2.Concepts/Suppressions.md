---
layout: default
published: true
title: Suppressions
order: 5
---

# Suppressions

Like any static-analysis tool it is limited by its analysis scope. 
For example, if a resource is managed manually, or using subsequent configuration management tooling, 
a suppression can be inserted as a simple code annotation.

## Suppression comment format

To skip a check on a given Terraform definition block or CloudFormation resource, apply the following comment pattern inside it's scope:

`checkov:skip=<check_id>:<suppression_comment>`

* `<check_id>` is one of the [available check scanners](../3.Scans/resource-scans.md)
* `<suppression_comment>` is an optional suppression reason to be included in the output

### Example
The following comment skip the `CKV_AWS_20` check on the resource identified by `foo-bucket`, where the scan checks if an AWS S3 bucket is private.
In the example, the bucket is configured with a public read access; Adding the suppress comment would skip the appropriate check instead of the check to fail.
```hcl-terraform
resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
    #checkov:skip=CKV_AWS_20:The bucket is a public static content host
  bucket        = local.bucket_name
  force_destroy = true
  acl           = "public-read"
}
```

The output would now contain a ``SKIPPED`` check result entry:

```bash
...
...
Check: "S3 Bucket has an ACL defined which allows public access."
	SKIPPED for resource: aws_s3_bucket.foo-bucket
	Suppress comment: The bucket is a public static content host
	File: /example_skip_acl.tf:1-25
	
...
```

### Kubernetes Example
To suppress checks in Kubernetes manifests, annotations are used with the following format:
`checkov.io/skip#: <check_id>=<suppression_comment>`

```bash
apiVersion: v1
kind: Pod
metadata:
  name: mypod
  annotations:
    checkov.io/skip1: CKV_K8S_20=I don't care about Privilege Escalation :-O
    checkov.io/skip2: CKV_K8S_14
    checkov.io/skip3: CKV_K8S_11=I have not set CPU limits as I want BestEffort QoS
spec:
  containers:
...
```

# Global skip
If you'd like to whitelist or blacklist a check_id from being executed, use the `--check`(whitelist) or `--skip-check` flags