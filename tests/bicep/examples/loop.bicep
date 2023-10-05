resource Disks 'Microsoft.Compute/disks@2022-07-02' = [for (disk, i) in dataDisks: {
  name: disk.diskName
  location: location
  tags: tags
  sku: {
    name: disk.storageAccountType
  }
  zones: [
    avZone
  ]
  properties: {
    creationData: {
      createOption: 'Empty'
    }
    diskSizeGB: disk.diskSizeGB
    encryption: {
      type: 'EncryptionAtRestWithCustomerKey'
      diskEncryptionSetId: diskEncryptionSetId
    }
  }
}]
