#!/bin/sh
################################################################################
# Download all Kubernetes resources and run checkov against them
################################################################################

# kubectl api-resources --verbs=list --namespaced -o name  | xargs -n1 -I{} bash -c "kubectl get {} --all-namespaces -oyaml && echo ---"
RESOURCES="clusterroles
clusterrolebindings
configmaps
cronjobs
daemonsets
deployments
endpoints
horizontalpodautoscalers
ingresses
jobs
limitranges
networkpolicies
poddisruptionbudgets
pods
podsecuritypolicies
replicasets
replicationcontrollers
resourcequotas
roles
rolebindings
serviceaccounts
services
statefulsets"

for resource in $RESOURCES;
do
  kubectl get $resource --all-namespaces -oyaml | yq eval 'del(.items[] | select(.metadata.ownerReferences)) ' -  > /data/runtime.${resource}.yaml
done

if [ -f /etc/checkov/apikey ]; then
  apikey=$(cat /etc/checkov/apikey)
  if [ -f /etc/checkov/repoid ]; then
    repoid=$(cat /etc/checkov/repoid)
  else
    repoid="runtime/unknown"
  fi

  checkov -s -d /data --bc-api-key "$apikey" --repo-id "$repoid" --branch runtime --framework kubernetes "$@"
else
  checkov -s -d /data --framework kubernetes "$@"
fi

