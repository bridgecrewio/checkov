# Checkov Runtime

Checkov is an infrastructure as code scanning tool which provides static code analysis for 
infrastructure prior to deploying.  Since Kubernetes resources can be defined as code in runtime, 
Checkov can be used for scanning in runtime.  A caveat to this is that typically checkov reports on the file 
that is not compliant, but in runtime there is no concept of files. 

## Usage

Checkov is deployed into a Kubernetes cluster as a Cron Job (or standalone Job for one-time use).  Using a Bridgecrew 
API key the results can be forwarded to the Bridgecrew platform where you can compare with build time violations.  

The first step is to create a secret for your Bridgecrew api key.  Skip this step if you're not integrating with Bridgecrew.

Replace `<my_api_key>` below with your key from Bridgecrew.  
Also replace `<my_cluster_name>` with the name of your cluster so it shows up in the platform.  
```$xslt  
kubectl create ns checkov 
kubectl create secret generic checkov-rt-secret --from-literal=apikey=<my_api_key> \
        --from-literal=repoid='runtime/<my_cluster_name>' -n checkov
```

Next deploy the cron job using the provided manifest with runs once per hour

```$xslt
kubectl apply -f checkov-cronjob.yaml

# Alternatively if you want to see the output immediately:
# kubectl apply -f checkov-job.yaml
```

Review the output in the Bridgecrew console or directly from the logs 

```$xslt
kubectl get jobs -n checkov
kubectl logs job/checkov -n checkov
```