**By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 license.**

[//]: # "
    # PR Title
    We use the title to create changelog automatically and therefore only allow specific prefixes
    - break:    to indicate a breaking change, this supersedes any of the other types
    - feat:     to indicate new features or checks
    - fix:      to indicate a bugfix or handling of edge cases of existing checks
    - docs:     to indicate an update to our documentation
    - chore:    to indicate adjustments to workflow files or dependency updates
    - platform: to indicate a change needed for the platform
    Each prefix should be accompanied by a scope that specifies the targeted framework. If uncertain, use 'general'.
    #    
    Allowed prefixs:
    ansible|argo|arm|azure|bicep|bitbucket|circleci|cloudformation|dockerfile|github|gha|gitlab|helm|kubernetes|kustomize|openapi|sast|sca|secrets|serverless|terraform|general|graph|terraform_plan|terraform_json
    #
    ex.
    feat(terraform): add CKV_AWS_123 to ensure that VPC Endpoint Service is configured for Manual Acceptance
"

## Description

*Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context. List any dependencies that are required for this change.*

Fixes # (issue)

## New/Edited policies (Delete if not relevant)

### Description
*Include a description of what makes it a violation and any relevant external links.*

### Fix
*How does someone fix the issue in code and/or in runtime?*

## Checklist:

- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] I have added tests that prove my feature, policy, or fix is effective and works
- [ ] New and existing tests pass locally with my changes
