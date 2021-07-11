# Custom Encryption Attribute Calculation
When building queries, we noticed we were constantly asking a common question - _Is the resource encrypted?_

To avoid having to know the correct configuration of each resource, and to make queries more concise, we decided to add
`encryption` as a custom attribute to the relevant resource types. You can skip directly to:
1. [Overview](#overview)
2. [Example usage](#example-usage)
3. [Contributing](#contributing-to-extend-coverage)

## Overview
To support the different configurations of the different terraform resources with encryption, we've created 2 important
objects defined [here](./graph_components/generic_resource_encryption.py):
1. `GenericResourceEncryption` - this class executes the configuration logic based on the constructor parameters
   to decide whether the resource is encrypted or not.
2. `ENCRYPTION_BY_RESOURCE_TYPE` - a map of <resource_type, GenericResourceEncryption<resource_type>>. This means that
   for every resource type (i.e. `aws_s3_bucket`, `aws_rds_cluster` etc) there's either an entry in this map or there 
   isn't. If there is an entry - the GenericResourceEncryption class will decide whether it is encrypted according to
   the [calculation logic](#calculation-logic). If there is no entry - the attribute will not exist for that resource 
   type.
   

### Calculation Logic
ENCRYPTION_BY_RESOURCE_TYPE receives as a second parameter a dict, consisting of the attribute paths as keys & the 
possible matching values as value list, i.e.:
```python
{
    "encrypt_at_rest.enabled": [True],
    "kms_key_id": [],
    "node_to_node_encryption.enabled": [True]
}
```
Please note the empty list is supported - it means ANY. So in the case above, if the attribute `kms_key_id` exists in 
the resource it will be marked as encrypted, no matter what the actual value is for `kms_key_id`. However, we do expect
`encrypt_at_rest.enabled` to be set to `True` - otherwise it will be marked as unencrypted.

##Example Usage
This field can be leveraged in policies, i.e. query the field `encryption_` for the strings "ENCRYPTED" / "UNENCRYPTED".
Example [query](../../../tests/terraform/graph/checks_infra/attribute_solvers/equals_solver/EncryptedResources.yaml), 
and the expected resources can be found in the matching [test-case on line 22 here](../../../tests/terraform/graph/checks_infra/attribute_solvers/equals_solver/test_solver.py).

## Contributing to Extend Coverage
To add support for a new resource type, for example `foo_bar`, a new entry needs to be added to 
`ENCRYPTION_BY_RESOURCE_TYPE`, which maps the resource type string to an instance of `GenericResourceEncryption`.
The constructor first parameter is the resource type, and the second is the dict as described in the 
[calculation logic](#calculation-logic)
