## Python Checks

Each Check in checkov is responsible for defining identifying ONE violation in the code which we want to prevent.
We NEVER define a check which is trying to identify several issues.
Each check also validates ONLY ONE ENTITY at a time, and CANNOT check for connections between multiple entities.
Each check inherits from the base class of `BaseCheck` under the `checkov/common` directory.
Each check should add the following fields in the constructor:
- `name` - one line of accurate description of the check for a human to read and understand.
- `id` - the check's id, always in one of the formats:
    1. `CKV_<cloud-provider>_<number>` where `cloud-provider` would be `AWS`, `AZURE` or `GCP` based on cloud provider. We will choose this if the check is related to a specific cloud provider.
    2. `CKV_<framework>_<number>` where `framework` is a 3 letter representation fo the framework like `K8S`. We will choose this option when we do not have a specific cloud provider we use.
- `supported_resources` - tuple of resource types the check is intended to run against.
- `categories` - tuple of categories this check relate to, based on `CheckCategories` object under `checkov/common`.

Note that we don't want to have 2 checks with the same id, and the `<number>` should follow. So if the last check for K8S is number 75, the next check for k8s should be `CKV_K8S_76`.
The full index of available checks is maintained under [Policy Index](../5.Policy%20Index/).

The main function which defines the check is `scan_entity_conf`, but this can be also overrided in specific frameworks to allow easier implementation, with some examples are `scan_resource_conf` in `terraform` design for scanning `resource` objects in terraform, and `get_inspected_key` which is implemented in various frameworks.
Main notes:
1. `scan_entity_conf` - getting as input a dict representation of the entity we want to scan with all attributes defined on it after the graph building. Uses the dict to understand if the entity is defined correctly. If we use it we should also implement `get_evaluated_keys` to specify the specific keys we tried to check, or we can override the `self.evaluated_keys` during the implementation of `scan_entity_conf`.
2. `get_inspected_key` - as opposed to `scan_entity_conf`, this function gets the same input but just returns the string which represents the jsonpath of the key it searches. If found, the policy passes and the `evaluated_keys` field is automatically assignes it. 
NOTE - we shouldn't implement both `get_inspected_key` and `scan_entity_conf` together, only one of them.

## Graph Checks
Graph checks relate to checks which REQUIRE CONNECTIONS BETWEEN MULTIPLE ENTITIES.
For example, if we define a service account with certain write permissions in kubernetes, by itself it's not a violation. But if we use it in a k8s resource which should have minimal permissions, it might be an issue.
Graph checks are defined in `yaml` files instead of `python` files and use the BQL syntax which is defined under the [Yaml Custom Policies documentation](../3.Custom%20Policies/YAML%20Custom%20Policies.md).
The graph checks are usually written under the `checks` directory of the relevant IAC framework under a directory called `graph` or `graph_checks`.
All graph checks's ids start with `CKV2_` (as opposed to `CKV_` for python checks).
We define a connection for graph checks between 2 entities by the existence of an edge between the 2 objects which represent those resources.
The implementation of all operators which are available for graph checks are under the directory `checkov/common/graph/checks_infra/solvers`.