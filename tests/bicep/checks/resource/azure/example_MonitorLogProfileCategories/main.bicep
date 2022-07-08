// pass

resource pass 'Microsoft.Insights/logprofiles@2016-03-01' = {
  name: 'example'
  location: location

  properties: {
    categories: [
      'Action'
      'Delete'
      'Write'
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

// fail

resource fail 'Microsoft.Insights/logprofiles@2016-03-01' = {
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
