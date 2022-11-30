resource containerGroup 'Microsoft.ContainerInstance/containerGroups@2021-10-01' = {
  name: 'example'

  properties: {
    initContainers: [
      {
        name: 'init'
        properties: {
          image: 'busybox'
        }
      }
    ]
    containers: [
      {
        name: 'reader'
        properties: {
          image: 'ubuntu:20.04'
          resources: {
            requests: {
              cpu: 1
              memoryInGB: 2
            }
          }
        }
      }
    ]
    osType: 'Linux'
  }
}
