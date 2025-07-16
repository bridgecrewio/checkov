---
layout: default
published: true
title: Helm
nav_order: 9
---

# Scan Helm charts with Checkov

Checkov is able to autodetect helm charts by the presence of a `Chart.yaml` file, if found, the helm framework will automatically be used to template out the helm chart (with it's default values) into resulting Kubernetes manifests, which will then be scanned by all Checkovs' Kubernetes policies.


```
       _               _
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V /
  \___|_| |_|\___|\___|_|\_\___/ \_/

By Prisma Cloud | version: x.x.x 

helm scan results:

Passed checks: 370, Failed checks: 90, Skipped checks: 0

Check: CKV_K8S_27: "Do not expose the docker daemon socket to containers"
	PASSED for resource: Deployment.RELEASE-NAME-nextcloud.default
	File: /nextcloud/templates/deployment.yaml:3-107
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/kubernetes-policies/kubernetes-policy-index/bc-k8s-26


...
```

To do this, we use the helm binary, if the helm binary (v3) is not available via the users `$PATH` for Checkov, Checkov will automatically skip the helm framework, with a message informing the user as below. Checkov will then run with exactly the same behaviour as if running with `checkov --skip-framework helm`.

```
The following frameworks will automatically be disabled due to missing system dependencies: helm
```

This auto-detection behaviour is to protect existing CI pipelines which pull the latest version of Checkov, which may not have the helm binary available.

If you have custom value files, and scanning a Chart (a directory containing a `Chart.yaml` file), you can tell checkov to use your values while creating the kubernetes manifests from the chart, to do this, use the following (for example, scanning a gocd chart directory):

```
checkov -d ./testdir/gocd --framework helm --var-file ./testdir/gocd.yaml
```

in the example below, we can see the difference between the default `gocd` version `1.39.4` Helm chart scan, compared to a scan using the following `gocd.yaml` variables file:


```
checkov -d ./testdir/gocd --framework helm --quiet --compact -c CKV_K8S_15

helm scan results:

Passed checks: 0, Failed checks: 3, Skipped checks: 0

Check: CKV_K8S_15: "Image Pull Policy should be Always"
        FAILED for resource: Deployment.default.RELEASE-NAME-gocd-agent
        File: /gocd/templates/gocd-agent-deployment.yaml:3-46

Check: CKV_K8S_15: "Image Pull Policy should be Always"
        FAILED for resource: Deployment.default.RELEASE-NAME-gocd-server
        File: /gocd/templates/gocd-server-deployment.yaml:3-90

Check: CKV_K8S_15: "Image Pull Policy should be Always"
        FAILED for resource: Pod.default.RELEASE-NAME-gocd-test-ku4xn
        File: /gocd/templates/tests/gocd-test.yaml:3-44
```


```
checkov -d ./testdir/gocd --framework helm --quiet --compact --var-file ./testdir/gocd.yaml -c CKV_K8S_15

helm scan results:

Passed checks: 2, Failed checks: 1, Skipped checks: 0

Check: CKV_K8S_15: "Image Pull Policy should be Always"
        FAILED for resource: Pod.default.RELEASE-NAME-gocd-test-o6jdi
        File: /gocd/templates/tests/gocd-test.yaml:3-44

```


# Third party Helm charts
## Scan Helm values.yaml files without a locally developed chart with Checkov

If you are consuming third party charts, it is unlikely you will have a `Chart.yaml` file for Checkov to auto-detect.

For example, you may have run: 

```
helm repo add gocd https://gocd.github.io/helm-chart
helm inspect values gocd/gocd > gocd.yaml
```

Then edited your custom values in `gocd.yaml` to suit your deployment needs.

In this case, you can use your custom values from your values file (`gocd.yml` in this case) to generate kubernetes output with Helm, and pass the templated output to checkov to receive the same policy information. This would also be trivial to set up in CI for automated scanning of this scenario:

```
helm template gocd/gocd -f gocd.yaml > k8s-template.yaml
checkov -f k8s-template.yaml --framework kubernetes --skip-check CKV_K8S_21
```

Note we skip check `CKV_K8S_21` for this process, which alerts on default namespace usage within Kubernetes manifests. 
Since helm manages our namespaces, we always skip this internally when using the helm framework, so we want to replicate the same behaviour here.

