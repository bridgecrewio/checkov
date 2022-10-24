param virtualMachineName string = 'example-vm'

param location string

param acrName string = 'exmaple-acr'

param acrNestedName string = 'exmaple-nested-acr'

param keyData3 string = 'key-data-3'

param publisher string = 'MicrosoftWindowsServer'

param nicId array = [
  {
    id: 'example-id'
  }
]

param publicKey2 object = {
  keyData: 'key-data-2'
  path: 'path-2'
}

param publicKey4 object = {
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
