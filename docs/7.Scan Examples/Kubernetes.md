---
layout: default
published: true
title: Kubernetes configuration scanning
nav_order: 20
---

# Kubernetes configuration scanning
Checkov supports the evaluation of policies on your Kubernetes files.
When using checkov to scan a directory that contains a Kubernetes manifests it will validate if the file is compliant with K8 best practices such as not admitting root containers, making sure there are CPU limits, and more.  

Full list of Kubernetes policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/kubernetes.html).

### Example misconfigured kubernetes

```yaml
# runAsNonRoot and runAsUser not set (pod or container)
apiVersion: v1
kind: Pod
metadata:
  name: pod1
spec:
  containers:
  - name: main
    image: alpine
    command: ["/bin/sleep", "999999"]

```
### Running in CLI

```bash
checkov -d . --framework kubernetes
```

### Example output
```bash
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x 

Passed checks: 70, Failed checks: 19, Skipped checks: 0

Check: CKV_K8S_37: "Minimize the admission of containers with capabilities assigned"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc-k8s-34

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_31: "Ensure that the seccomp profile is set to docker/default or runtime/default"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc-k8s-29

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_8: "Liveness Probe Should be Configured"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc-k8s-7

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_12: "Memory requests should be set"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc-k8s-11

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_20: "Containers should not run with allowPrivilegeEscalation"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc-k8s-19

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_13: "Memory limits should be set"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc-k8s-12

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_40: "Containers should run as a high UID to avoid host conflict"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc-k8s-37

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_10: "CPU requests should be set"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc-k8s-9

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_22: "Use read-only filesystem for containers where possible"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_21

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_9: "Readiness Probe Should be Configured"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_8

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_28: "Minimize the admission of containers with the NET_RAW capability"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_27

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_29: "Apply security context to your pods and containers"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_28

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_30: "Apply security context to your pods and containers"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_28

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_14: "Image Tag should be fixed - not latest or blank"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_13

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_38: "Ensure that Service Account Tokens are only mounted where necessary"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_35

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_21: "The default namespace should not be used"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_20

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_23: "Minimize the admission of root containers"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_22

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_43: "Image should use digest"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_39

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]


Check: CKV_K8S_11: "CPU limits should be set"
	FAILED for resource: Pod.default.pod1
	File: /rootContainersFAILED.yaml:2-10
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc_k8s_10

		2  | apiVersion: v1
		3  | kind: Pod
		4  | metadata:
		5  |   name: pod1
		6  | spec:
		7  |   containers:
		8  |   - name: main
		9  |     image: alpine
		10 |     command: ["/bin/sleep", "999999"]

```
