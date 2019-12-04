# Checkov
[![Maintained by Bridgecrew.io](https://img.shields.io/badge/maintained%20by-bridgecrew.io-blueviolet)](https://bridgecrew.io)
[![build status](https://github.com/bridgecrewio/terraform-static-analysis/workflows/build/badge.svg)](https://github.com/bridgecrewio/terraform-static-analysis/actions?query=workflow%3Abuild) 
[![code_coverage](coverage.svg)](https://github.com/bridgecrewio/terraform-static-analysis/actions?query=workflow%3Acoverage)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
![Terraform Version](https://img.shields.io/badge/tf-%3E%3D0.12.0-blue.svg)

Bridgecrew is a platform to programmatically author and govern cloud infrastructure policies.
When policies are defined as code, they become more maintainable, versionable, testable and collaborative.
Use bridgecrew static analysis to vet infrastructure as code modules.  

**Table of contents**
- [Getting started](#getting-started)
- [Beyond the horizon](#beyond-the-horizon)
- [Principles](#principles)
- [CLI](#cli)
- [Contributing](#contributing)
- []
- [Resource scans](#resource-scans)

## Getting started
Please visit the Checkov documentation for help with [installing checkov**TODO](), getting a [quick_start**TODO](), or a more complete [tutorial**TODO]().

Documentation of GitHub master (latest development branch): [ReadTheDocs Documentation**TODO]()
 
## Beyond the Horizon
Checkov **is not** runtime protection solution. It does not relay on running infrastucture at AWS/GCP/Azure. 
Checkov is not in the [Cloudcustodian](https://cloudcustodian.io/) or [StreamAlert](https://github.com/airbnb/streamalert) space.

It is more comparable to [Terrascan](https://github.com/cesar-rodriguez/terrascan) or [tfsec](https://github.com/liamg/tfsec). 

## Principles
- **Security-oriented**: Checkov scans are defines as code (Python), allowing security and devops engineers to write content easily. 
- **Extensible**: Easily define your own scans, suppressions and extend the library so that it fits the policy granularity that suits your environment.
- **Rich-data** Preform resource scans or complex dependency graph scans using the powerful dependency graph query package.

## CLI
###********TODO: List checks
###********TODO: Run Checks
###********TODO: Suppress Check
###********TODO: Output formats

## Contributing
Want to help build Checkov? Checkout our [contributing documentation ***TODO](***TODO)

## Who Maintains Checkov?
Checkov is the work of the [community](graphs/contributors), 
but the core committers/maintainers are responsible for reviewing and merging PRs as well as steering 
conversation around new feature requests. If you would like to become a maintainer, please review the Chekov 
committer requirements.


