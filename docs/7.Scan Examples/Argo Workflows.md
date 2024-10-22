---
layout: default
published: true
title: Argo Workflows configuration scanning
nav_order: 20
---

# Argo Workflows configuration scanning
Checkov supports the evaluation of policies on your Argo Workflows files.
When using checkov to scan a directory that contains Argo Workflows specs and templates it will validate if the file is compliant with Argo Workflows best practices such as usage of securityContext and non default serviceAccountName, and more.  

Full list of Argo Workflows policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/argo_workflows.html).

### Example misconfigured Argo Workflows template

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  entrypoint: whalesay
  serviceAccountName: custom-sa
  templates:
  - name: whalesay
    container:
      image: docker/whalesay:latest
      command: [cowsay]
      args: ["hello world"]
```
### Running in CLI

```bash
checkov -d . --framework argo_workflows
```

### Example output
```bash
 
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: 2.0.1210


argo_workflows scan results:

Passed checks: 1, Failed checks: 1, Skipped checks: 0

Check: CKV_ARGO_1: "Ensure Workflow pods are not using the default ServiceAccount"
        PASSED for resource: /hello_world.yaml.spec.spec.CKV_ARGO_1[6:14]
        File: /hello_world.yaml:6-15
Check: CKV_ARGO_2: "Ensure Workflow pods are running as non-root user"
        FAILED for resource: /hello_world.yaml.spec.spec.CKV_ARGO_2[6:14]
        File: /hello_world.yaml:6-15

                6  |   entrypoint: whalesay
                7  |   serviceAccountName: custom-sa
                8  |   templates:
                9  |   - name: whalesay
                10 |     container:
                11 |       image: docker/whalesay:latest
                12 |       command: [cowsay]
                13 |       args: ["hello world"]


```
