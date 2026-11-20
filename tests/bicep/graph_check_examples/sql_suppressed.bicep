resource suppressedDatabase 'Microsoft.Sql/servers/databases@2023-08-01' = {
  // checkov:skip=CKV_AZURE_25: threat detection is configured on the server
  name: 'sql-server/suppressed-database'
  location: resourceGroup().location
}

resource database 'Microsoft.Sql/servers/databases@2023-08-01' = {
  name: 'sql-server/database'
  location: resourceGroup().location
}
