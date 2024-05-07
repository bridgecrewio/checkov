---
layout: default
published: true
title: GitLab CI
nav_order: 4
---

# Integrate Checkov with GitLab CI

Since Checkov supports GitLab's SAST JSON format, using it in your GitLab CI pipelines enables integration with GitLab's most advanced security functionality in [Security Dashboard](https://docs.gitlab.com/ee/user/application_security/security_dashboard/), [Merge Request findings display](https://docs.gitlab.com/ee/user/application_security/sast/) and, importantly [Security Policy Merge Approvals](https://docs.gitlab.com/ee/user/application_security/policies/scan-result-policies.html).

## GitLab CI Component Setup
GitLab CI Components are managed CI dependencies published by GitLab and the GitLab community.

```yaml
include:
  - component: $CI_SERVER_FQDN/guided-explorations/ci-components/checkov-iac-sast/checkov-iac-sast@<VERSION>
```

Where <VERSION> is the component version from [the Checkov components listing here](https://gitlab.com/explore/catalog/guided-explorations/ci-components/checkov-iac-sast).

See documentation on the [Checkov GitLab CI Component](https://gitlab.com/explore/catalog/guided-explorations/ci-components/checkov-iac-sast)

## Manual Custom Setup
Add a new job in `.gitlab-ci.yml` in your repository (at whatever stage is appropriate for you).

Here is a basic example:

```yaml
stages:
    - test
    
checkov-iac-sast:
checkov-iac-sast-qdjs:
  variables:
    CKV_CONTAINER_TAG: 3.2.83
# Do not set at this level if you wish to also set it at a higher level
#    CKV_IS_ALLOW_FAILURE:
#      value: 'true' # defaults to 'true'(by only checking for false)
#      description: 'Whether Checkov findings should fail the build. It is not a GitLab best practice to fail builds right in scanner jobs.'
#    CKV_ATTEMPT_COLOR_LOGS:
#      value: 'false' # defaults to 'false' (by only checking for true)
#      description: 'Whether to attempt to use the "script" command to show color output in GitLab CI'
  stage: test
  image:
    name: bridgecrew/checkov:$CKV_CONTAINER_TAG
    entrypoint:
      - '/usr/bin/env'
      - 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
  rules:
    - if: $SAST_DISABLED
      when: never
    - if: $CI_COMMIT_BRANCH && $CKV_IS_ALLOW_FAILURE == "false"
      allow_failure: false
      exists:
      - '**/*.yml'
      - '**/*.yaml'
      - '**/*.json'
      - '**/*.template'
      - '**/*.tf'      
      - '**/serverless.yml'
      - '**/serverless.yaml'
    - if: $CI_COMMIT_BRANCH
      allow_failure: true
      exists:
      - '**/*.yml'
      - '**/*.yaml'
      - '**/*.json'
      - '**/*.template'
      - '**/*.tf'      
      - '**/serverless.yml'
      - '**/serverless.yaml'
  script:
    - |
      if [[ "${CI_DEBUG_TRACE,,}" == "true" ]]; then
        echo "GitLab's global trace (CI_DEBUG_TRACE) has been set, debug logging. More info: https://docs.gitlab.com/ee/ci/variables/#enable-debug-logging"
        set -xv
      fi
      
      if [[ ! "${CKV_IS_ALLOW_FAILURE}" == "false" ]]; then
        SOFTFAILARG='--soft-fail'
      fi

      if [[ "${GITLAB_FEATURES}" == *"security_dashboard"* ]]; then
        echo "You are licensed for GitLab Security Dashboards, you will find scanning results in Security Dashboard."
        OUTPUTARG='gitlab_sast'
        OUTPUTFILEEXT='json'
      else
        echo "You will find scanning results in the GitLab Test results visualization panel on your pipeline tabs."
        OUTPUTARG='junitxml'
        OUTPUTFILEEXT='xml'
      fi

      if [[ "${CKV_ATTEMPT_COLOR_LOGS,,}" == "true" && ! -z "$(command -v screen)" ]]; then
        script -q -c 'checkov ${SOFTFAILARG,,} -d . --output ${OUTPUTARG} | tee checkov-sast.${OUTPUTFILEEXT}' ; CKVEXIT=${PIPESTATUS[0]}
      else
        checkov ${SOFTFAILARG} -d . --output ${OUTPUTARG} | tee checkov-sast.${OUTPUTFILEEXT} ; CKVEXIT=${PIPESTATUS[0]}
      fi

      if [[ ! "${CKV_IS_ALLOW_FAILURE,,}" == "false" ]]; then
        exit $(cat CKVEXIT)
      fi

  artifacts:
    reports:
      junit: "checkov-sast.xml"
      sast: "checkov-sast.json"
```

## Example Results
When your pipeline executes, it will run this job. If Checkov finds any issues, it will report them to GitLab.

### GitLab Security Policy Merge Approvals Instead of Pipeline Failures.
GitLab has advanced DevSecOps workflow automation. Rather than fail builds, Security Policy Merge Approvals simply prevent merging before code ever progresses to a shared branch or production bound branch. This allows developers to continue working on their code while collaborating on security findings. Once they resolve the offending findings, the approval rule becomes optional without any human intervention or oversight. In the scope of a Merge Request scanning results are only for new vulnerabilities in the code changed in the Merge Request - so this is a very effective way to both retain developer productivity and prevent new vulnerabilities from being merged without external involvement of another team.

Pipeline soft failure also allows all other security scanners to run and have the findings collected - this is helpful when multiple scanner findings help in vulnerability root cause analysis and solutions and for developer productivity in addressing multiple findings at one time.

#### Pipeline Failure
Pipeline failure might be appropriate when developers are not required to use Merge Requests and approvals to merge to a production bound branch - but this should be an extremely rare configuration if security is a high concern.

Enable this by setting the GitLab CI variable: `CKV_IS_ALLOW_FAILURE: 'false'`

For this example, an S3 bucket that does not have versioning enabled. Checkov detects this and fails the job and pipeline.

[](gitlab_failed_job.png)

This will comment on an associated merge request or fail the build depending on the context.

GitLab will collect the results into the normal unit testing area of the pipeline and/or the merge request.

#### Pipeline Success
Once you correct the configuration, Checkov verifies that no errors have been found.

[](gitlab_results.png)

## Colored Output
GitLab Runner runs without an interactive TTY so generally does not display color. The `script` command can be added in the above to emulate `tty` so colors can be displayed. Update the above code with this fragment.

Enable this by setting the GitLab CI variable: `CKV_ATTEMPT_COLOR_LOGS: 'true'`

See the [GitLab CI documentation](https://docs.gitlab.com/ee/ci/) for additional information.
There is also a working example of using GitLab CI with Checkov [here](https://gitlab.com/guided-explorations/ci-cd-plugin-extensions/checkov-iac-sast).  This example shows how to use the same Checkov YAML file as an includable extension so that all your jobs reuse the same job definition.
