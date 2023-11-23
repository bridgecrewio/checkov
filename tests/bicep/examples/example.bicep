param subNameInfix string
param WaName string
param WAnumber string
param Location string
param Tags object
param WaKind string
param HttpsOnly bool
param Reserved bool
param appServicePlanName string // Parameter for the App Service Plan name

// Define the App Service Plan resource
resource _asp 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: Location
  // Other properties for the App Service Plan can be specified here
}
resource _webApplication 'Microsoft.Web/sites@2022-03-01' = {
    dependsOn: []
    name: format(subNameInfix, 'WA', WaName, WAnumber)
    location: Location
    tags: Tags
    kind: WaKind
    properties: {
      serverFarmId: _asp.id
      httpsOnly: HttpsOnly
      reserved: Reserved
      siteConfig: {
        http20Enabled: true
      }
  }
}