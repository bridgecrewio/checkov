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
      emailAccountAdmins: true
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
    state: 'Enabled'
    emailAccountAdmins: 'enabled'
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
      emailAccountAdmins: true
    }
  }
}

resource databaseAdminsFalse 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: 'admins-false'
  location: resourceGroup().location

  resource securityAlertPolicy 'securityAlertPolicies' = {
    name: 'Default'
    properties: {
      state: 'Enabled'
      emailAccountAdmins: false
      emailAddresses: [
        'secops@example.com'
      ]
    }
  }
}

resource databaseAdminsDisabled 'Microsoft.Sql/servers/databases@2014-04-01' = {
  parent: server
  name: 'admins-disabled'
  location: resourceGroup().location

  resource securityAlertPolicy 'securityAlertPolicies' = {
    name: 'default'
    properties: {
      state: 'Enabled'
      emailAccountAdmins: 'Disabled'
      emailAddresses: 'secops@example.com'
    }
  }
}

resource databaseWithoutAdminsSetting 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: 'without-admins-setting'
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
