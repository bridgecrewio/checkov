---
layout: default
published: true
title: Bitbucket Cloud Pipelines
nav_order: 2
---

# Integrate Checkov with Bitbucket Cloud Pipelines

You can integrate checkov into your Bitbucket Cloud pipelines. This provides a simple, automatic way of applying policies to your Terraform code both during merge request review and as part of your build process.

## Basic Setup

Add a new step in the `bitbucket-pipelines.yml` file in your repository as part of whichever pipelines are appropriate for you.

Here is a minimalistic example:
```yaml
checkov: &checkov
  step:
    name: Checkov
    image:
      name: bridgecrew/checkov:latest
      entrypoint:
        - '/usr/bin/env'
        - 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
    script:
      - checkov -d .

pipelines:
  default:
    - <<: *checkov
```

## Example Results

When your pipeline executes, it will run this job. If checkov finds any issues, it will fail the build.

### Pipeline Failure

For example, I have an S3 bucket that does not have versioning enabled. Checkov detects this and fails the job and pipeline.

![Bitbucket Failed Pipeline](bitbucket_failed_pipeline.png)

This will comment on an associated merge request or fail the build depending on the context.

### Pipeline Success

Once I have corrected the configuration, checkov verifies that all is well.

![Bitbucket Results](bitbucket_results.png)

## Further Reading

See the [Bitbucket pipelines documentation](https://confluence.atlassian.com/bitbucket/build-test-and-deploy-with-pipelines-792496469.html) for additional information.
