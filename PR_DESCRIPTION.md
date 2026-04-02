# Pull Request: Include UNKNOWN check results in report

**PR Title:** `feat(general): include UNKNOWN check results in report and outputs`

---

**By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 license.**

---

## Description

Policies can return `CheckResult.UNKNOWN` when they cannot determine pass or fail (e.g. variable-dependent values, Terraform plan `after_unknown`, or cases like CKV_AWS_140 when a global cluster is created from a source). Previously those results were never added to the report, so UNKNOWNs were invisible in the summary, JSON, CLI, and other outputs.

**Why surface UNKNOWN checks:** It’s important to see which checks were **not evaluated** (not passed, failed, or skipped). That lets you spot coverage gaps, follow up when a policy couldn’t reach a definite result, and decide whether to resolve variables, adjust the plan, or accept the uncertainty—instead of assuming “no result” meant the check didn’t run or wasn’t applicable.

This change adds an `unknown_checks` list to the report and treats it like `passed_checks` / `failed_checks` / `skipped_checks` everywhere:

- **Report:** `Report.unknown_checks`, `add_record()` appends UNKNOWN, summary includes `unknown`, and `get_dict` / `get_all_records` / merge / dedupe include it.
- **Outputs:** CLI (yellow, with count), JSON, SARIF (note), CSV, JUnit (skipped with message), and Bridgecrew upload.
- **Docs:** New [Unknown Check Results](docs/2.Basics/Unknown%20Check%20Results.md) with CKV_AWS_140 example and `EVAL_TF_PLAN_AFTER_UNKNOWN`; README and Reviewing Scan Results updated.

Backward compatibility: `from_reduced_json` still loads reports that don’t have `unknown_checks` by normalizing the checks dict. UNKNOWN does not affect exit code.

Fixes # (issue)

---

## New/Edited policies (Delete if not relevant)

*Not applicable — no new or edited policies.*

---

## Checklist

- [x] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [x] I have added tests that prove my feature, policy, or fix is effective and works
- [x] New and existing tests pass locally with my changes
