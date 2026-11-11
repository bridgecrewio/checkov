param minimumTlsVersion string = '1.2'

resource eventHubNamespace 'Microsoft.EventHub/namespaces@2022-01-01-preview' = {
  name: 'example-namespace'
  location: 'westeurope'
  properties: {
    minimumTlsVersion: minimumTlsVersion
  }
}
