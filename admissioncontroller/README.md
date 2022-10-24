# Whorf - Checkov implementation of a Kubernetes admission controller
A K8s admission controller for security and operational best practices (Based on [Checkov](https://checkov.io))

Whorf is your last line of defence against deploying vulnerable or misconfigured kubernetes objects.  

## Install
It is easily deployed by simply running the setup.sh script.  This will download the default kubernetes objects into a local bridgecrew directory.  It will customise to your local requirements and deploy into the kubernetes cluster currently in context

### Step 1:
```
curl –o setup.sh https://raw.githubusercontent.com/bridgecrewio/checkov/master/admissioncontroller/setup.sh
```

### Step 2:
```
chmod +x ./setup.sh
```
### Step 3:
Get an [API key](https://docs.bridgecrew.io/docs/get-api-token)
### Step 3:
```
./setup.sh <a unique cluster name> <bc-api-key>
```

## Uninstall
```
kubectl delete -f bridgecrew<timestamp>
```

## Customisation of Checks for Validation
After installation the check which would block a kubernetes object from being deployed are created and deployed as a kubernetes ConfigMap.

The default checks are only a small subset of the entire kubernetes range focusing only on root and privileged access and capabilities.  

These can be found in the file checkovconfig.yaml.  The default example is below where k8sac/cluster would be replaced with k8sac/'your cluster name'

```
apiVersion: v1
kind: ConfigMap
metadata:
  creationTimestamp: null
  name: checkovconfig
  namespace: bridgecrew
data:
  .checkov.yaml: |
    branch: master
    repo-id: k8sac/cluster
    download-external-modules: false
    evaluate-variables: true
    external-modules-download-path: .external_modules
    framework: kubernetes
    hard-fail-on:
    - CKV_K8S_1
    - CKV_K8S_2
    - CKV_K8S_3
    - CKV_K8S_4
    - CKV_K8S_5
    - CKV_K8S_6
    - CKV_K8S_7
    - CKV_K8S_16
    - CKV_K8S_17
    - CKV_K8S_18
    - CKV_K8S_19
    - CKV_K8S_20
    - CKV_K8S_21
    - CKV_K8S_23
    - CKV_K8S_27
    - CKV_K8S_39
    - CKV_K8S_49
    output:
    - json
```
## Ignoring critical namespaces
There is a second configMap called whorfconfig.yaml.  Within this config you'll find a property called k8s.properties where the key value pair 'ignores-namespaces' is preconfigured with the kube-system namespace and the bridgecrew namespace.  Add any other system critical namespaces to this configuration, reapply the configMap and restart Whorf to apply the new configMap settings.

_NOTE: The list does not currently accept wildcard entries such as kube-*._

E.g.
```
  # kubernetes related config
  k8s.properties: |
    ignores-namespaces=kube-system,bridgecrew