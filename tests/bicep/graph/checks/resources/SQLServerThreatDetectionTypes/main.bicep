// pass
resource serverEnabled 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }

  resource securityAlertPolicyEnabled 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Enabled'
      disabledAlerts: [
      ]
    }
  }
}

resource serverEnabledWithoutAlertsAttribute 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }

  resource securityAlertPolicyEnabled 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Enabled'
    }
  }
}

resource databaseEnabled 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  name: '${server.name}/${sqlDBName}'
  location: location
  sku: {
    name: 'GP_S_Gen5_2'
    tier: 'GeneralPurpose'
  }

  resource securityAlertPolicyEnabled 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Enabled'
      disabledAlerts: [
      ]
    }
  }
}

resource databaseEnabledWithoutAlertsAttribute 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  name: '${server.name}/${sqlDBName}'
  location: location
  sku: {
    name: 'GP_S_Gen5_2'
    tier: 'GeneralPurpose'
  }

  resource securityAlertPolicyEnabled 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Enabled'
    }
  }
}

// fail
resource serverDisabledState 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }

  resource securityAlertPolicyEnabled 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Disabled'
      disabledAlerts: [
      ]
    }
  }
}

resource serverDisabledAlerts 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }

  resource securityAlertPolicyEnabled 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Enabled'
      disabledAlerts: [
        'disabledAlert'
      ]
    }
  }
}

resource serverDisabled 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: 'default'
  location: location

  properties: {
    administratorLogin: sqlLogicalServer.userName
    administratorLoginPassword: password
    version: '12.0'
    minimalTlsVersion: sqlLogicalServer.minimalTlsVersion
    publicNetworkAccess: sqlLogicalServer.publicNetworkAccess
  }

  resource securityAlertPolicyEnabled 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Disabled'
      disabledAlerts: [
        'disabledAlert'
      ]
    }
  }
}

resource databaseDisabledState 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  name: '${server.name}/${sqlDBName}'
  location: location
  sku: {
    name: 'GP_S_Gen5_2'
    tier: 'GeneralPurpose'
  }

  resource securityAlertPolicyDisabledAlerts 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Disabled'
      disabledAlerts: [
      ]
    }
  }
}

resource databaseDisabledAlerts 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  name: '${server.name}/${sqlDBName}'
  location: location
  sku: {
    name: 'GP_S_Gen5_2'
    tier: 'GeneralPurpose'
  }

  resource securityAlertPolicyDisabledAlerts 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Enabled'
      disabledAlerts: [
        'disabledAlert'
      ]
    }
  }
}

resource databaseDisabled 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  name: '${server.name}/${sqlDBName}'
  location: location
  sku: {
    name: 'GP_S_Gen5_2'
    tier: 'GeneralPurpose'
  }

  resource securityAlertPolicy 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Disabled'
      disabledAlerts: [
        'disabledAlert'
      ]
    }
  }
}

