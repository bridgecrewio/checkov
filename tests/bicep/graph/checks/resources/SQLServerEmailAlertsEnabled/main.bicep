resource server 'Microsoft.Sql/servers@2023-08-01' existing = {
  name: 'sql-server'
}

// pass

resource databaseNestedPolicy 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: 'nested-policy'
  location: resourceGroup().location

  resource securityAlertPolicy 'securityAlertPolicies' = {
    name: 'Default'
    properties: {
      state: 'Enabled'
      emailAddresses: [
        'secops@example.com'
      ]
    }
  }
}

resource databaseParentPolicy 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: 'parent-policy'
  location: resourceGroup().location
}

resource parentPolicy 'Microsoft.Sql/servers/databases/securityAlertPolicies@2014-04-01' = {
  parent: databaseParentPolicy
  name: 'default'
  properties: {
    state: 'enabled'
    emailAddresses: 'secops@example.com;dba@example.com'
  }
}

// fail

resource databaseWithoutPolicy 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: 'without-policy'
  location: resourceGroup().location
}

resource databaseDisabledPolicy 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: 'disabled-policy'
  location: resourceGroup().location

  resource securityAlertPolicy 'securityAlertPolicies' = {
    name: 'Default'
    properties: {
      state: 'Disabled'
      emailAddresses: [
        'secops@example.com'
      ]
    }
  }
}

resource databaseWithoutEmailAddresses 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: 'without-email-addresses'
  location: resourceGroup().location

  resource securityAlertPolicy 'securityAlertPolicies' = {
    name: 'Default'
    properties: {
      state: 'Enabled'
      emailAccountAdmins: true
    }
  }
}

resource databaseEmptyEmailAddresses 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: 'empty-email-addresses'
  location: resourceGroup().location

  resource securityAlertPolicy 'securityAlertPolicies' = {
    name: 'Default'
    properties: {
      state: 'Enabled'
      emailAddresses: []
    }
  }
}
