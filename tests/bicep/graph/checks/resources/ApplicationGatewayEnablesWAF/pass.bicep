@description('Admin username for the backend servers')
param adminUsername string

@description('Password for the admin account on the backend servers')
@secure()
param adminPassword string

@description('Location for all resources.')
param location string = resourceGroup().location

@description('Size of the virtual machine.')
param vmSize string = 'Standard_B2ms'

var virtualMachines_myVM_name = 'myVM'
var virtualNetworks_myVNet_name_var = 'myVNet'
var myNic_name = 'net-int'
var ipconfig_name = 'ipconfig'
var publicIPAddress_name = 'public_ip'
var nsg_name = 'vm-nsg'
var applicationGateways_myAppGateway_name = 'pass'
var vnet_prefix = '10.0.0.0/16'
var ag_subnet_prefix = '10.0.0.0/24'
var backend_subnet_prefix = '10.0.1.0/24'
var AppGW_AppFW_Pol_name_var = 'WafPol01'

resource nsg_name_0_2_1 'Microsoft.Network/networkSecurityGroups@2021-08-01' = [for i in range(0, length(range(0, 2))): {
  name: '${nsg_name}${(range(0, 2)[i] + 1)}'
  location: location
  properties: {
    securityRules: [
      {
        name: 'RDP'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '3389'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 300
          direction: 'Inbound'
        }
      }
    ]
  }
}]

resource publicIPAddress_name_0_3 'Microsoft.Network/publicIPAddresses@2021-08-01' = [for i in range(0, length(range(0, 3))): {
  name: '${publicIPAddress_name}${range(0, 3)[i]}'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAddressVersion: 'IPv4'
    publicIPAllocationMethod: 'Static'
    idleTimeoutInMinutes: 4
  }
}]

resource virtualNetworks_myVNet_name 'Microsoft.Network/virtualNetworks@2021-08-01' = {
  name: virtualNetworks_myVNet_name_var
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnet_prefix
      ]
    }
    subnets: [
      {
        name: 'myAGSubnet'
        properties: {
          addressPrefix: ag_subnet_prefix
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
      {
        name: 'myBackendSubnet'
        properties: {
          addressPrefix: backend_subnet_prefix
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
    ]
    enableDdosProtection: false
    enableVmProtection: false
  }
}

resource virtualMachines_myVM_name_0_2_1 'Microsoft.Compute/virtualMachines@2021-11-01' = [for i in range(0, length(range(0, 2))): {
  name: '${virtualMachines_myVM_name}${(range(0, 2)[i] + 1)}'
  location: location
  properties: {
    hardwareProfile: {
      vmSize: vmSize
    }
    storageProfile: {
      imageReference: {
        publisher: 'MicrosoftWindowsServer'
        offer: 'WindowsServer'
        sku: '2019-Datacenter'
        version: 'latest'
      }
      osDisk: {
        osType: 'Windows'
        createOption: 'FromImage'
        caching: 'ReadWrite'
        managedDisk: {
          storageAccountType: 'StandardSSD_LRS'
        }
        diskSizeGB: 127
      }
    }
    osProfile: {
      computerName: '${virtualMachines_myVM_name}${(range(0, 2)[i] + 1)}'
      adminUsername: adminUsername
      adminPassword: adminPassword
      windowsConfiguration: {
        provisionVMAgent: true
        enableAutomaticUpdates: true
      }
      allowExtensionOperations: true
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: resourceId('Microsoft.Network/networkInterfaces', '${myNic_name}${(range(0, 2)[i] + 1)}')
        }
      ]
    }
  }
  dependsOn: [
    myNic_name_0_2_1
  ]
}]

resource virtualMachines_myVM_name_0_2_1_IIS 'Microsoft.Compute/virtualMachines/extensions@2021-11-01' = [for i in range(0, length(range(0, 2))): {
  name: '${virtualMachines_myVM_name}${(range(0, 2)[i] + 1)}/IIS'
  location: location
  properties: {
    autoUpgradeMinorVersion: true
    publisher: 'Microsoft.Compute'
    type: 'CustomScriptExtension'
    typeHandlerVersion: '1.4'
    settings: {
      commandToExecute: 'powershell Add-WindowsFeature Web-Server; powershell Add-Content -Path "C:\\inetpub\\wwwroot\\Default.htm" -Value $($env:computername)'
    }
  }
  dependsOn: [
    virtualMachines_myVM_name_0_2_1
  ]
}]

resource pass 'Microsoft.Network/applicationGateways@2021-08-01' = {
  name: 'pass'
  location: location
  properties: {
    sku: {
      name: 'WAF_v2'
      tier: 'WAF_v2'
      capacity: 2
    }
    gatewayIPConfigurations: [
      {
        name: 'appGatewayIpConfig'
        properties: {
          subnet: {
            id: resourceId('Microsoft.Network/virtualNetworks/subnets', virtualNetworks_myVNet_name_var, 'myAGSubnet')
          }
        }
      }
    ]
    frontendIPConfigurations: [
      {
        name: 'appGwPublicFrontendIp'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: resourceId('Microsoft.Network/publicIPAddresses', '${publicIPAddress_name}0')
          }
        }
      }
    ]
    frontendPorts: [
      {
        name: 'port_80'
        properties: {
          port: 80
        }
      }
    ]
    backendAddressPools: [
      {
        name: 'myBackendPool'
        properties: {}
      }
    ]
    backendHttpSettingsCollection: [
      {
        name: 'myHTTPSetting'
        properties: {
          port: 80
          protocol: 'Http'
          cookieBasedAffinity: 'Disabled'
          pickHostNameFromBackendAddress: false
          requestTimeout: 20
        }
      }
    ]
    httpListeners: [
      {
        name: 'myListener'
        properties: {
          firewallPolicy: {
            id: AppGW_AppFW_Pol_name.id
          }
          frontendIPConfiguration: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendIPConfigurations', applicationGateways_myAppGateway_name, 'appGwPublicFrontendIp')
          }
          frontendPort: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendPorts', applicationGateways_myAppGateway_name, 'port_80')
          }
          protocol: 'Http'
          requireServerNameIndication: false
        }
      }
    ]
    requestRoutingRules: [
      {
        name: 'myRoutingRule'
        properties: {
          ruleType: 'Basic'
          priority: 10
          httpListener: {
            id: resourceId('Microsoft.Network/applicationGateways/httpListeners', applicationGateways_myAppGateway_name, 'myListener')
          }
          backendAddressPool: {
            id: resourceId('Microsoft.Network/applicationGateways/backendAddressPools', applicationGateways_myAppGateway_name, 'myBackendPool')
          }
          backendHttpSettings: {
            id: resourceId('Microsoft.Network/applicationGateways/backendHttpSettingsCollection', applicationGateways_myAppGateway_name, 'myHTTPSetting')
          }
        }
      }
    ]
    enableHttp2: false
    firewallPolicy: {
      id: AppGW_AppFW_Pol_name.id
    }
  }
  dependsOn: [

    virtualNetworks_myVNet_name
    publicIPAddress_name_0_3
  ]
}

resource AppGW_AppFW_Pol_name 'Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies@2021-08-01' = {
  name: AppGW_AppFW_Pol_name_var
  location: location
  properties: {
    customRules: [
      {
        name: 'CustRule01'
        priority: 100
        ruleType: 'MatchRule'
        action: 'Block'
        matchConditions: [
          {
            matchVariables: [
              {
                variableName: 'RemoteAddr'
              }
            ]
            operator: 'IPMatch'
            negationConditon: true
            matchValues: [
              '10.10.10.0/24'
            ]
          }
        ]
      }
    ]
    policySettings: {
      requestBodyCheck: true
      maxRequestBodySizeInKb: 128
      fileUploadLimitInMb: 100
      state: 'Enabled'
      mode: 'Prevention'
    }
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType: 'OWASP'
          ruleSetVersion: '3.1'
        }
      ]
    }
  }
}

resource myNic_name_0_2_1 'Microsoft.Network/networkInterfaces@2021-08-01' = [for i in range(0, length(range(0, 2))): {
  name: '${myNic_name}${(range(0, 2)[i] + 1)}'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: '${ipconfig_name}${(range(0, 2)[i] + 1)}'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: resourceId('Microsoft.Network/publicIPAddresses', '${publicIPAddress_name}${(range(0, 2)[i] + 1)}')
          }
          subnet: {
            id: resourceId('Microsoft.Network/virtualNetworks/subnets', virtualNetworks_myVNet_name_var, 'myBackendSubnet')
          }
          primary: true
          privateIPAddressVersion: 'IPv4'
          applicationGatewayBackendAddressPools: [
            {
              id: resourceId('Microsoft.Network/applicationGateways/backendAddressPools', applicationGateways_myAppGateway_name, 'myBackendPool')
            }
          ]
        }
      }
    ]
    enableAcceleratedNetworking: false
    enableIPForwarding: false
    networkSecurityGroup: {
      id: resourceId('Microsoft.Network/networkSecurityGroups', '${nsg_name}${(range(0, 2)[i] + 1)}')
    }
  }
  dependsOn: [
    resourceId('Microsoft.Network/applicationGateways', applicationGateways_myAppGateway_name)
    virtualNetworks_myVNet_name
    nsg_name_0_2_1
    publicIPAddress_name_0_3
  ]
}]