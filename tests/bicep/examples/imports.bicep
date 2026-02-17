// Test file for Bicep import statement support
import { storageAccountType } from './types.bicep'
import { networkConfig, vmConfig } from './config.bicep'
import { securityRules } from './security/rules.bicep'

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Storage account name')
param storageAccountName string

var resourcePrefix = 'test'

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-02-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: storageAccountType
  }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

output storageAccountId string = storageAccount.id
