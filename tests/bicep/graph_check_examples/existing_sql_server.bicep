resource server 'Microsoft.Sql/servers@2023-08-01' existing = {
  name: 'sql-server'
}

resource existingDatabase 'Microsoft.Sql/servers/databases@2023-08-01' existing = {
  parent: server
  name: 'existing-database'
}

resource database 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: 'new-database'
  location: resourceGroup().location
}

resource securityAlertPolicy 'Microsoft.Sql/servers/databases/securityAlertPolicies@2023-08-01' = {
  parent: database
  name: 'default'
  properties: {
    state: 'Enabled'
  }
}
