---
layout: default
published: true
title: Hard and soft fail
nav_order: 7
---

# Hard and soft fail

You can fine tune exactly which cases cause the Checkov scan to return a pass or fail result. The exit code of the Checkov process will be `0` for a passing result and `1` for a failure result.

A result is passing if all checks are passed or skipped; otherwise, the result is a failure. However, you can use the `--soft-fail`, `--soft-fail-on`, and `--hard-fail-on` options to customize this.

A "soft failure" is a result in which Checkov finds and reports errors during the scan, but still returns an exit code of `0`. This differs from skipping or suppressing checks in that a skipped or suppressed check is not a failing check, and thus will not result in an error exit code.

## Argument details

### --soft-fail

Use the `--soft-fail` (`-s`) option to have Checkov always return a `0` exit code, regardless of scan results.

### --soft-fail-on

Use the `--soft-fail-on` option to pass one or more check IDs and / or severity levels to specify which failed checks will result in a soft fail result. Any failed check that does not match a criteria in the soft-fail list will result in an error exit code (`1`).

### --hard-fail-on

Use the `--hard-fail-on` option to pass one or more check IDs and / or severity levels to specify which failed checks will result in an error result. If all failed checks do *not* match any criteria in the hard-fail list, then the result of the scan will be a soft fail (`0`).
