// pass

resource enabled 'Microsoft.Compute/disks@2021-12-01' = {
  name: '${name}-disk-${env}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }

  properties: {
    diskSizeGB: 10
    encryptionSettingsCollection: {
      enabled: true
      encryptionSettings: [
        {
          diskEncryptionKey: {
            secretUrl: secretUrl
            sourceVault: {
              id: vault.id
            }
          }
        }
      ]
    }
  }
}

// fail

resource disabled 'Microsoft.Compute/disks@2021-12-01' = {
  name: '${name}-disk-${env}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }

  properties: {
    diskSizeGB: 10
    encryptionSettingsCollection: {
      enabled: false
    }
  }
}
