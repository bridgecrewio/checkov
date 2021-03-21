# pass

resource "aws_ssm_document" "s3_enabled_encrypted" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  content = <<DOC
  {
    "schemaVersion": "1.0",
    "description": "Document to hold regional settings for Session Manager",
    "sessionType": "Standard_Stream",
    "inputs": {
      "s3BucketName": "example",
      "s3KeyPrefix": "",
      "s3EncryptionEnabled": true,
      "cloudWatchLogGroupName": "",
      "cloudWatchEncryptionEnabled": true,
      "idleSessionTimeout": "20",
      "cloudWatchStreamingEnabled": true,
      "kmsKeyId": "",
      "runAsEnabled": false,
      "runAsDefaultUser": "",
      "shellProfile": {
        "windows": "",
        "linux": ""
      }
    }
  }
DOC
}

resource "aws_ssm_document" "s3_enabled_encrypted_yaml" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  document_format = "YAML"

  content = <<DOC
  schemaVersion: '1.0'
  description: Document to hold regional settings for Session Manager
  sessionType: Standard_Stream
  inputs:
    s3BucketName: 'example'
    s3KeyPrefix: ''
    s3EncryptionEnabled: true
    cloudWatchLogGroupName: ''
    cloudWatchEncryptionEnabled: true
    cloudWatchStreamingEnabled: true
    kmsKeyId: ''
    runAsEnabled: true
    runAsDefaultUser: ''
    idleSessionTimeout: '20'
    shellProfile:
      windows: ''
      linux: ''
DOC
}

resource "aws_ssm_document" "cw_enabled_encrypted" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  content = <<DOC
  {
    "schemaVersion": "1.0",
    "description": "Document to hold regional settings for Session Manager",
    "sessionType": "Standard_Stream",
    "inputs": {
      "s3BucketName": "",
      "s3KeyPrefix": "",
      "s3EncryptionEnabled": true,
      "cloudWatchLogGroupName": "example",
      "cloudWatchEncryptionEnabled": true,
      "idleSessionTimeout": "20",
      "cloudWatchStreamingEnabled": true,
      "kmsKeyId": "",
      "runAsEnabled": false,
      "runAsDefaultUser": "",
      "shellProfile": {
        "windows": "",
        "linux": ""
      }
    }
  }
DOC
}

resource "aws_ssm_document" "cw_enabled_encrypted_yaml" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  document_format = "YAML"

  content = <<DOC
  schemaVersion: '1.0'
  description: Document to hold regional settings for Session Manager
  sessionType: Standard_Stream
  inputs:
    s3BucketName: ''
    s3KeyPrefix: ''
    s3EncryptionEnabled: true
    cloudWatchLogGroupName: 'example'
    cloudWatchEncryptionEnabled: true
    cloudWatchStreamingEnabled: true
    kmsKeyId: ''
    runAsEnabled: true
    runAsDefaultUser: ''
    idleSessionTimeout: '20'
    shellProfile:
      windows: ''
      linux: ''
DOC
}

# failure

resource "aws_ssm_document" "disabled" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  content = <<DOC
  {
    "schemaVersion": "1.0",
    "description": "Document to hold regional settings for Session Manager",
    "sessionType": "Standard_Stream",
    "inputs": {
      "s3BucketName": "",
      "s3KeyPrefix": "",
      "s3EncryptionEnabled": true,
      "cloudWatchLogGroupName": "",
      "cloudWatchEncryptionEnabled": true,
      "idleSessionTimeout": "20",
      "cloudWatchStreamingEnabled": true,
      "kmsKeyId": "",
      "runAsEnabled": false,
      "runAsDefaultUser": "",
      "shellProfile": {
        "windows": "",
        "linux": ""
      }
    }
  }
DOC
}

resource "aws_ssm_document" "disabled_yaml" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  document_format = "YAML"

  content = <<DOC
  schemaVersion: '1.0'
  description: Document to hold regional settings for Session Manager
  sessionType: Standard_Stream
  inputs:
    s3BucketName: ''
    s3KeyPrefix: ''
    s3EncryptionEnabled: true
    cloudWatchLogGroupName: ''
    cloudWatchEncryptionEnabled: true
    cloudWatchStreamingEnabled: true
    kmsKeyId: ''
    runAsEnabled: true
    runAsDefaultUser: ''
    idleSessionTimeout: '20'
    shellProfile:
      windows: ''
      linux: ''
DOC
}

resource "aws_ssm_document" "s3_enabled_not_encrypted" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  content = <<DOC
  {
    "schemaVersion": "1.0",
    "description": "Document to hold regional settings for Session Manager",
    "sessionType": "Standard_Stream",
    "inputs": {
      "s3BucketName": "example",
      "s3KeyPrefix": "",
      "s3EncryptionEnabled": false,
      "cloudWatchLogGroupName": "",
      "cloudWatchEncryptionEnabled": true,
      "idleSessionTimeout": "20",
      "cloudWatchStreamingEnabled": true,
      "kmsKeyId": "",
      "runAsEnabled": false,
      "runAsDefaultUser": "",
      "shellProfile": {
        "windows": "",
        "linux": ""
      }
    }
  }
DOC
}

resource "aws_ssm_document" "s3_enabled_not_encrypted_yaml" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  document_format = "YAML"

  content = <<DOC
  schemaVersion: '1.0'
  description: Document to hold regional settings for Session Manager
  sessionType: Standard_Stream
  inputs:
    s3BucketName: 'example'
    s3KeyPrefix: ''
    s3EncryptionEnabled: false
    cloudWatchLogGroupName: ''
    cloudWatchEncryptionEnabled: true
    cloudWatchStreamingEnabled: true
    kmsKeyId: ''
    runAsEnabled: true
    runAsDefaultUser: ''
    idleSessionTimeout: '20'
    shellProfile:
      windows: ''
      linux: ''
DOC
}

resource "aws_ssm_document" "cw_enabled_not_encrypted" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  content = <<DOC
  {
    "schemaVersion": "1.0",
    "description": "Document to hold regional settings for Session Manager",
    "sessionType": "Standard_Stream",
    "inputs": {
      "s3BucketName": "",
      "s3KeyPrefix": "",
      "s3EncryptionEnabled": true,
      "cloudWatchLogGroupName": "example",
      "cloudWatchEncryptionEnabled": false,
      "idleSessionTimeout": "20",
      "cloudWatchStreamingEnabled": true,
      "kmsKeyId": "",
      "runAsEnabled": false,
      "runAsDefaultUser": "",
      "shellProfile": {
        "windows": "",
        "linux": ""
      }
    }
  }
DOC
}

resource "aws_ssm_document" "cw_enabled_not_encrypted_yaml" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"

  document_format = "YAML"

  content = <<DOC
  schemaVersion: '1.0'
  description: Document to hold regional settings for Session Manager
  sessionType: Standard_Stream
  inputs:
    s3BucketName: ''
    s3KeyPrefix: ''
    s3EncryptionEnabled: false
    cloudWatchLogGroupName: 'example'
    cloudWatchEncryptionEnabled: false
    cloudWatchStreamingEnabled: true
    kmsKeyId: ''
    runAsEnabled: true
    runAsDefaultUser: ''
    idleSessionTimeout: '20'
    shellProfile:
      windows: ''
      linux: ''
DOC
}
