# Checkov

Bridgecrew is a platform to programmatically author and govern cloud infrastructure policies.
When policies are defined as code, they become more maintainable, versionable, testable and collaborative.
Use bridgecrew static analysis to vet infrastructure as code modules.  

## Principles
- **Security-oriented**: Checkov scans are defines as code (Python), allowing security and devops engineers to write content easily. 
- **Extensible**: Easily define your own scans, suppressions and extend the library so that it fits the policy granularity that suits your environment.
- **Rich-data** Preform resource scans or complex dependency graph scans using the powerful dependency graph query package.
- **Multi-Cloud** Enforce build-time policies across cloud providers

## Beyond the Horizon
Checkov **is not** runtime protection solution. It does not relay on running infrastucture at AWS/GCP/Azure. 
Checkov is not in the [Cloudcustodian](https://cloudcustodian.io/) or [StreamAlert](https://github.com/airbnb/streamalert) space.

It is more comparable to [Terrascan](https://github.com/cesar-rodriguez/terrascan) or [tfsec](https://github.com/liamg/tfsec). 

