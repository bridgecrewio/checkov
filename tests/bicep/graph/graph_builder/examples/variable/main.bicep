var virtualMachineName = 'example-vm'

var location = 'westeurope'

var acrName = 'exmaple-acr'

var acrNestedName = 'exmaple-nested-acr'

var keyData3 = 'key-data-3'

var publisher = 'MicrosoftWindowsServer'

var nicId = [
  {
    id: 'example-id'
  }
]

var publicKey2 = {
  keyData: 'key-data-2'
  path: 'path-2'
}

var publicKey4 = {
  keyData: 'key-data-4'
  path: {
    name: 'path-4'
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2021-11-01' = {
  name: virtualMachineName
  location: location
  properties: {
    networkProfile: {
      networkInterfaces: nicId
    }
    osProfile: {
      linuxConfiguration: {
        ssh: {
          publicKeys: [
            {
              keyData: 'key-data-1'
              path: 'path-1'
            }
            publicKey2
            {
              keyData: keyData3
              path: 'path-3'
            }
            {
              keyData: publicKey4.keyData
              path: publicKey4.path.name
            }
          ]
        }
      }
    }
    storageProfile: {
      imageReference: {
        publisher: publisher
      }
    }
  }
  tags: {
    displayName: 'Container Registry'
    'container.registry.name': acrName
    'container.registry': {
      name: acrNestedName
    }
  }
}
