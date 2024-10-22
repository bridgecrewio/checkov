---
layout: default
published: true
title: Azure ARM templates configuration scanning
nav_order: 20
---

# Azure ARM templates configuration scanning
Checkov supports the evaluation of policies on your ARM templates files.
When using checkov to scan a directory that contains a ARM template it will validate if the file is compliant with Azure best practices such as having logging and auditing enabled, Ensure that 'Public access level' is set to Private for blob containers, Ensure no SQL Databases allow ingress from 0.0.0.0/0 (ANY IP), and more.  

Full list of ARM templates policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/arm.html).

### Example misconfigured ARM templates

```json
{
   "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
   "contentVersion": "1.0.0.0",
   "parameters": {
     "webAppName": {
       "type": "string",
       "defaultValue" : "AzureLinuxApp",
       "metadata": {
         "description": "Base name of the resource such as web app name and app service plan "
       },
       "minLength": 2
     },
     "sku":{
       "type": "string",
       "defaultValue" : "S1",
       "metadata": {
         "description": "The SKU of App Service Plan "
       }
     },
     "linuxFxVersion" : {
       "type": "string",
       "defaultValue" : "php|7.0",
       "metadata": {
         "description": "The Runtime stack of current web app"
       }
     },
     "location": {
       "type": "string",
       "defaultValue": "[resourceGroup().location]",
       "metadata": {
         "description": "Location for all resources."
       }
     }
   },
   "variables": {
     "webAppPortalName": "[concat(parameters('webAppName'), '-webapp')]",
     "appServicePlanName": "[concat('AppServicePlan-', parameters('webAppName'))]"
   },
   "resources": [
     {
       "type": "Microsoft.Web/serverfarms",
       "apiVersion": "2018-02-01",
       "name": "[variables('appServicePlanName')]",
       "location": "[parameters('location')]",
       "sku": {
         "name": "[parameters('sku')]"
       },
       "kind": "linux",
       "properties":{
         "reserved":true
       }
     },
     {
       "type": "Microsoft.Web/sites",
       "apiVersion": "2018-11-01",
       "name": "[variables('webAppPortalName')]",
       "location": "[parameters('location')]",
       "kind": "app",
       "dependsOn": [
         "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]"
       ],
       "properties": {
         "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]",
         "siteConfig": {
           "linuxFxVersion": "[parameters('linuxFxVersion')]"
         }
       }
     }
   ]
 }


```
### Running in CLI

```bash
checkov -d . --framework arm
```

### Example output

```bash
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x 

arm scan results:

Passed checks: 0, Failed checks: 5, Skipped checks: 0

Check: CKV_AZURE_15: "Ensure web app is using the latest version of TLS encryption"
	FAILED for resource: Microsoft.Web/sites.[concat(parameters('webAppName'), '-webapp')]
	File: /example.json:53-68
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-networking-policies/bc-azr-networking-6

		53 |     {
		54 |       "type": "Microsoft.Web/sites",
		55 |       "apiVersion": "2018-11-01",
		56 |       "name": "[variables('webAppPortalName')]",
		57 |       "location": "[parameters('location')]",
		58 |       "kind": "app",
		59 |       "dependsOn": [
		60 |         "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]"
		61 |       ],
		62 |       "properties": {
		63 |         "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]",
		64 |         "siteConfig": {
		65 |           "linuxFxVersion": "[parameters('linuxFxVersion')]"
		66 |         }
		67 |       }
		68 |     }


Check: CKV_AZURE_17: "Ensure the web app has 'Client Certificates (Incoming client certificates)' set"
	FAILED for resource: Microsoft.Web/sites.[concat(parameters('webAppName'), '-webapp')]
	File: /example.json:53-68
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-networking-policies/bc-azr-networking-7

		53 |     {
		54 |       "type": "Microsoft.Web/sites",
		55 |       "apiVersion": "2018-11-01",
		56 |       "name": "[variables('webAppPortalName')]",
		57 |       "location": "[parameters('location')]",
		58 |       "kind": "app",
		59 |       "dependsOn": [
		60 |         "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]"
		61 |       ],
		62 |       "properties": {
		63 |         "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]",
		64 |         "siteConfig": {
		65 |           "linuxFxVersion": "[parameters('linuxFxVersion')]"
		66 |         }
		67 |       }
		68 |     }


Check: CKV_AZURE_14: "Ensure web app redirects all HTTP traffic to HTTPS in Azure App Service"
	FAILED for resource: Microsoft.Web/sites.[concat(parameters('webAppName'), '-webapp')]
	File: /example.json:53-68
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-networking-policies/bc-azr-networking-5

		53 |     {
		54 |       "type": "Microsoft.Web/sites",
		55 |       "apiVersion": "2018-11-01",
		56 |       "name": "[variables('webAppPortalName')]",
		57 |       "location": "[parameters('location')]",
		58 |       "kind": "app",
		59 |       "dependsOn": [
		60 |         "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]"
		61 |       ],
		62 |       "properties": {
		63 |         "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]",
		64 |         "siteConfig": {
		65 |           "linuxFxVersion": "[parameters('linuxFxVersion')]"
		66 |         }
		67 |       }
		68 |     }


Check: CKV_AZURE_16: "Ensure that Register with Azure Active Directory is enabled on App Service"
	FAILED for resource: Microsoft.Web/sites.[concat(parameters('webAppName'), '-webapp')]
	File: /example.json:53-68
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-iam-policies/bc-azr-iam-1

		53 |     {
		54 |       "type": "Microsoft.Web/sites",
		55 |       "apiVersion": "2018-11-01",
		56 |       "name": "[variables('webAppPortalName')]",
		57 |       "location": "[parameters('location')]",
		58 |       "kind": "app",
		59 |       "dependsOn": [
		60 |         "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]"
		61 |       ],
		62 |       "properties": {
		63 |         "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]",
		64 |         "siteConfig": {
		65 |           "linuxFxVersion": "[parameters('linuxFxVersion')]"
		66 |         }
		67 |       }
		68 |     }


Check: CKV_AZURE_18: "Ensure that 'HTTP Version' is the latest if used to run the web app"
	FAILED for resource: Microsoft.Web/sites.[concat(parameters('webAppName'), '-webapp')]
	File: /example.json:53-68
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/azure-policies/azure-networking-policies/bc-azr-networking-8

		53 |     {
		54 |       "type": "Microsoft.Web/sites",
		55 |       "apiVersion": "2018-11-01",
		56 |       "name": "[variables('webAppPortalName')]",
		57 |       "location": "[parameters('location')]",
		58 |       "kind": "app",
		59 |       "dependsOn": [
		60 |         "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]"
		61 |       ],
		62 |       "properties": {
		63 |         "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]",
		64 |         "siteConfig": {
		65 |           "linuxFxVersion": "[parameters('linuxFxVersion')]"
		66 |         }
		67 |       }
		68 |     }


```
