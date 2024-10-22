// pass

resource enabled 'Microsoft.Compute/virtualMachines@2021-11-01' = {
  name: virtualMachineName
  location: location
  properties: {
    securityProfile: {
      encryptionAtHost: true
    }
  }
}

// fail

resource disabled 'Microsoft.Compute/virtualMachines@2021-11-01' = {
  name: virtualMachineName
  location: location
  properties: {
    securityProfile: {
      encryptionAtHost: false
    }
  }
}
