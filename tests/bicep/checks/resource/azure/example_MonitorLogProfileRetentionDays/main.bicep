// pass

resource enabled 'Microsoft.Insights/logprofiles@2016-03-01' = {
  name: 'example'
  location: location

  properties: {
    categories: [
      'Action'
    ]
    locations: [
      'global'
    ]
    retentionPolicy: {
      days: 365
      enabled: true
    }
  }
}

// fail

resource disabled 'Microsoft.Insights/logprofiles@2016-03-01' = {
  name: 'example'
  location: location

  properties: {
    categories: [
      'Action'
    ]
    locations: [
      'global'
    ]
    retentionPolicy: {
      days: 30
      enabled: false
    }
  }
}

resource low 'Microsoft.Insights/logprofiles@2016-03-01' = {
  name: 'example'
  location: location

  properties: {
    categories: [
      'Action'
    ]
    locations: [
      'global'
    ]
    retentionPolicy: {
      days: 30
      enabled: true
    }
  }
}
