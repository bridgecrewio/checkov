---
layout: default
published: true
title: OpenAPI configuration scanning
nav_order: 20
---

# SCA scanning
Checkov is an SCA (Software Composition Analysis) tool.  This means it scans package files closed source images for Common Vulnerabilities and Exposures (CVEs).
You can [Find here](https://docs.bridgecrew.io/docs/open-source-vulnerability-scanning) the full list of Package Manager Types Supported
In order to use this feature, you first need to create an [API token using Bridgecrew](https://docs.bridgecrew.io/docs/integrations#open-the-api-token-grid)

```
### Running in CLI
TODO: FILL HERE

```bash
checkov -d . --framework openapi
```

### Example output
TODO: ADD HERE
