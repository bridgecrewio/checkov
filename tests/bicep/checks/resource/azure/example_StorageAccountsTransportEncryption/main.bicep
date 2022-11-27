// pass

resource default2019 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
}

resource enabled 'Microsoft.Storage/storageAccounts@2018-11-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'

  properties: {
    supportsHttpsTrafficOnly: true
  }
}

// fail

resource default2018 'Microsoft.Storage/storageAccounts@2018-11-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
}

resource disabled 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'

  properties: {
    supportsHttpsTrafficOnly: false
  }
}

// unknown

resource unknown 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'

  properties: storageAccountProperties
}

