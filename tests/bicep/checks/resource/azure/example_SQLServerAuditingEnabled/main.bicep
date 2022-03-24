// pass

resource serverEnabled 'Microsoft.Sql/servers/auditingSettings@2021-02-01-preview' = {
  name: 'default'
  parent: sqlServer
  properties: {
    isAzureMonitorTargetEnabled: true
    state: 'Enabled'
  }
}

resource dbEnabled 'Microsoft.Sql/servers/databases/auditingSettings@2021-08-01-preview' = {
  name: 'default'
  parent: sqlServerDB
  properties: {
    isAzureMonitorTargetEnabled: true
    state: 'Enabled'
  }
}

resource nestedExample 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }

  resource nestedAudit 'auditingSettings' = {
    name: 'default123'

    properties: {
      isAzureMonitorTargetEnabled: true
      state: 'Enabled'
    }
  }
}

// fail

resource serverDefault 'Microsoft.Sql/servers/auditingSettings@2021-02-01-preview' = {
  name: 'default'
  parent: sqlServer
}

resource serverDisabled 'Microsoft.Sql/servers/auditingSettings@2021-02-01-preview' = {
  name: 'default'
  parent: sqlServer
  properties: {
    isAzureMonitorTargetEnabled: true
    state: 'Disabled'
  }
}

resource dbDefault 'Microsoft.Sql/servers/databases/auditingSettings@2021-08-01-preview' = {
  name: 'default'
  parent: sqlServerDB
}

resource dbDisabled 'Microsoft.Sql/servers/databases/auditingSettings@2021-08-01-preview' = {
  name: 'default'
  parent: sqlServerDB
  properties: {
    isAzureMonitorTargetEnabled: true
    state: 'Disabled'
  }
}
