---
layout: default
published: true
title: Custom YAML Policies Examples
nav_order: 4
---

# Examples - YAML-Based Custom Policies

## Basic Query - One Attribute Block

```yaml
---
metadata:
 name: "Check that all resources are tagged with the key - env"
 id: "CKV2_AWS_1"
 category: "GENERAL_SECURITY"
definition:
       cond_type: "attribute"
       resource_types: "all"
       attribute: "tags.env"
       operator: "exists"
```

## OR at Top Level - Two Attribute Blocks

```yaml
---
metadata:
 name: "Org's compute instances should not be t3.micro or t3.nano"
 id: "CKV2_AWS_1"
 category: "NETWORKING"
definition:
 or:
 - cond_type: "attribute"
   resource_types:
    - "aws_instance"
   attribute: "instance_type"
   operator: "not_equals"
   value: "t3.micro"
 - cond_type: "attribute"
   resource_types:
   - "aws_instance"
   attribute: "instance_type"
   operator: "not_equals"
   value: "t3.nano"
```

## OR Logic - Attribute Block

```yaml
---
metadata:
 name: "Check that all encrypted RDS clusters are tagged with encrypted: true"
 id: "CKV2_AWS_1"
 category: "SECRETS"
definition:
 and:
     - cond_type: "attribute"
       resource_types:
       - "aws_rds_cluster"
       attribute: "tags.encrypted"
       operator: "equals"
       value: "true"
     - or:
         - cond_type: "attribute"
           resource_types:
           - "aws_rds_cluster"
           attribute: "kms_key_id"
           operator: "exists"
         - cond_type: "attribute"
           resource_types:
           - "aws_rds_cluster"
           attribute: "storage_encrypted"
           operator: "equals"
           value: "true"
```

## OR -  Multiple Attribute Blocks

```yaml
---
metadata:
 name: "Ensure all AWS databases have Backup Policy"
 id: "CKV2_AWS_1"
 category: "BACKUP_AND_RECOVERY"
definition:
 or:
   - cond_type: "attribute"
     resource_types:
     - "aws_rds_cluster"
     - "aws_db_instance"
     attribute: "backup_retention_period"
     operator: "not_exists"
   - cond_type: "attribute"
     resource_types:
     - "aws_rds_cluster"
     - "aws_db_instance"
     attribute: "backup_retention_period"
     operator: "not_equals"
     value: "0"
   - cond_type: "attribute"
     resource_types:
     - "aws_redshift_cluster"
     attribute: "automated_snapshot_retention_period"
     operator: "not_equals"
     value: "0"
   - cond_type: "attribute"
     resource_types:
     - "aws_dynamodb_table"
     attribute: "point_in_time_recovery"
     operator: "not_equals"
     value: "false"
   - cond_type: "attribute"
     resource_types:
     - "aws_dynamodb_table"
     attribute: "point_in_time_recovery"
     operator: "exists"
```

## Simple Connection State Block and Filter and Attribute Blocks

```yaml
---
metadata:
 name: "Ensure all EC2s are connected only to encrypted EBS volumes"
 id: "CKV2_AWS_1"
 category: "ENCRYPTION"
definition:
    and:
        - cond_type: "attribute"
          resource_types:
          - "aws_ebs_volume"
          attribute: "encrypted"
          operator: "equals"
          value: "true"
        - cond_type: "connection"
          resource_types:
          - "aws_volume_attachment"
          connected_resource_types:
          - "aws_ebs_volume"
          operator: "exists"
        - cond_type: "filter"
          attribute: "resource_type"
          value:
           - "aws_ebs_volume"
          operator: "within"
```

## Complex Definition - Connection State Block and Filter and Attribute Blocks - Example 1

```yaml
---
metadata:
  name: "Ensure all ALBs are connected only to HTTPS listeners"
  id: "CKV2_AWS_1"
  category: "NETWORKING"
definition:
  and:
  - cond_type: "filter"
    value:
    - "aws_lb"
    attribute: "resource_type"
    operator: "within"
  - cond_type: "attribute"
    resource_types:
    - "aws_lb"    
    attribute: "load_balancer_type"
    operator: "equals"
    value: "application"
  - or:
    - cond_type: "connection"
      resource_types:
      - "aws_lb"
      connected_resource_types:
      - "aws_lb_listener"
      operator: "not_exists"
    - and:
      - cond_type: "connection"
        resource_types:
        - "aws_lb"
        connected_resource_types:
        - "aws_lb_listener"
        operator: "exists"
      - cond_type: "attribute"
        resource_types:
        - "aws_lb_listener"
        attribute: "certificate_arn"
        operator: "exists"
      - cond_type: "attribute"
        resource_types:
        - "aws_lb_listener"
        attribute: "ssl_policy"
        operator: "exists"
      - cond_type: "attribute"
        resource_types:
        - "aws_lb_listener"
        attribute: "protocol"
        operator: "equals"
        value: "HTTPS"
      - or:
        - cond_type: "attribute"
          resource_types:
          - "aws_lb_listener"
          attribute: "default_action.redirect.protocol"
          operator: "equals"
          value: "HTTPS"
        - cond_type: "attribute"
          resource_types:
          - "aws_lb_listener"
          attribute: "default_action.redirect.protocol"
          operator: "not_exists"
      - or:
        - cond_type: "connection"
          resource_types:
          - "aws_lb_listener_rule"
          connected_resource_types:
          - "aws_lb_listener"
          operator: "not_exists"
        - and:
          - cond_type: "connection"
            resource_types:
            - "aws_lb_listener_rule"
            connected_resource_types:
            - "aws_lb_listener"
            operator: "exists"
          - or:
            - cond_type: "attribute"
              resource_types:
              - "aws_lb_listener_rule"
              attribute: "default_action.redirect.protocol"
              operator: "equals"
              value: "HTTPS"
            - cond_type: "attribute"
              resource_types:
              - "aws_lb_listener_rule"
              attribute: "default_action.redirect.protocol"
              operator: "not_exists"
```

## Complex Definition - Connection State Block and Filter and Attribute Blocks - Example 2

```yaml
---
metadata:
  name: "Ensure resources allows encrypted ingress communication (SSH)"
  id: "CKV2_AWS_1"
  category: "NETWORKING"
definition:
  and:
  - cond_type: "filter"
    attribute: "resource_type"
    value:
    - "aws_instance"
    - "aws_elb"
    - "aws_lb"
    - "aws_db_instance"
    - "aws_elasticache_cluster"
    - "aws_emr_cluster"
    - "aws_redshift_cluster"
    - "aws_elasticsearch_domain"
    - "aws_rds_cluster"
    - "aws_efs_mount_target"
    - "aws_efs_file_system"
    - "aws_ecs_service"
    operator: "within"
  - cond_type: "connection"
    resource_types:
    - "aws_instance"
    - "aws_elb"
    - "aws_lb"
    - "aws_db_instance"
    - "aws_elasticache_cluster"
    - "aws_emr_cluster"
    - "aws_redshift_cluster"
    - "aws_elasticsearch_domain"
    - "aws_rds_cluster"
    - "aws_efs_mount_target"
    - "aws_efs_file_system"
    - "aws_ecs_service"
    connected_resource_types:
    - "aws_security_group"
    - "aws_default_security_group"
    operator: "exists"
  - or:
    - cond_type: "attribute"
      resource_types:
      - "aws_security_group"
      - "aws_default_security_group"
      attribute: "ingress.from_port"
      operator: "equals"
      value: "22"
    - cond_type: "attribute"
      resource_types:
      - "aws_security_group"
      - "aws_default_security_group"
      value: "22"
      operator: "equals"
      attribute: "ingress.to_port"
  - or:
    - cond_type: "connection"
      resource_types:
      - "aws_security_group_rule"
      connected_resource_types:
      - "aws_security_group"
      - "aws_default_security_group"
      operator: "not_exists"
    - and:
      - cond_type: "connection"
        resource_types:
        - "aws_security_group_rule"
        connected_resource_types:
        - "aws_security_group"
        - "aws_default_security_group"
        operator: "exists"
      - cond_type: "attribute"
        resource_types:
        - "aws_security_group_rule"
        attribute: "type"
        operator: "equals"
        value: "ingress"
      - or:
        - cond_type: "attribute"
          resource_types:
          - "aws_security_group_rule"
          attribute: "to_port"
          operator: "equals"
          value: "22"
        - cond_type: "attribute"
          resource_types:
          - "aws_security_group_rule"
          attribute: "from_port"
          operator: "equals"
          value: "22"
```
