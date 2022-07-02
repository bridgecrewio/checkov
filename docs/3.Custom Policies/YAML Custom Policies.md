---
layout: default
published: true
title: YAML Custom Policies
nav_order: 3
---

# Create Custom Policy - YAML - Attribute Check and Composite

Custom policies created in YAML support checking a resource’s connection state and the use of complex AND/OR logic. Read also how to [create custom Python Policies for attribute scanning](https://www.checkov.io/3.Custom%20Policies/Python%20Custom%20Policies.html).

A YAML-based custom policy for Checkov consists of sections for the **Metadata** and **Policy Definition**.

![](policy-definition.png)

**Metadata**

The Metadata includes:

* Policy Name
* ID - `CKV2_<provider>_<number>`
* Category

The possible values for category are:

* GENERAL_SECURITY
* LOGGING
* ENCRYPTION
* NETWORKING
* IAM
* BACKUP_AND_RECOVERY
* CONVENTION
* SECRETS
* KUBERNETES

## Policy Definition

The policy definition consists of:

* **Definition Block(s)** - either *Attribute Block(s)* or *Connection State Block(s)* or both
* **Logical Operator(s)** (optional)
* **Filter**(optional)


## Types of Definition Blocks

* **Attribute Blocks:** The policy describes resources with a certain configuration as defined by a configuration **attribute** and its value (per Terraform), or by the presence/absence of an attribute.
* **Connection State Blocks** - The policy describes resources in a particular **Connection state**; either connected or not connected to another type of resource (for example, a security group).

### Using AND/OR Logic
A policy definition may include multiple blocks (**Attribute**, **Connection state** or both), associated by **AND/OR** logic.

## Attribute Blocks

An **Attribute Block** in a policy's definition indicates that a resource will be non-compliant if a certain configuration attribute does not have a specified value or if it exists/doesn't exist.

Bridgecrew's custom policies in code utilize the Terraform attribute library and syntax. These policies are checked during scans of both build-time and runtime resources and for all supported cloud providers.

### Attribute Block Example

The Attribute Block in the `definition` in the example below is used to ensure that a proper back-up policy is configured for Redshift clusters:

```yaml
definition:
     cond_type: "attribute"
     resource_types:
     - "aws_redshift_cluster"
     attribute: "automated_snapshot_retention_period"
     operator: "not_equals"
     value: "0"
```

### Attribute Condition: Operators

| Operator              | Value in YAML           |
|-----------------------|-------------------------|
| Equals                | `equals`                |
| Not Equals            | `not_equals`            |
| Regex Match           | `regex_match`           |
| Not Regex Match       | `not_regex_match`       |
| Exists                | `exists`                |
| Not Exists            | `not_exists`            |
| One Exists            | `one_exists`            |
| Any                   | `any`                   |
| Contains              | `contains`              |
| Not Contains          | `not_contains`          |
| Within                | `within`                |
| Starts With           | `starting_with`         |
| Not Starts With       | `not_starting_with`     |
| Ends With             | `ending_with`           |
| Not Ends With         | `not_ending_with`       |
| Greater Than          | `greater_than`          |
| Greater Than Or Equal | `greater_than_or_equal` |
| Less Than             | `less_than`             |
| Less Than Or Equal    | `less_than_or_equal`    |
| Subset                | `subset`                |
| Not Subset            | `not_subset`            |
| Json Path Equals      | `jsonpath_equals`       |
| Json Path Exists      | `jsonpath_exists`       |
| Json Path Not Exists  | `jsonpath_not_exists`   |
| Is Empty              | `is_empty`              |
| Is Not Empty          | `is_not_empty`          |

### Attribute Condition: Keys and Values

| Key | Type | Value(s)                                                                                                                                                                                                                                                                                                 |
| --- | --- |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `cond_type` | string | Must be `attribute`                                                                                                                                                                                                                                                                                      |
| `resource_type` | collection of strings | Use either `all` or `[resource types from list]`                                                                                                                                                                                                                                                         |
| `attribute` | string | Attribute of defined resource types. For example, `automated_snapshot_retention_period`                                                                                                                                                                                                                  |
| `operator` | string | - `equals`, `not_equals`, `regex_match`, `not_regex_match`, `exists`, `not exists`, `any`, `contains`, `not_contains`, `within`, `starting_with`, `not_starting_with`, `ending_with`, `not_ending_with`, `greater_than`, `greater_than_or_equal`, `less_than`, `less_than_or_equal`, `jsonpath_equals`, `jsonpath_exists`, `jsonpath_not_exists`, `is_empty`, `is_not_empty` |
| `value` (not relevant for operator: `exists`/`not_exists`) | string | User input.                                                                                                                                                                                                                                                                                              |


## Connection State Block

A Connection State Block indicates a type of resource that has or does not have a connection to another type of resource.
In the example presented in the table below, in order to be compliant, `aws_lb` and `aws_elb` must have connections to either `aws_security_group` or `aws_default_security_group`.

| Group A | Group B |
| --- | --- |
|`aws_lb` `aws_elb` | `aws_security_group` `aws_default_security_group` |


### Connection State Example

The Connection State Block below indicates that to be compliant with the policy, resources of type `aws_lb` or of type `aws_elb` must be connected to either a resource of type `aws_security_group` or a resource of type `aws_default_security_group`.

```yaml
definition:
       cond_type: "connection"
       resource_types:
           - "aws_elb"
           - "aws_lb"
       connected_resource_types:
         - "aws_security_group"
         - "aws_default_security_group"
       operator: "exists"
```

### Connection State Condition: Operators

| Operator | Value |
| ----- | ----- |
| Exists | `exists` |
| Not Exists | `not_exists` |

### Connection State Condition: Keys and Values

| Key | Type | Values |
| ----- | ----- | ----- |
| `cond_type` | string | Must be `connection` |
| `resource_types` |   | Use either `all` or `[included resource type from list]` |
| `connected_resource_types` | collection of strings | Use either `all` or `[included resource type from list]` |
| `operator` | string | `exists`/`not exists` |

## Filters

Filters can be used to limit the types of resources relevant to a condition. Filters are most commonly used for Connection Blocks (for Attribute Blocks you can easily limit the resource type with the `resource_type` parameter).
For example, you may want to enforce a policy only for a specific resource type (or types) from specific groups defined in the conditions. Filters are available only for AND logic at the top level.

### Filter Example

The Custom Policy in this example ensures that all ELBs are attached to security groups as shown in the table below. In line with best practices, connections of this nature should be defined using the `security_groups` key.

| Group A | Group B |
| ----- | ----- |
| `aws_elb` | `aws_security_group` `aws_default_security_group` |
| Not Exists | `not_exists` |

```yaml
definition:
 and:
      - cond_type: "filter"
        attribute: "resource_type"
        value:
           - "aws_elb"
        operator: "within"
      - cond_type: "connection"
        resource_types:
           - "aws_elb"
        connected_resource_types:
         - "aws_security_group"
         - "aws_default_security_group"
        operator: "exists"
```

*Note: The condition above uses AND logic. See [additional examples](https://www.checkov.io/3.Custom%20Policies/Examples.html) for complex logic in policy definitions.*

## Using AND/OR Logic

The Bridgecrew platform allows you to combine definition blocks using AND/OR operators.

* The top-level logical operator is the first key below \"definition\" (and not an item in a collection). It defines the relationship of all of the definition blocks in the specific YAML policy definition.
* Filter blocks apply (only) to the top-level and constitute an AND condition. For example, if you'd like to indicate a requirement for a Connection State between types of resources, but only within a certain subset of all of those resources.
Every other logical operator applies within a collection. For example, you can use AND/OR logic in a collection of key-value pairs.

### Example

The logic in the policy definition shown below is:
`AND[block 1,block 2,OR[block 3,block 4]]`.

```yaml
#....
defintion:
           and:
               - #filter block 1
               - #block 2
               - or:
                   - #block 3
                   - #block 4
```

[See all examples of Custom Policies in code](https://www.checkov.io/3.Custom%20Policies/Examples.html)
