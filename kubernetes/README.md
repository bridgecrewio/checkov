# Checkov Runtime

Checkov is an infrastructure as code scanning tool which provides static code analysis for 
infrastructure prior to deploying.  Since Kubernetes resources can be defined as code in runtime, 
Checkov can be used for scanning in runtime.  A caveat to this is that typically checkov reports on the file 
that is not compliant, but in runtime there is no concept of files. 

## Usage

Checkov can be deployed in Kubernetes as a Job to get immediate feedback on the state of resources in your cluster. 

```$xslt
kubectl apply -f https://raw.githubusercontent.com/bridgecrewio/checkov/main/kubernetes/checkov-job.yaml
```

Review the output of the job.  

```$xslt
kubectl get jobs -n checkov
kubectl logs job/checkov -n checkov
```