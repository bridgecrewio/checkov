// should not flag an existing resource for any check
resource storageAccountExisting 'Microsoft.Storage/storageAccounts@2021-08-01' existing = {
  name: 'existing'
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-08-01' = {
  name: 'new'
}
