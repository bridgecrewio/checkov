param azureFirewalls_fail_name string
param publicIPAddresses_testpip_name string
param virtualNetworks_testvnet_name string

resource publicIPAddresses_testpip_name_resource 'Microsoft.Network/publicIPAddresses@2022-09-01' = {
  location: 'westeurope'
  name: publicIPAddresses_testpip_name
  properties: {
    ddosSettings: {
      protectionMode: 'VirtualNetworkInherited'
    }
    idleTimeoutInMinutes: 4
    ipAddress: '20.234.231.26'
    ipTags: []
    publicIPAddressVersion: 'IPv4'
    publicIPAllocationMethod: 'Static'
  }
  sku: {
    name: 'Standard'
    tier: 'Regional'
  }
}

resource virtualNetworks_testvnet_name_resource 'Microsoft.Network/virtualNetworks@2022-09-01' = {
  location: 'westeurope'
  name: virtualNetworks_testvnet_name
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    dhcpOptions: {
      dnsServers: []
    }
    enableDdosProtection: false
    subnets: [
      {
        id: virtualNetworks_testvnet_name_AzureFirewallSubnet.id
        name: 'AzureFirewallSubnet'
        properties: {
          addressPrefix: '10.0.1.0/24'
          delegations: []
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
          serviceEndpoints: []
        }
        type: 'Microsoft.Network/virtualNetworks/subnets'
      }
    ]
    virtualNetworkPeerings: []
  }
}

resource virtualNetworks_testvnet_name_AzureFirewallSubnet 'Microsoft.Network/virtualNetworks/subnets@2022-09-01' = {
  name: '${virtualNetworks_testvnet_name}/AzureFirewallSubnet'
  properties: {
    addressPrefix: '10.0.1.0/24'
    delegations: []
    privateEndpointNetworkPolicies: 'Enabled'
    privateLinkServiceNetworkPolicies: 'Enabled'
    serviceEndpoints: []
  }
  dependsOn: [
    virtualNetworks_testvnet_name_resource
  ]
}

resource fail 'Microsoft.Network/azureFirewalls@2022-09-01' = {
  location: 'westeurope'
  name: 'fail'
  properties: {
    additionalProperties: {}
    applicationRuleCollections: []
    ipConfigurations: [
      {
        id: '${resourceId('Microsoft.Network/azureFirewalls', azureFirewalls_fail_name)}/azureFirewallIpConfigurations/configuration'
        name: 'configuration'
        properties: {
          publicIPAddress: {
            id: publicIPAddresses_testpip_name_resource.id
          }
          subnet: {
            id: virtualNetworks_testvnet_name_AzureFirewallSubnet.id
          }
        }
      }
    ]
    natRuleCollections: []
    networkRuleCollections: []
    sku: {
      name: 'AZFW_VNet'
      tier: 'Standard'
    }
    threatIntelMode: 'Alert'
  }
}