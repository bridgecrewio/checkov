---
layout: default
published: true
title: Azure Bicep configuration scanning
nav_order: 20
---

# Azure Bicep configuration scanning
Checkov supports the evaluation of policies on your Bicep files.
When using checkov to scan a directory that contains a Bicep file it will validate if it is compliant with Azure best practices such as having logging and auditing enabled, Ensure that 'Public access level' is set to Private for blob containers, Ensure no SQL Databases allow ingress from 0.0.0.0/0 (ANY IP), and more.  

Full list of ARM templates policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/arm.html).

### Example misconfigured Bicep file

```bicep
@description('The location in which all resources should be deployed.')
param location string = resourceGroup().location

@description('The name of the app to create.')
param appName string = uniqueString(resourceGroup().id)

var appServicePlanName = '${appName}${uniqueString(subscription().subscriptionId)}'
var appServicePlanSku = 'S1'

resource appServicePlan 'Microsoft.Web/serverfarms@2020-06-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: appServicePlanSku
  }
  kind: 'app'
}

resource webApp 'Microsoft.Web/sites@2020-06-01' = {
  name: appName
  location: location
  kind: 'app'
  properties: {
    serverFarmId: appServicePlan.id
  }
}
```
### Running in CLI

```bash
checkov -d . --framework bicep
```

### Example output

```bash
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x 

bicep scan results:

Passed checks: 0, Failed checks: 5, Skipped checks: 0

Check: CKV_AZURE_15: "Ensure web app is using the latest version of TLS encryption"
        FAILED for resource: Microsoft.Web/sites.webApp
        File: anton/bicep/playground/example.bicep:19-26
        Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-networking-policies/bc-azr-networking-6

                19 | resource webApp 'Microsoft.Web/sites@2020-06-01' = {
                20 |   name: appName
                21 |   location: location
                22 |   kind: 'app'
                23 |   properties: {
                24 |     serverFarmId: appServicePlan.id
                25 |   }
                26 | }

Check: CKV_AZURE_17: "Ensure the web app has 'Client Certificates (Incoming client certificates)' set"
        FAILED for resource: Microsoft.Web/sites.webApp
        File: anton/bicep/playground/example.bicep:19-26
        Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-networking-policies/bc-azr-networking-7

                19 | resource webApp 'Microsoft.Web/sites@2020-06-01' = {
                20 |   name: appName
                21 |   location: location
                22 |   kind: 'app'
                23 |   properties: {
                24 |     serverFarmId: appServicePlan.id
                25 |   }
                26 | }

Check: CKV_AZURE_14: "Ensure web app redirects all HTTP traffic to HTTPS in Azure App Service"
        FAILED for resource: Microsoft.Web/sites.webApp
        File: anton/bicep/playground/example.bicep:19-26
        Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-networking-policies/bc-azr-networking-5

                19 | resource webApp 'Microsoft.Web/sites@2020-06-01' = {
                20 |   name: appName
                21 |   location: location
                22 |   kind: 'app'
                23 |   properties: {
                24 |     serverFarmId: appServicePlan.id
                25 |   }
                26 | }

Check: CKV_AZURE_16: "Ensure that Register with Azure Active Directory is enabled on App Service"
        FAILED for resource: Microsoft.Web/sites.webApp
        File: anton/bicep/playground/example.bicep:19-26
        Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-iam-policies/bc-azr-iam-1

                19 | resource webApp 'Microsoft.Web/sites@2020-06-01' = {
                20 |   name: appName
                21 |   location: location
                22 |   kind: 'app'
                23 |   properties: {
                24 |     serverFarmId: appServicePlan.id
                25 |   }
                26 | }

Check: CKV_AZURE_18: "Ensure that 'HTTP Version' is the latest if used to run the web app"
        FAILED for resource: Microsoft.Web/sites.webApp
        File: anton/bicep/playground/example.bicep:19-26
        Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-networking-policies/bc-azr-networking-8

                19 | resource webApp 'Microsoft.Web/sites@2020-06-01' = {
                20 |   name: appName
                21 |   location: location
                22 |   kind: 'app'
                23 |   properties: {
                24 |     serverFarmId: appServicePlan.id
                25 |   }
                26 | }
```
