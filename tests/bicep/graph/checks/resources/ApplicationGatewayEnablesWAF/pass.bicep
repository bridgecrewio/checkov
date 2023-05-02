@description('Application gateway name')
param applicationGatewayName string = 'pass'

@description('Application gateway location')
param location string = resourceGroup().location

@description('Application gateway tier')
@allowed([
  'Standard'
  'WAF'
  'Standard_v2'
  'WAF_v2'
])
param tier string = 'WAF_v2'

@description('Application gateway sku')
@allowed([
  'Standard_Small'
  'Standard_Medium'
  'Standard_Large'
  'WAF_Medium'
  'WAF_Large'
  'Standard_v2'
  'WAF_v2'
])
param sku string = 'WAF_v2'

@description('Enable HTTP/2 support')
param http2Enabled bool = true

@description('Capacity (instance count) of application gateway')
@minValue(1)
@maxValue(32)
param capacity int = 2

@description('Autoscale capacity (instance count) of application gateway')
@minValue(1)
@maxValue(32)
param autoScaleMaxCapacity int = 10

@description('Public ip address name')
param publicIpAddressName string = 'appGwpublicIp'

@description('Virutal network subscription id')
param vNetSubscriptionId string = subscription().subscriptionId

@description('Virutal network resource group')
param existingVnetResourceGroup string

@description('Virutal network name')
param existingVnetName string

@description('Application gateway subnet name')
param existingSubnetName string

@description('Array containing ssl certificates')
param sslCertificates array = []

@description('Array containing trusted root certificates')
param trustedRootCertificates array = []

@description('Array containing http listeners')
param httpListeners array = [
{
name: 'HttpListener01'
protocol: 'Http'
frontEndPort: 'port_80'
firewallPolicy: 'Enabled'
}
]

@description('Array containing backend address pools')
param backendAddressPools array = [
{
name: 'BackendPool01'
backendAddresses: [
{
ipAddress: '10.1.2.3'
}
]
}
]

@description('Array containing backend http settings')
param backendHttpSettings array = [
{
name: 'BackendHttpSetting01'
port: 80
protocol: 'Http'
cookieBasedAffinity: 'Enabled'
affinityCookieName: 'CookieAffinity01'
requestTimeout: 300
connectionDraining: {
drainTimeoutInSec: 60
enabled: true
}
}
]

@description('Array containing request routing rules')
param rules array = [
{
name: 'Rule01'
ruleType: 'Basic'
listener: 'HttpListener01'
backendPool: 'BackendPool01'
backendHttpSettings: 'BackendHttpSetting01'
}
]

@description('Array containing redirect configurations')
param redirectConfigurations array = []

@description('Array containing front end ports')
param frontEndPorts array = [
{
name: 'port_80'
port: 80
}
]

@description('Array containing custom probes')
param customProbes array = []

@description('Enable web application firewall')
param enableWebApplicationFirewall bool = true

@description('Name of the firewall policy. Only required if enableWebApplicationFirewall is set to true')
param firewallPolicyName string = 'FirewallPolicy01'

@description('Array containing the firewall policy settings. Only required if enableWebApplicationFirewall is set to true')
param firewallPolicySettings object = {
requestBodyCheck: true
maxRequestBodySizeInKb: 128
fileUploadLimitInMb: 100
state: 'Enabled'
mode: 'Detection'
}

@description('Array containing the firewall policy custom rules. Only required if enableWebApplicationFirewall is set to true')
param firewallPolicyCustomRules array = []

@description('Array containing the firewall policy managed rule sets. Only required if enableWebApplicationFirewall is set to true')
param firewallPolicyManagedRuleSets array = [
{
ruleSetType: 'OWASP'
ruleSetVersion: '3.2'
}
]

@description('Array containing the firewall policy managed rule exclusions. Only required if enableWebApplicationFirewall is set to true')
param firewallPolicyManagedRuleExclusions array = []

@description('Enable delete lock')
param enableDeleteLock bool = false

@description('Enable diagnostic logs')
param enableDiagnostics bool = false

@description('Storage account resource id. Only required if enableDiagnostics is set to true')
param diagnosticStorageAccountId string = ''

@description('Log analytics workspace resource id. Only required if enableDiagnostics is set to true')
param logAnalyticsWorkspaceId string = ''

var publicIpLockName = '${publicIpAddressName}-lck'
var publicIpDiagnosticsName = '${publicIpAddressName}-dgs'
var appGatewayLockName = '${applicationGatewayName}-lck'
var appGatewayDiagnosticsName = '${applicationGatewayName}-dgs'
var gatewayIpConfigurationName = 'appGatewayIpConfig'
var frontendIpConfigurationName = 'appGwPublicFrontendIp'

resource publicIpAddress 'Microsoft.Network/publicIPAddresses@2021-03-01' = {
  name: publicIpAddressName
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource publicIpDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (enableDiagnostics) {
  scope: publicIpAddress
  name: publicIpDiagnosticsName
  properties: {
    workspaceId: (empty(logAnalyticsWorkspaceId) ? null : logAnalyticsWorkspaceId)
    storageAccountId: (empty(diagnosticStorageAccountId) ? null : diagnosticStorageAccountId)
    logs: [
      {
        category: 'DDoSProtectionNotifications'
        enabled: true
      }
      {
        category: 'DDoSMitigationFlowLogs'
        enabled: true
      }
      {
        category: 'DDoSMitigationReports'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

resource publicIpLock 'Microsoft.Authorization/locks@2017-04-01' = if (enableDeleteLock) {
  scope: publicIpAddress
  name: publicIpLockName
  properties: {
    level: 'CanNotDelete'
  }
}

resource applicationGateway 'Microsoft.Network/applicationGateways@2021-03-01' = {
  name: applicationGatewayName
  location: location
  properties: {
    frontendPorts: [for item in frontEndPorts: {
      name: item.name
      properties: {
        port: item.port
      }
    }]
    probes: [for item in customProbes: {
      name: item.name
      properties: {
        protocol: item.protocol
        host: item.host
        path: item.path
        interval: item.interval
        timeout: item.timeout
        unhealthyThreshold: item.unhealthyThreshold
        pickHostNameFromBackendHttpSettings: item.pickHostNameFromBackendHttpSettings
        minServers: item.minServers
        match: item.match
      }
    }]
    backendAddressPools: [for item in backendAddressPools: {
      name: item.name
      properties: {
        backendAddresses: item.backendAddresses
      }
    }]
    trustedRootCertificates: [for item in trustedRootCertificates: {
      name: item.name
      properties: {
        keyVaultSecretId: '${reference(item.keyVaultResourceId, '2021-10-01').vaultUri}secrets/${item.secretName}'
      }
    }]
    sslCertificates: [for item in sslCertificates: {
      name: item.name
      properties: {
        keyVaultSecretId: '${reference(item.keyVaultResourceId, '2021-10-01').vaultUri}secrets/${item.secretName}'
      }
    }]
    backendHttpSettingsCollection: [for item in backendHttpSettings: {
      name: item.name
      properties: {
        port: item.port
        protocol: item.protocol
        cookieBasedAffinity: item.cookieBasedAffinity
        affinityCookieName: (contains(item, 'affinityCookieName') ? item.affinityCookieName : null)
        requestTimeout: item.requestTimeout
        connectionDraining: item.connectionDraining
        probe: (contains(item, 'probeName') ? json('{"id": "${resourceId('Microsoft.Network/applicationGateways/probes', applicationGatewayName, item.probeName)}"}') : null)
        trustedRootCertificates: (contains(item, 'trustedRootCertificate') ? json('[{"id": "${resourceId('Microsoft.Network/applicationGateways/trustedRootCertificates', applicationGatewayName, item.trustedRootCertificate)}"}]') : null)
        hostName: (contains(item, 'hostName') ? item.hostName : null)
        pickHostNameFromBackendAddress: (contains(item, 'pickHostNameFromBackendAddress') ? item.pickHostNameFromBackendAddress : false)
      }
    }]
    httpListeners: [for item in httpListeners: {
      name: item.name
      properties: {
        frontendIPConfiguration: {
          id: resourceId('Microsoft.Network/applicationGateways/frontendIPConfigurations', applicationGatewayName, frontendIpConfigurationName)
        }
        frontendPort: {
          id: resourceId('Microsoft.Network/applicationGateways/frontendPorts', applicationGatewayName, item.frontEndPort)
        }
        protocol: item.protocol
        sslCertificate: (contains(item, 'sslCertificate') ? json('{"id": "${resourceId('Microsoft.Network/applicationGateways/sslCertificates', applicationGatewayName, item.sslCertificate)}"}') : null)
        hostNames: (contains(item, 'hostNames') ? item.hostNames : null)
        hostName: (contains(item, 'hostName') ? item.hostName : null)
        requireServerNameIndication: (contains(item, 'requireServerNameIndication') ? item.requireServerNameIndication : false)
        firewallPolicy: (contains(item, 'firewallPolicy') ? json('{"id": "${firewallPolicyName_placeholdervalue_firewallPolicy.id}"}') : null)
      }
    }]
    requestRoutingRules: [for item in rules: {
      name: item.name
      properties: {
        ruleType: item.ruleType
        httpListener: (contains(item, 'listener') ? json('{"id": "${resourceId('Microsoft.Network/applicationGateways/httpListeners', applicationGatewayName, item.listener)}"}') : null)
        backendAddressPool: (contains(item, 'backendPool') ? json('{"id": "${resourceId('Microsoft.Network/applicationGateways/backendAddressPools', applicationGatewayName, item.backendPool)}"}') : null)
        backendHttpSettings: (contains(item, 'backendHttpSettings') ? json('{"id": "${resourceId('Microsoft.Network/applicationGateways/backendHttpSettingsCollection', applicationGatewayName, item.backendHttpSettings)}"}') : null)
        redirectConfiguration: (contains(item, 'redirectConfiguration') ? json('{"id": "${resourceId('Microsoft.Network/applicationGateways/redirectConfigurations', applicationGatewayName, item.redirectConfiguration)}"}') : null)
      }
    }]
    redirectConfigurations: [for item in redirectConfigurations: {
      name: item.name
      properties: {
        redirectType: item.redirectType
        targetUrl: item.targetUrl
        targetListener: (contains(item, 'targetListener') ? json('{"id": "${resourceId('Microsoft.Network/applicationGateways/httpListeners', applicationGatewayName, item.targetListener)}"}') : null)
        includePath: item.includePath
        includeQueryString: item.includeQueryString
        requestRoutingRules: [
          {
            id: resourceId('Microsoft.Network/applicationGateways/requestRoutingRules', applicationGatewayName, item.requestRoutingRule)
          }
        ]
      }
    }]
    sku: {
      name: sku
      tier: tier
    }
    autoscaleConfiguration: {
      minCapacity: capacity
      maxCapacity: autoScaleMaxCapacity
    }
    enableHttp2: http2Enabled
    webApplicationFirewallConfiguration: {
      enabled:  true
      firewallMode: firewallPolicySettings.mode
      ruleSetType: 'OWASP'
      ruleSetVersion: '3.2'
    } 
    gatewayIPConfigurations: [
      {
        name: gatewayIpConfigurationName
        properties: {
          subnet: {
            id: resourceId(vNetSubscriptionId, existingVnetResourceGroup, 'Microsoft.Network/virtualNetworks/subnets', existingVnetName, existingSubnetName)
          }
        }
      }
    ]
    frontendIPConfigurations: [
      {
        name: frontendIpConfigurationName
        properties: {
          publicIPAddress: {
            id: publicIpAddress.id
          }
        }
      }
    ]
    firewallPolicy: (enableWebApplicationFirewall ? {
      id: firewallPolicyName_placeholdervalue_firewallPolicy.id
    } : null)
  }
}

resource appGatewayDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (enableDiagnostics) {
  scope: applicationGateway
  name: appGatewayDiagnosticsName
  properties: {
    workspaceId: (empty(logAnalyticsWorkspaceId) ? null : logAnalyticsWorkspaceId)
    storageAccountId: (empty(diagnosticStorageAccountId) ? null : diagnosticStorageAccountId)
    logs: [
      {
        category: 'ApplicationGatewayAccessLog'
        enabled: true
      }
      {
        category: 'ApplicationGatewayPerformanceLog'
        enabled: true
      }
      {
        category: 'ApplicationGatewayFirewallLog'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

resource appGatewayLock 'Microsoft.Authorization/locks@2017-04-01' = if (enableDeleteLock) {
  scope: applicationGateway
  name: appGatewayLockName
  properties: {
    level: 'CanNotDelete'
  }
}

resource firewallPolicyName_placeholdervalue_firewallPolicy 'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies@2021-03-01' = if (enableWebApplicationFirewall) {
  name: ((firewallPolicyName == '') ? 'placeholdervalue' : firewallPolicyName)
  location: location
  properties: {
    customRules: firewallPolicyCustomRules
    policySettings: firewallPolicySettings
    managedRules: {
      managedRuleSets: firewallPolicyManagedRuleSets
      exclusions: firewallPolicyManagedRuleExclusions
    }
  }
}

output name string = applicationGatewayName
output id string = applicationGateway.id
