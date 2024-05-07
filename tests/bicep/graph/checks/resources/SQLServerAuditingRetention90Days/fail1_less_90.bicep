resource sqlServer_fail1 'Microsoft.Sql/servers@2023-05-01-preview' = {  
  name: sqlServerName
}

/// SQL Auditing

resource sql_auditing_fail1 'Microsoft.Sql/servers/auditingSettings@2023-05-01-preview' = {
  name: 'default'
  parent: sqlServer_fail1
  properties: {
    isAzureMonitorTargetEnabled: true
    retentionDays: 67
    state: 'Enabled'
  }
}
