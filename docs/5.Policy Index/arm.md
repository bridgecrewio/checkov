---
layout: default
title: arm resource scans
nav_order: 1
---

# arm resource scans (auto generated)

|    | Id            | Type      | Entity                                                                       | Policy                                                                                        | IaC   |
|----|---------------|-----------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|-------|
|  0 | CKV_AZURE_1   | resource  | Microsoft.Compute/virtualMachines                                            | Ensure Azure Instance does not use basic authentication(Use SSH Key Instead)                  | arm   |
|  1 | CKV_AZURE_2   | resource  | Microsoft.Compute/disks                                                      | Ensure Azure managed disk have encryption enabled                                             | arm   |
|  2 | CKV_AZURE_3   | resource  | Microsoft.Storage/storageAccounts                                            | Ensure that 'supportsHttpsTrafficOnly' is set to 'true'                                       | arm   |
|  3 | CKV_AZURE_4   | resource  | Microsoft.ContainerService/managedClusters                                   | Ensure AKS logging to Azure Monitoring is Configured                                          | arm   |
|  4 | CKV_AZURE_5   | resource  | Microsoft.ContainerService/managedClusters                                   | Ensure RBAC is enabled on AKS clusters                                                        | arm   |
|  5 | CKV_AZURE_6   | resource  | Microsoft.ContainerService/managedClusters                                   | Ensure AKS has an API Server Authorized IP Ranges enabled                                     | arm   |
|  6 | CKV_AZURE_7   | resource  | Microsoft.ContainerService/managedClusters                                   | Ensure AKS cluster has Network Policy configured                                              | arm   |
|  7 | CKV_AZURE_8   | resource  | Microsoft.ContainerService/managedClusters                                   | Ensure Kubernetes Dashboard is disabled                                                       | arm   |
|  8 | CKV_AZURE_9   | resource  | Microsoft.Network/networkSecurityGroups                                      | Ensure that RDP access is restricted from the internet                                        | arm   |
|  9 | CKV_AZURE_9   | resource  | Microsoft.Network/networkSecurityGroups/securityRules                        | Ensure that RDP access is restricted from the internet                                        | arm   |
| 10 | CKV_AZURE_10  | resource  | Microsoft.Network/networkSecurityGroups                                      | Ensure that SSH access is restricted from the internet                                        | arm   |
| 11 | CKV_AZURE_10  | resource  | Microsoft.Network/networkSecurityGroups/securityRules                        | Ensure that SSH access is restricted from the internet                                        | arm   |
| 12 | CKV_AZURE_11  | resource  | Microsoft.Sql/servers                                                        | Ensure no SQL Databases allow ingress from 0.0.0.0/0 (ANY IP)                                 | arm   |
| 13 | CKV_AZURE_12  | resource  | Microsoft.Network/networkWatchers/FlowLogs                                   | Ensure that Network Security Group Flow Log retention period is 'greater than 90 days'        | arm   |
| 14 | CKV_AZURE_12  | resource  | Microsoft.Network/networkWatchers/FlowLogs/                                  | Ensure that Network Security Group Flow Log retention period is 'greater than 90 days'        | arm   |
| 15 | CKV_AZURE_12  | resource  | Microsoft.Network/networkWatchers/flowLogs                                   | Ensure that Network Security Group Flow Log retention period is 'greater than 90 days'        | arm   |
| 16 | CKV_AZURE_12  | resource  | Microsoft.Network/networkWatchers/flowLogs/                                  | Ensure that Network Security Group Flow Log retention period is 'greater than 90 days'        | arm   |
| 17 | CKV_AZURE_13  | resource  | Microsoft.Web/sites/config                                                   | Ensure App Service Authentication is set on Azure App Service                                 | arm   |
| 18 | CKV_AZURE_13  | resource  | config                                                                       | Ensure App Service Authentication is set on Azure App Service                                 | arm   |
| 19 | CKV_AZURE_14  | resource  | Microsoft.Web/sites                                                          | Ensure web app redirects all HTTP traffic to HTTPS in Azure App Service                       | arm   |
| 20 | CKV_AZURE_15  | resource  | Microsoft.Web/sites                                                          | Ensure web app is using the latest version of TLS encryption                                  | arm   |
| 21 | CKV_AZURE_16  | resource  | Microsoft.Web/sites                                                          | Ensure that Register with Azure Active Directory is enabled on App Service                    | arm   |
| 22 | CKV_AZURE_17  | resource  | Microsoft.Web/sites                                                          | Ensure the web app has 'Client Certificates (Incoming client certificates)' set               | arm   |
| 23 | CKV_AZURE_18  | resource  | Microsoft.Web/sites                                                          | Ensure that 'HTTP Version' is the latest if used to run the web app                           | arm   |
| 24 | CKV_AZURE_19  | resource  | Microsoft.Security/pricings                                                  | Ensure that standard pricing tier is selected                                                 | arm   |
| 25 | CKV_AZURE_20  | resource  | Microsoft.Security/securityContacts                                          | Ensure that security contact 'Phone number' is set                                            | arm   |
| 26 | CKV_AZURE_21  | resource  | Microsoft.Security/securityContacts                                          | Ensure that 'Send email notification for high severity alerts' is set to 'On'                 | arm   |
| 27 | CKV_AZURE_22  | resource  | Microsoft.Security/securityContacts                                          | Ensure that 'Send email notification for high severity alerts' is set to 'On'                 | arm   |
| 28 | CKV_AZURE_23  | resource  | Microsoft.Sql/servers                                                        | Ensure that 'Auditing' is set to 'Enabled' for SQL servers                                    | arm   |
| 29 | CKV_AZURE_24  | resource  | Microsoft.Sql/servers                                                        | Ensure that 'Auditing' Retention is 'greater than 90 days' for SQL servers                    | arm   |
| 30 | CKV_AZURE_25  | resource  | Microsoft.Sql/servers/databases                                              | Ensure that 'Threat Detection types' is set to 'All'                                          | arm   |
| 31 | CKV_AZURE_26  | resource  | Microsoft.Sql/servers/databases                                              | Ensure that 'Send Alerts To' is enabled for MSSQL servers                                     | arm   |
| 32 | CKV_AZURE_27  | resource  | Microsoft.Sql/servers/databases                                              | Ensure that 'Email service and co-administrators' is 'Enabled' for MSSQL servers              | arm   |
| 33 | CKV_AZURE_28  | resource  | Microsoft.DBforMySQL/servers                                                 | Ensure 'Enforce SSL connection' is set to 'ENABLED' for MySQL Database Server                 | arm   |
| 34 | CKV_AZURE_29  | resource  | Microsoft.DBforPostgreSQL/servers                                            | Ensure 'Enforce SSL connection' is set to 'ENABLED' for PostgreSQL Database Server            | arm   |
| 35 | CKV_AZURE_30  | resource  | Microsoft.DBforPostgreSQL/servers/configurations                             | Ensure server parameter 'log_checkpoints' is set to 'ON' for PostgreSQL Database Server       | arm   |
| 36 | CKV_AZURE_30  | resource  | configurations                                                               | Ensure server parameter 'log_checkpoints' is set to 'ON' for PostgreSQL Database Server       | arm   |
| 37 | CKV_AZURE_31  | resource  | Microsoft.DBforPostgreSQL/servers/configurations                             | Ensure configuration 'log_connections' is set to 'ON' for PostgreSQL Database Server          | arm   |
| 38 | CKV_AZURE_31  | resource  | configurations                                                               | Ensure configuration 'log_connections' is set to 'ON' for PostgreSQL Database Server          | arm   |
| 39 | CKV_AZURE_32  | resource  | Microsoft.DBforPostgreSQL/servers/configurations                             | Ensure server parameter 'connection_throttling' is set to 'ON' for PostgreSQL Database Server | arm   |
| 40 | CKV_AZURE_32  | resource  | configurations                                                               | Ensure server parameter 'connection_throttling' is set to 'ON' for PostgreSQL Database Server | arm   |
| 41 | CKV_AZURE_33  | resource  | Microsoft.Storage/storageAccounts/queueServices/providers/diagnosticsettings | Ensure Storage logging is enabled for Queue service for read, write and delete requests       | arm   |
| 42 | CKV_AZURE_34  | resource  | Microsoft.Storage/storageAccounts/blobServices/containers                    | Ensure that 'Public access level' is set to Private for blob containers                       | arm   |
| 43 | CKV_AZURE_34  | resource  | blobServices/containers                                                      | Ensure that 'Public access level' is set to Private for blob containers                       | arm   |
| 44 | CKV_AZURE_34  | resource  | containers                                                                   | Ensure that 'Public access level' is set to Private for blob containers                       | arm   |
| 45 | CKV_AZURE_35  | resource  | Microsoft.Storage/storageAccounts                                            | Ensure default network access rule for Storage Accounts is set to deny                        | arm   |
| 46 | CKV_AZURE_36  | resource  | Microsoft.Storage/storageAccounts                                            | Ensure 'Trusted Microsoft Services' is enabled for Storage Account access                     | arm   |
| 47 | CKV_AZURE_37  | resource  | microsoft.insights/logprofiles                                               | Ensure that Activity Log Retention is set 365 days or greater                                 | arm   |
| 48 | CKV_AZURE_38  | resource  | microsoft.insights/logprofiles                                               | Ensure audit profile captures all the activities                                              | arm   |
| 49 | CKV_AZURE_39  | resource  | Microsoft.Authorization/roleDefinitions                                      | Ensure that no custom subscription owner roles are created                                    | arm   |
| 50 | CKV_AZURE_41  | resource  | Microsoft.KeyVault/vaults/secrets                                            | Ensure that the expiration date is set on all secrets                                         | arm   |
| 51 | CKV_AZURE_42  | resource  | Microsoft.KeyVault/vaults                                                    | Ensure the key vault is recoverable                                                           | arm   |
| 52 | CKV_AZURE_47  | resource  | Microsoft.DBforMariaDB/servers                                               | Ensure 'Enforce SSL connection' is set to 'ENABLED' for MariaDB servers                       | arm   |
| 53 | CKV_AZURE_49  | resource  | Microsoft.Compute/virtualMachineScaleSets                                    | Ensure Azure linux scale set does not use basic authentication(Use SSH Key Instead)           | arm   |
| 54 | CKV_AZURE_131 | parameter | secureString                                                                 | SecureString parameter should not have hardcoded default values                               | arm   |
| 55 | CKV_AZURE_132 | resource  | Microsoft.DocumentDB/databaseAccounts                                        | Ensure cosmosdb does not allow privileged escalation by restricting management plane changes  | arm   |


---


