var minimumTlsVersion = 'TLS1_2'

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: 'examplestorage'
  location: 'westeurope'
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    minimumTlsVersion: minimumTlsVersion
  }
}
