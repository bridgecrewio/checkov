// pass

resource serverEnabled 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: resourceGroup().location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }

  resource childEnabled 'auditingSettings' = {
    name: 'default123'

    properties: {
      isAzureMonitorTargetEnabled: true
      state: 'Enabled'
    }
  }
}

resource parentEnabled 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: resourceGroup().location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }
}

resource childEnabled 'Microsoft.Sql/servers/auditingSettings@2021-02-01-preview' = {
  name: 'default'

  parent: parentEnabled

  properties: {
    isAzureMonitorTargetEnabled: true
    state: 'Enabled'
  }
}

resource databaseEnabled 'Microsoft.Sql/servers/databases@2020-08-01-preview' = {
  name: '${server.name}/${sqlDBName}'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }

  resource childEnabled 'auditingSettings' = {
    name: 'default123'

    properties: {
      isAzureMonitorTargetEnabled: true
      state: 'Enabled'
    }
  }
}

// fail

resource serverDefault 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: resourceGroup().location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }

  resource childDefault 'auditingSettings' = {
    name: 'default'

    properties: {
      isAzureMonitorTargetEnabled: true
    }
  }
}

resource parentDefault 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: resourceGroup().location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }
}

resource childDefault 'Microsoft.Sql/servers/auditingSettings@2021-02-01-preview' = {
  name: 'default'

  parent: parentDefault

  properties: {
    isAzureMonitorTargetEnabled: true
  }
}

resource databaseDefault 'Microsoft.Sql/servers/databases@2020-08-01-preview' = {
  name: '${server.name}/${sqlDBName}'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }

  resource childDefault 'auditingSettings' = {
    name: 'default123'

    properties: {
      isAzureMonitorTargetEnabled: true
    }
  }
}

resource serverDisabled 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: resourceGroup().location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }

  resource childDisabled 'auditingSettings' = {
    name: 'default'

    properties: {
      isAzureMonitorTargetEnabled: true
      state: 'Disabled'
    }
  }
}

resource parentDisabled 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: resourceGroup().location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }
}

resource childDisabled 'Microsoft.Sql/servers/auditingSettings@2021-02-01-preview' = {
  name: 'default'

  parent: parentDefault

  properties: {
    isAzureMonitorTargetEnabled: true
    state: 'Disabled'
  }
}

resource databaseDisabled 'Microsoft.Sql/servers/databases@2020-08-01-preview' = {
  name: '${server.name}/${sqlDBName}'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }

  resource childDisabled 'auditingSettings' = {
    name: 'default123'

    properties: {
      isAzureMonitorTargetEnabled: true
      state: 'Disabled'
    }
  }
}
