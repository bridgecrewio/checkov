resource pool 'Microsoft.Batch/batchAccounts/pools@2022-06-01' = {
  name: 'example'

  properties: {
    scaleSettings: {
      fixedScale: {
        targetDedicatedNodes: 1
      }
    }
    virtualMachineConfiguration: {
      containerConfiguration: {
        containerImageNames: [
          'centos7'
        ]
        containerRegistries: [
          {
            // checkov:skip=CKV_SECRET_6 test secret
            password: 'myPassword'
            registryServer: 'myContainerRegistry.azurecr.io'
            username: 'myUserName'
          }
        ]
        type: 'DockerCompatible'
      }
    }
  }
}
