---
title: "Gitlab CLI"
slug: "gitlab-cli"
hidden: false
createdAt: "2021-03-11T14:31:09.941Z"
updatedAt: "2021-03-18T13:27:02.859Z"
---
# Integrate Checkov with GitLab CI
You can integrate checkov into your GitLab CI pipelines. This provides a simple, automatic way of applying policies to your Terraform code both during merge request review and as part of your build process.

#Basic Setup
Add a new job in `.gitlab-ci.yml` in your repository (at whatever stage is appropriate for you).

Here is a basic example:
[block:code]
{
  "codes": [
    {
      "code": "stages:\n    - test\nvariables: \n  ALLOWFAILURE: true #True for AutoDevOps compatibility\n\ncheckov:\n  stage: test\n  allow_failure: $ALLOWFAILURE\n  image:\n    name: bridgecrew/checkov:latest\n    entrypoint:\n      - '/usr/bin/env'\n      - 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'\n  rules:\n    - if: $SAST_DISABLED\n      when: never\n    - if: $CI_COMMIT_BRANCH\n      exists:\n      - '**/*.yml'\n      - '**/*.yaml'\n      - '**/*.json'\n      - '**/*.template'\n      - '**/*.tf'      \n      - '**/serverless.yml'\n      - '**/serverless.yaml'\n  script:\n    - checkov -d . -o junitxml | tee checkov.test.xml\n  artifacts:\n    reports:\n      junit: \"checkov.test.xml\"\n    paths:\n      - \"checkov.test.xml\"",
      "language": "yaml",
      "name": " "
    }
  ]
}
[/block]
#Example Results
When your pipeline executes, it will run this job. If Checkov finds any issues, it will fail the build.

#View Gitlab CLI Results
## Pipeline Failure
For example, I have an S3 bucket that does not have versioning enabled. Checkov detects this and fails the job and pipeline.
[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/2c41577-gitlab_failed_job.png",
        "gitlab_failed_job.png",
        872,
        933,
        "#2b2b2b"
      ],
      "border": true
    }
  ]
}
[/block]
This will comment on an associated merge request or fail the build depending on the context.

GitLab will collect the results into the normal unit testing area of the pipeline and/or the merge request.

## Pipeline Success
Once you correct the configuration, Checkov verifies that no errors have been found.
[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/922fc23-gitlab_results.png",
        "gitlab_results.png",
        868,
        721,
        "#373737"
      ],
      "border": true
    }
  ]
}
[/block]
## Colored Output
Note that in the examples above, the output of the test results does not display colors. This is because GitLab Runner runs without an interactive TTY. Although Checkov does not currently support an environment variable to force colored output, the `script` command can be used to emulate `tty` so colors are displayed:
[block:code]
{
  "codes": [
    {
      "code": "stages:\n    - test\nvariables: \n  ALLOWFAILURE: true #True for AutoDevOps compatibility\n\ncheckov:\n  stage: test\n  allow_failure: $ALLOWFAILURE\n  image:\n    name: bridgecrew/checkov:latest\n    entrypoint:\n      - '/usr/bin/env'\n      - 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'\n  rules:\n    - if: $SAST_DISABLED\n      when: never\n    - if: $CI_COMMIT_BRANCH\n      exists:\n      - '**/*.yml'\n      - '**/*.yaml'\n      - '**/*.json'\n      - '**/*.template'\n      - '**/*.tf'      \n      - '**/serverless.yml'\n      - '**/serverless.yaml'\n  script:\n    # Use `script` to emulate `tty` for colored output.\n    - script -q -c 'checkov -d . ; echo $? > CKVEXIT'\n    - exit $(cat CKVEXIT)\n  artifacts:\n    reports:\n      junit: \"checkov.test.xml\"\n    paths:\n      - \"checkov.test.xml\"",
      "language": "yaml",
      "name": " "
    }
  ]
}
[/block]
#Further Reading
See the [GitLab CI documentation](https://docs.gitlab.com/ee/ci/) for additional information.
The there is also a working example of using GitLab CI with Checkov [here](https://gitlab.com/guided-explorations/ci-cd-plugin-extensions/checkov-iac-sast.  This example shows how to use the same Checkov YAML file as an includable extension so that all your jobs reuse the same job definition.