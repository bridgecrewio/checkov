---
layout: default
published: true
title: Policies
order: 3
---

# Policies

Checkov runs static code analysis on Terraform files. It will scan each resource only for policies that were defined by the policy file. 

Policies are expressed as Python files and include the following:

* The type of resource to run the policy against
* The required result(s) of a specific configuration under that resource



## Writing a new Policy

A policy needs to specify the following items:

``name`` : A new policy's unique purpose; It should ideally specify the positive desired outcome of the policy.

``id``: A mandatory unique identifier of a policy; Native policies written by Bridgecrew contributors will follow the following convention ``CKV_providerType_serialNumber``. (e.g. `CKV_AWS_9` , `CKV_GCP_12`)

``supported_resources``: Infrastructure objects, as described in Terraform language; This should usually contain one specific resource block.

``categories``: Categorization of a scan; usually used to produce compliance reports, pipeline analytics and infrastructure health metrics, etc.



For this tutorial let's produce a policy that ensures that new RDS services spun-up are encrypted at rest ([CKV_AWS_16](https://github.com/bridgecrewio/checkov/blob/master/checkov/terraform/checks/resource/aws/RDSEncryption.py)).

1. Start by creating a new file in the AWS check directory ``checkov/terraform/checks/resource/aws/RDSEncryption.py``
2. Import the following:

```python
from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck
```

3. At this point, we define the meta entities for this check: ``name``, ``id``, ``supported_resources``, ``categories``

```python
class RDSEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the RDS is securely encrypted at rest"
        id = "CKV_AWS_16"
        supported_resources = ['aws_db_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
```

4. Next we define a simple check of the ```aws_db_instance``` resource block to find if ```aws_db_instance``` is disabled. When disabled, we require it will result in a ```CheckResult.FAILURE```.

```python
def scan_resource_conf(self, conf):
    """
        Looks for encryption configuration at aws_db_instance:
        https://www.terraform.io/docs/providers/aws/d/db_instance.html
    :param conf: aws_db_instance configuration
    :return: <CheckResult>
    """
    if 'storage_encrypted' in conf.keys():
        key = conf['storage_encrypted'][0]
        if key:
            return CheckResult.PASSED
    return CheckResult.FAILED
```

5. Last - our file should conclude the policy name and operationalize it with this statement.

```python
check = RDSEncryption()
```



## Run a new scan

To run a new scan containing our newly added policy, use the ```checkov``` command.

```bash
checkov -d /user/tf
```



## Next Steps

Explore your scan [Results](Results.md) and check out the supported output methods (CLI, JSON, Junit XML).

##
