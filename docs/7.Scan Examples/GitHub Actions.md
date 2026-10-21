---
layout: default
published: true
title: GitHub Actions configuration scanning
nav_order: 20
---

# GitHub Actions configuration scanning
Checkov supports the evaluation of policies on your GitHub Actions workflow files.
When using checkov to scan a directory that contains GitHub Actions workflows (`.github/workflows/*.yml`) it will validate if the workflows are compliant with GitHub Actions best practices such as not running shell commands built from untrusted input, limiting the permissions of the `GITHUB_TOKEN`, and more.

Full list of GitHub Actions policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/github_actions.html).

### Example misconfigured GitHub Actions workflow

```yaml
name: label
on: pull_request
jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - run: echo labelling
```

### Running in CLI

```bash
checkov -d . --framework github_actions
```

### Example output
```bash
github_actions scan results:

Passed checks: 0, Failed checks: 1, Skipped checks: 0

Check: CKV2_GHA_1: "Ensure top-level permissions are not set to write-all"
	FAILED for resource: on(label)
	File: /.github/workflows/label.yml:6-7
```

## CKV2_GHA_1: Ensure top-level permissions are not set to write-all

### What it checks
The check looks at the `permissions` key at the top level of each workflow file, the one that sets the default permissions of the `GITHUB_TOKEN` for every job in the workflow.
It fails when:

- the top-level `permissions` is set to `write-all`, or
- the workflow has no top-level `permissions` key at all.

The second case is the one that surprises people. When a workflow does not set `permissions`, the token gets the default permissions configured for the repository or organization, and Checkov cannot see that setting.
For many repositories and organizations that default is still read and write for most scopes, so Checkov treats a missing top-level `permissions` key as `write-all`.
Permissions set inside a job (`jobs.<job_id>.permissions`) do not change this result, because they only apply to that job and any job without its own `permissions` key still falls back to the workflow default.

### Why it matters
Every job gets a `GITHUB_TOKEN`. If a step in a job is compromised, for example through a malicious dependency, a compromised third party action or a shell injection, it can use that token with all the permissions the job was given.
A write token can, for example, push code, create releases, and change issues and pull requests. Following least privilege, a workflow should start with no permissions and grant only what each job needs.

### How to fix it
Set the top-level permissions to an empty map, which removes all permissions from the default, and grant permissions per job:

```yaml
name: label
on: pull_request
permissions: {}
jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - run: echo labelling
```

If most jobs need the same read access, you can instead set a read-only default at the top level and add write scopes only on the jobs that need them:

```yaml
permissions:
  contents: read
```

`permissions: read-all` also passes this check, but it gives every job read access to every scope, so prefer `permissions: {}` or a minimal list of scopes.

For the full syntax see the GitHub documentation on [permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions) and on [the `GITHUB_TOKEN`](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token).
