---
layout: default
published: true
title: Compliance Frameworks Guide
nav_order: 8
---

Checkov supports multiple compliance frameworks to help you meet regulatory requirements and industry standards. This guide covers how to use these frameworks effectively.

## Supported Compliance Frameworks

Checkov currently supports the following compliance frameworks:

| Framework | Description | Coverage |
|-----------|-------------|----------|
| **CIS Benchmarks** | Center for Internet Security standards | AWS, Azure, GCP, Kubernetes |
| **SOC 2** | Service Organization Control 2 | Cloud environments |
| **NIST** | National Institute of Standards and Technology | Partial coverage |
| **ISO 27001** | Information security standard | Partial coverage |
| **PCI DSS** | Payment Card Industry Data Security Standard | Cloud resources |

## Running Compliance Framework Scans

### Basic Usage

To scan your IaC against a specific compliance framework:

```shell
# Scan using CIS AWS Foundations Benchmark
checkov --directory ./terraform --framework terraform --check CKV_AWS*

# Scan with compliance-specific checks only
checkov -d . --run-all-external-checks
```

### Using Built-in Policy Sets

```shell
# Example: Run all AWS-related checks
checkov -d . --framework terraform --check CKV_AWS_*

# Example: Run Kubernetes CIS checks  
checkov -d . --framework kubernetes --check CKV_K8S_*
```

## Understanding Compliance Results

### Output Format

Checkov provides detailed output showing:
- **Check ID**: Unique identifier for each policy
- **Description**: What the check validates
- **Severity**: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
- **Guideline**: Link to detailed documentation

Example output:
```
Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
	FAILED for resource: aws_s3_bucket.data
	File: /main.tf:15-28
	Severity: MEDIUM
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-13-enable-logging
```

### Filtering by Severity

```shell
# Show only HIGH and CRITICAL findings
checkov -d . --severity HIGH,CRITICAL

# Skip informational findings
checkov -d . --skip-check CKV_AWS_999
```

## Best Practices for Compliance

### 1. Integrate Early in CI/CD

Add Checkov to your pipeline to catch violations before deployment:

```yaml
# .github/workflows/checkov.yml
name: Compliance Check
on: [pull_request]
jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform
```

### 2. Baseline Your Current State

```shell
# Create a baseline of current findings
checkov -d . --create-baseline --baseline-output-path baseline.json

# Use baseline to track new issues only
checkov -d . --baseline baseline.json
```

### 3. Customize for Your Environment

Not all checks apply to every environment. Use skip comments for legitimate exceptions:

```hcl
#checkov:skip=CKV_AWS_18:Data bucket doesn't need access logging (internal data only)
resource "aws_s3_bucket" "data" {
  bucket = "my-internal-data-bucket"
}
```

## Framework-Specific Guidance

### CIS Benchmarks

The CIS Benchmarks are consensus-based security configuration guides:

- **CIS AWS Foundations**: 55+ checks for AWS infrastructure
- **CIS Azure Foundations**: 40+ checks for Azure resources  
- **CIS GCP Foundations**: 40+ checks for GCP resources
- **CIS Kubernetes**: 100+ checks for K8s clusters

```shell
# Focus on CIS Level 1 (practical, minimal impact)
checkov -d . --check CKV_AWS_1,CKV_AWS_2,CKV_AWS_3
```

### SOC 2

SOC 2 compliance focuses on five trust principles:

1. **Security**: Protection against unauthorized access
2. **Availability**: System availability monitoring
3. **Processing Integrity**: Data processing accuracy
4. **Confidentiality**: Data protection measures
5. **Privacy**: Personal information handling

```shell
# Run checks relevant to SOC 2
checkov -d . --check CKV_AWS_19,CKV_AWS_20,CKV_AWS_21
```

## China MLPS 2.0 Compliance (等保2.0)

Multi-Level Protection Scheme 2.0 (MLPS 2.0) is China's cybersecurity compliance framework that requires organizations to implement security measures based on the criticality of their information systems.

### MLPS 2.0 Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **Level 1** | Basic protection | General information systems |
| **Level 2** | Moderate protection | Systems affecting social order |
| **Level 3** | Strict protection | Critical infrastructure |
| **Level 4** | Strictest protection | National security systems |

### Using Checkov for MLPS 2.0

While Checkov doesn't have dedicated MLPS 2.0 policies yet, many existing checks map to MLPS requirements:

#### Access Control (访问控制)

```shell
# Authentication and authorization checks
checkov -d . --check CKV_AWS_1,CKV_AWS_23,CKV_AWS_40
```

| MLPS Requirement | Checkov Check | Description |
|------------------|---------------|-------------|
| Identity authentication | CKV_AWS_1 | Ensure IAM policies are attached to groups/roles |
| Access control | CKV_AWS_23 | Ensure AWS SES configuration set has TLS policy |
| Permission management | CKV_AWS_40 | Ensure IAM policies do not allow privilege escalation |

#### Data Security (数据安全)

```shell
# Encryption and data protection checks
checkov -d . --check CKV_AWS_16,CKV_AWS_17,CKV_AWS_19
```

| MLPS Requirement | Checkov Check | Description |
|------------------|---------------|-------------|
| Data encryption | CKV_AWS_16 | Ensure EBS volumes are encrypted |
| Key management | CKV_AWS_17 | Ensure RDS instances have encryption enabled |
| Data backup | CKV_AWS_19 | Ensure EBS snapshots are encrypted |

#### Logging and Monitoring (安全审计)

```shell
# Audit logging checks
checkov -d . --check CKV_AWS_18,CKV_AWS_21
```

| MLPS Requirement | Checkov Check | Description |
|------------------|---------------|-------------|
| Access logging | CKV_AWS_18 | Ensure S3 bucket access logging is enabled |
| CloudTrail | CKV_AWS_21 | Ensure CloudTrail is enabled in all regions |

### Example: MLPS Level 3 Baseline Scan

For organizations targeting MLPS Level 3 compliance, here's a recommended baseline scan:

```shell
#!/bin/bash
# mlps-level3-scan.sh
# Recommended checks for MLPS 2.0 Level 3 compliance baseline

checkov -d . \
  --check \
  CKV_AWS_1,CKV_AWS_16,CKV_AWS_17,CKV_AWS_18,CKV_AWS_19,\
  CKV_AWS_21,CKV_AWS_23,CKV_AWS_40,CKV_AWS_53,CKV_AWS_54,\
  CKV_AWS_55,CKV_AWS_56,CKV_AWS_57,CKV_AWS_58,CKV_AWS_59 \
  --output cli \
  --compact
```

### Creating MLPS-Focused Reports

Generate structured reports for compliance auditors:

```shell
# JSON report for automated compliance tracking
checkov -d . \
  --check CKV_AWS_1,CKV_AWS_16,CKV_AWS_17,CKV_AWS_18,CKV_AWS_19 \
  --output json \
  --output-file mlps-compliance-report.json

# SARIF for integration with compliance dashboards
checkov -d . \
  --check CKV_AWS_1,CKV_AWS_16,CKV_AWS_17,CKV_AWS_18,CKV_AWS_19 \
  --output sarif \
  --output-file mlps-results.sarif
```

### Contributing MLPS Policies

The Checkov community welcomes contributions for MLPS 2.0-specific checks! If you're working on MLPS compliance and have developed custom policies, consider contributing them:

1. Review the [Contributing Guide](https://github.com/bridgecrewio/checkov/blob/main/CONTRIBUTING.md)
2. Map your checks to specific MLPS 2.0 requirements
3. Submit a PR with clear documentation

### Resources for Chinese Compliance

- [MLPS 2.0 Official Standard (GB/T 22239-2019)](http://www.cac.gov.cn/)
- [Checkov Custom Policies Guide](https://www.checkov.io/3.Custom%20Policies/Getting%20Started.html)
- Community discussion: [MLPS 2.0 Support Issue #1234](https://github.com/bridgecrewio/checkov/issues) *(placeholder - actual issue number may vary)*

---

## Generating Compliance Reports

### JSON Output for Automation

```shell
checkov -d . --output json --output-file compliance-report.json
```

### JUnit XML for CI/CD Integration

```shell
checkov -d . --output junitxml --output-file junit-report.xml
```

### SARIF for GitHub Advanced Security

```shell
checkov -d . --output sarif --output-file results.sarif
```

## Tips for Teams

### Establish Clear Ownership

- Assign compliance champions per team
- Document accepted risk decisions
- Regular review of suppressed checks

### Progressive Enforcement

```shell
# Phase 1: Monitor only (soft fail)
checkov -d . --soft-fail

# Phase 2: Block on critical only
checkov -d . --severity CRITICAL

# Phase 3: Full enforcement
checkov -d .
```

### Regular Audit Cycles

Schedule periodic reviews:
- Monthly: Review new check additions
- Quarterly: Assess baseline updates
- Annually: Comprehensive compliance review

## Troubleshooting Common Issues

### Too Many Findings?

```shell
# Start with highest severity
checkov -d . --severity CRITICAL,HIGH

# Use baseline mode to track progress
checkov -d . --baseline baseline.json --output github_failed_only
```

### Custom Policies Needed?

```shell
# Reference custom policy directory
checkov -d . --external-checks-dir ./custom-checks/
```

---

*This guide is community-maintained. For official documentation, visit [docs.prismacloud.io](https://docs.prismacloud.io)*