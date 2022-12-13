// pass

resource default 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
}

resource allowAll 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'

  properties: {
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

resource denyAndBypass 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'

  properties: {
    networkAcls: {
      bypass: 'Logging'
      defaultAction: 'Deny'
    }
  }
}

// fail

resource deny 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'

  properties: {
    networkAcls: {
      defaultAction: 'Deny'
    }
  }
}

resource denyAndBypassNone 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: diagStorageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'

  properties: {
    networkAcls: {
      bypass: 'None'
      defaultAction: 'Deny'
    }
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
