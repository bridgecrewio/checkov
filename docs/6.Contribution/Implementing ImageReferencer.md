# Implementing ImageReferencer
The relevant class can be found at `checkov/common/images/image_referencer.py`
## How was the idea born?
Container images are referenced widely across CI workflow files, Terraform, Serverless, K8 manifests, etc. 
Those files can naturally have a misconfig and reference an image with a vulnerability.

When using checkov with API token, checkov gets that capability to perform image scanning and utilize Prisma cloud compute vulnerability DB.
If `ImageReferencer` is derived by a `Runner`than referenced images in an IaC file can be scanned for vulnerabilities.

## Would container images are scanned automatically? 
Yes, If the `--framework` `sca_image` is not excluded from the execution scope, an API token is provided.
The automatic scanning is happening thanks to the registration process for any Derived class of ImageReferencers that occurs in `RunnerRegistry` init.    
Implementing image referencer will mean scan results will take additional time since images are being pulled.
 
## What needs to be implemented? 
Look at: `checkov/common/images/image_referencer.py`  
and the derived class: `checkov/github_actions/runner.py`

## What would be a good candidate?
K8 manifests, helm charts, Serverless functions utilizing containers, and the list goes on :) 

## Example CLI command 
checkov -d 
```bash
export CHECKOV_EXPERIMENTAL_IMAGE_REFERENCING=True # notice this feature flag will be removed in the future
checkov -d /checkov/integration_tests/example_workflow_file/.github/workflows/ --framework sca_image --bc-api-key SOME_TOKEN
```
