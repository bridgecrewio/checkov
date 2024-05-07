resource sqlServer_pass 'Microsoft.Sql/servers@2023-05-01-preview' = {  
  name: sqlServerName
}

/// SQL Auditing

resource sql_auditing_pass 'Microsoft.Sql/servers/auditingSettings@2023-05-01-preview' = {
  name: 'default'
  parent: sqlServer_pass
  properties: {
    isAzureMonitorTargetEnabled: true
    retentionDays: 92
    state: 'Enabled'
  }
}
