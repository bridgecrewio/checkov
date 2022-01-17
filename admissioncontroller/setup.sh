#!/usr/bin/env bash
# setup.sh
#
# Sets up the files required to deploy the Bridgecrew Checkov admission controller in a cluster

set -euo pipefail

date=$(date '+%Y%m%d%H%M%S')
echo $date

codedir=bridgecrew$date
mkdir $codedir
k8sdir="$(dirname "$0")/${codedir}"
certdir="$(mktemp -d)"

# Get the files we need
deployment=https://raw.githubusercontent.com/eurogig/whorf/main/k8s/deployment.yaml
configmap=https://raw.githubusercontent.com/eurogig/whorf/main/k8s/checkovconfig.yaml
admissionregistration=https://raw.githubusercontent.com/eurogig/whorf/main/k8s/admissionconfiguration.yaml
service=https://raw.githubusercontent.com/eurogig/whorf/main/k8s/service.yaml

curl -o $k8sdir/deployment.yaml $deployment
curl -o $k8sdir/service.yaml $service
# Pop these into the temp directory as we'll make some customisations pipe in into the k8s dir
curl -o $certdir/checkovconfig.yaml $configmap
curl -o $certdir/admissionconfiguration.yaml $admissionregistration

# the namespace
ns=bridgecrew
kubectl create ns $ns --dry-run=client -o yaml > $k8sdir/namespace.yaml

# the cluster (repository name)
cluster=$1
# the bridgecrew platform api key 
bcapikey=$2

# Generate keys into a temporary directory.
echo "Generating TLS certs ..."
/usr/local/opt/openssl/bin/openssl req -x509 -sha256 -newkey rsa:2048 -keyout $certdir/webhook.key -out $certdir/webhook.crt -days 1024 -nodes -addext "subjectAltName = DNS.1:validate.$ns.svc"

kubectl create secret generic admission-tls -n bridgecrew --type=Opaque --from-file=$certdir/webhook.key --from-file=$certdir/webhook.crt --dry-run=client -o yaml > $k8sdir/secret.yaml

kubectl create secret generic bridgecrew-secret \
   --from-literal=credentials=$bcapikey -n bridgecrew --dry-run=client -o yaml > $k8sdir/secret-apikey.yaml

# Create the `bridgecrew` namespace.
echo "Creating Kubernetes objects ..."

# Read the PEM-encoded CA certificate, base64 encode it, and replace the `${CA_PEM_B64}` placeholder in the YAML
# template with it. Then, create the Kubernetes resources.
ca_pem_b64="$(openssl base64 -A <"${certdir}/webhook.crt")"
sed -e 's@${CA_PEM_B64}@'"$ca_pem_b64"'@g' "${certdir}/admissionconfiguration.yaml"  > "${k8sdir}/admissionconfiguration.yaml"

# Change the cluster in the checkovconfig to our cluster name
sed -e 's@cluster@'"$cluster"'@g' "${certdir}/checkovconfig.yaml"  > "${k8sdir}/checkovconfig.yaml"

# Apply everything in the bridgecrew directory in the correct order
kubectl apply -f $k8sdir/namespace.yaml 
kubectl apply -f $k8sdir/secret-apikey.yaml
kubectl apply -f $k8sdir/secret.yaml
kubectl apply -f $k8sdir/checkovconfig.yaml
kubectl apply -f $k8sdir/service.yaml
kubectl apply -f $k8sdir/deployment.yaml
kubectl apply -f $k8sdir/admissionconfiguration.yaml

# Delete the key directory to prevent abuse (DO NOT USE THESE KEYS ANYWHERE ELSE).
rm -rf "$certdir"

# Wait for the deployment to be available
echo "Waiting for deployment to be Ready..."
kubectl wait --for=condition=Available deployment/validation-webhook -n bridgecrew
echo "The webhook server has been deployed and configured!"
