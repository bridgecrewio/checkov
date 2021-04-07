---
layout: default
published: true
title: Custom Policies Overview
order: 1
---

Custom Policies allow monitoring and enforcing of cloud infrastructure configuration in accordance with your organization's specific needs. For example, for certain resource types, you may want to enforce a tagging methodology or a special secure password policy; or you may want to restrict usage of a new service depending on the types of other services it is connected to.

* You can create Custom Policies in Python that check for the status of configuration attributes - see [Create Custom Policy - Python - Attribute Check](doc:create-custom-policy-python-attribute-check).
* You can create Custom Policies in YAML format that can (1) check for the status of configuration attributes and (2) check the connection-state between types of resources - see [Create Custom Policy - YAML - Attribute Check and Connection-State Check](doc:create-custom-policy-yaml-attribute-check-and-composite).
* You can also apply sophisticated logic to multiple conditions within a Custom Policy - see [Custom Policy Examples](doc:custom-policy-examples-1).
* After creating tests for your Custom Policies, you can contribute them - see [Contribute New Policy](doc:contribute-new-policy).
