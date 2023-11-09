---
layout: default
published: true
title: GitLab SAST
nav_order: 20
---

# GitLab SAST

GitLab SAST output adds the possibility to directly integrate with the Security tab and Merge Requests in GitLab.

A typical output looks like this
```json
{
  "schema": "https://gitlab.com/gitlab-org/security-products/security-report-schemas/-/raw/v15.0.4/dist/sast-report-format.json",
  "version": "15.0.4",
  "scan": {
    "start_time": "2023-01-23T22:45:33",
    "end_time": "2023-01-23T22:45:33",
    "analyzer": {
      "id": "checkov",
      "name": "Checkov",
      "url": "https://www.checkov.io/",
      "vendor": {
        "name": "Prisma Cloud"
      },
      "version": "2.2.281"
    },
    "scanner": {
      "id": "checkov",
      "name": "Checkov",
      "url": "https://www.checkov.io/",
      "vendor": {
        "name": "Prisma Cloud"
      },
      "version": "2.2.281"
    },
    "status": "success",
    "type": "sast"
  },
  "vulnerabilities": [
    {
      "id": "605d1ad8-da1e-4784-859a-199708846fee",
      "identifiers": [
        {
          "name": "CKV_AWS_18",
          "type": "checkov",
          "url": "https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_13-enable-logging",
          "value": "CKV_AWS_18"
        }
      ],
      "links": [
        {
          "url": "https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_13-enable-logging"
        }
      ],
      "location": {
        "file": "main.tf",
        "start_line": 1,
        "end_line": 8
      },
      "name": "Ensure the S3 bucket has access logging enabled",
      "description": "Further info can be found None",
      "severity": "Unknown",
      "solution": "Further info can be found None"
    },
    {
      "id": "1fe876c4-db57-4785-867e-ab1415250382",
      "identifiers": [
        {
          "name": "CKV2_AWS_6",
          "type": "checkov",
          "url": "https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-bucket-should-have-public-access-blocks-defaults-to-false-if-the-public-access-block-is-not-attached",
          "value": "CKV2_AWS_6"
        }
      ],
      "links": [
        {
          "url": "https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-bucket-should-have-public-access-blocks-defaults-to-false-if-the-public-access-block-is-not-attached"
        }
      ],
      "location": {
        "file": "main.tf",
        "start_line": 1,
        "end_line": 8
      },
      "name": "Ensure that S3 bucket has a Public Access block",
      "description": "Further info can be found None",
      "severity": "Unknown",
      "solution": "Further info can be found None"
    }
  ]
}
```

The output can be created via the output flag

```shell
checkov -d . -o gitlab_sast
```

## Structure

Further information on the different elements and attributes can be found [here](https://gitlab.com/gitlab-org/security-products/security-report-schemas/-/raw/v15.0.4/dist/sast-report-format.json).
