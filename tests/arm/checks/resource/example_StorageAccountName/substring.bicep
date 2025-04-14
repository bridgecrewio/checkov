@description('Name of the environment')
param environmentName string

@description('Name of the Storage account')
param storageAccountName string = substring('abcdefgh${environmentName}${uniqueString(resourceGroup().id)}', 0, 24)

@description('Provide a location for the resources.')
param location string = resourceGroup().location

resource dataStorageAccount 'Microsoft.Storage/storageAccounts@2021-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    allowCrossTenantReplication: false
    isHnsEnabled: true
    allowedCopyScope: 'AAD'
    defaultToOAuthAuthentication: false
    encryption: {
      keySource: 'Microsoft.Storage'
      requireInfrastructureEncryption: false
      services: {
        blob: {
          enabled: true
          keyType: 'Account'
        }
      }
    }
    minimumTlsVersion: 'TLS1_2'
    largeFileSharesState: 'Disabled'
    sasPolicy: {
      expirationAction: 'Log'
      sasExpirationPeriod: '00.00:10:00'
    }
    supportsHttpsTrafficOnly: true
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
  }
}
