resource sqlServer_fail3 'Microsoft.Sql/servers@2023-05-01-preview' = {  
  name: sqlServerName
}

/// SQL Auditing

resource sql_auditing_fail3 'Microsoft.Sql/servers/auditingSettings@2023-05-01-preview' = {
  name: 'default'
  parent: sqlServer_fail3
  properties: {
    isAzureMonitorTargetEnabled: true
    retentionDays: 92
    state: 'Disabled'
  }
}
