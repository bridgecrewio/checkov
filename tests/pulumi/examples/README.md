# Pulumi examples

Each directory contains a Pulumi YAML program and the equivalent Terraform configuration,
which are used to compare the results of both frameworks.

The aws and gcp previews don't need cloud credentials. The azure provider needs an Azure CLI login
(`azure:useCli true`), the preview and plan are read-only. Replace the subscription and tenant IDs with zeros afterwards.

```shell
export PULUMI_BACKEND_URL=file://$(mktemp -d) PULUMI_CONFIG_PASSPHRASE=test

# aws
export AWS_ACCESS_KEY_ID=AKIAFAKE AWS_SECRET_ACCESS_KEY=fake
pulumi stack init dev
pulumi config set aws:region us-east-1
pulumi config set aws:skipCredentialsValidation true
pulumi config set aws:skipRequestingAccountId true
pulumi config set aws:skipMetadataApiCheck true

# gcp
pulumi stack init dev
pulumi config set gcp:project fake-project
pulumi config set gcp:region us-central1
pulumi config set gcp:accessToken fake-token --secret

# azure
pulumi stack init dev
pulumi config set azure:subscriptionId <subscription-id>
pulumi config set azure:resourceProviderRegistrations none
pulumi config set azure:useCli true

pulumi preview --json > preview.json
PULUMI_ENABLE_STREAMING_JSON_PREVIEW=true pulumi preview --json > preview_events.jsonl

# the aws Lambda function needs the zipped code
(cd app && zip ../app.zip index.py)
terraform init
terraform plan -refresh=false -out=tfplan.bin
terraform show -json tfplan.bin | python -m json.tool > tfplan.json
```
