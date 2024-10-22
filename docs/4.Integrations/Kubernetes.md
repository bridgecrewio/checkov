---
layout: default
published: true
title: Kubernetes
nav_order: 5
---

# Integrate Checkov with Kubernetes

Checkov is built to scan static code and is typically used at build time.  However, resources running in a Kubernetes cluster
can be described in the same way as at build-time.  This allows Checkov to run in a cluster with read-only access and report
on the same violations.  

## Execution

To run Checkov in your cluster, you must have Kubernetes CLI access to the cluster.  

To execute a job against your cluster, run the following manifest:

```bash
kubectl apply -f https://raw.githubusercontent.com/bridgecrewio/checkov/main/kubernetes/checkov-job.yaml
```

Review the output of the job:

```bash
kubectl get jobs -n checkov
kubectl logs job/checkov -n checkov
```
