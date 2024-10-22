---
layout: default
published: true
title: Hard and soft fail
nav_order: 4
---

# Hard and soft fail

You can fine tune exactly which cases cause the Checkov scan to return a pass or fail result. The exit code of the Checkov process will be `0` for a passing result and `1` for a failure result.

A result is passing if all checks are passed or skipped; otherwise, the result is a failure. However, you can use the `--soft-fail`, `--soft-fail-on`, and `--hard-fail-on` options to customize this.

A "soft failure" is a result in which Checkov finds and reports errors during the scan, but still returns an exit code of `0`. This differs from skipping or suppressing checks in that a skipped or suppressed check is not a failing check, and thus will not result in an error exit code.

## Argument details

### --soft-fail

Use the `--soft-fail` (`-s`) option to have Checkov always return a `0` exit code, regardless of scan results.

### --soft-fail-on

Use the `--soft-fail-on` option to pass one or more check IDs (including wildcards) and / or severity levels to specify which failed checks will result in a soft fail result. Any failed check that does not match a criteria in the soft-fail list will result in an error exit code (`1`).

For soft fails, a failed check *matches* the threshold if its severity is less than or equal to the soft fail severity. If you specify more than one severity for soft fail, then the highest severity will be used as the threshold.

### --hard-fail-on

Use the `--hard-fail-on` option to pass one or more check IDs and / or severity levels to specify which failed checks will result in an error result. If all failed checks do *not* match any criteria in the hard-fail list, then the result of the scan will be a soft fail (`0`).

For hard fails, a a failed check *matches* the threshold if its severity is greater than or equal to the hard fail severity. If you specify more than one severity for hard fail, then the lowest severity will be used as the threshold.

## Combining options

You can combine the use of the three flags described above. In this case, Checkov will evaluate each failed check, applying the following logic in order of precedence:

1. If the failed check matches a check ID (or wildcard) in the *hard fail* list, then the result is a hard failure.
2. If the failed check matches a check ID (or wildcard) in the *soft fail* list, then the result is a soft failure.
3. If the failed check's severity is equal to or greater than the severity in the *hard fail* list, then the result is a hard failure.
4. If the failed check's severity is equal to or less than the severity in the *soft fail* list, then the result is a soft failure.
6. If the failed check does not match a check ID, wildcard, or severity in either list, then the result is the value of the `--soft-fail` flag.

Using the logic above, if *any* failed check results hard failure, then the result of the run is a hard failure. If *all* failed checks result in a soft failure, then the result is a soft failure.

# Examples

Assume we have a scan with two failed results:

|Policy Id|Severity|
|---------|--------|
|CKV_123|LOW|
|CKV_789|HIGH|

The table below shows how different values of `--soft-fail`, `--soft-fail-on`, and `--hard-fail-on` will yield an exit code.

|Soft Fail|Soft Fail On|Hard Fail On|Scan Result|Comments|
|-|-|-|-|-|
|True | - | - |0 (soft fail)|All errors are soft fails|
|False|CKV_123|-|1 (hard fail)|Soft fail requires all failures to match a soft fail criteria|
|False|-|CKV_999|0|Every failed check did not match a hard fail criteria, so the result is implicitly soft fail|
|False|LOW,CKV_789|CKV_123|1|The explicit match of the hard fail criteria results in a hard fail|
|False|CKV_789|HIGH|1|CKV_789 explicitly matches a soft fail criteria, which overrides the hard fail. But CKV_123 is not in either list, so defaults to the value of `--soft-fail`, which is false|
|True|CKV_789|HIGH|0|CKV_789 explicitly matches a soft fail criteria, which overrides the hard fail. But CKV_123 is not in either list, so defaults to `--soft-fail`, which is true|

# Platform enforcement rules

Checkov can download [enforcement rules](https://docs.prismacloud.io/en/enterprise-edition/content-collections/application-security/risk-management/monitor-and-manage-code-build/enforcement) that you configure in the Prisma Cloud platform. This allows you to centralize the failure and check threshold configurations, instead of defining them in each pipeline.

To use enforcement rules, use the `--use-enforcement-rules` flag along with a platform API key.

Enforcement rules allow you to specify a hard-fail severity threshold equivalent to using the `--hard-fail-on <SEVERITY>` argument in Checkov. However, whereas this argument is global, the enforcement rules settings are more granular, for each major category of scanner that Checkov has (IaC, secrets, etc). So, for example, you can hard-fail any IaC scan on `MEDIUM` severity or higher, and hard-fail the SCA scan on `HIGH` severity or higher.

You can combine the platform enforcement rules with the `--soft-fail`, `--soft-fail-on`, and `--hard-fail-on` arguments to customize the options for a specific run. It will have the following effects. Note that these flags are still global and will get merged with the relevant enforcement rule for the particular framework being scanned.

* If you use `--soft-fail`, it overrides the enforcement rule hard fail threshold for all runners.
* If you use `--soft-fail-on` and / or `--hard-fail-on` with only check IDs (not severities), then it combines those lists with the hard fail threshold from the respective enforcement rule.
* If you use `--soft-fail-on` and / or `--hard-fail-on` with a severity, then those severities override the enforcement rule hard fail threshold for all runners.
