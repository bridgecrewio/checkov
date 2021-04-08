---
layout: default
published: true
title: Custom Policies Overview
nav_order: 1
---

# Custom Policies Overview

Custom Policies allow monitoring and enforcing of cloud infrastructure configuration in accordance with your organization's specific needs. For example, for certain resource types, you may want to enforce a tagging methodology or a special secure password policy; or you may want to restrict usage of a new service depending on the types of other services it is connected to.

* You can create custom policies in [Python](../3.Custom%20Policies/Python%20Custom%20Policies.md) that check for the status of configuration attributes.
* You can create custom policies in [YAML](../3.Custom%20Policies/YAML%20Custom%20Policies.md) that can both check for the status of configuration attributes and check the connection state between types of resources.
* You can also apply sophisticated logic to multiple conditions within a Custom Policy. Check out our [custom policy examples](../3.Custom%20Policies/Examples.md).
* After creating tests for your custom policies, you can contribute them back to Checkov! Learn how to [contibute your policies](../6.Contribution/Contribution%20Overview.md).
