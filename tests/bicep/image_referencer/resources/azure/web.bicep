resource webContainerApp 'Microsoft.Web/containerApps@2021-03-01' = {
  name: 'example'

  properties: {
    kubeEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetport: targetPort
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
    }
    template: {
      revisionSuffix: 'firstrevision'
      containers: [
        {
          name: proxy
          image: nginx
          resources: {
            cpu: cpuCore
            memory: '${memorySize}Gi'
          }
        }
      ]
      scale: {
        minReplica: minReplica
        maxReplica: maxReplica
      }
    }
  }
}

resource appContainerApp 'Microsoft.App/containerApps@2022-03-01' = {
  name: 'example'

  properties: {
    kubeEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetport: targetPort
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
    }
    template: {
      revisionSuffix: 'firstrevision'
      containers: [
        {
          name: app
          image: 'python:3.9'
          resources: {
            cpu: cpuCore
            memory: '${memorySize}Gi'
          }
        }
      ]
      scale: {
        minReplica: minReplica
        maxReplica: maxReplica
      }
    }
  }
}
