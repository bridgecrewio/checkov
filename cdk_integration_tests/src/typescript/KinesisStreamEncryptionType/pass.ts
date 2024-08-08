import { aws_kinesis as kinesis } from 'aws-cdk-lib';

const cfnSecurityConfigurationProps1: kinesis.CfnStreamProps = {
  streamEncryption: { encryptionType: "KMS", keyId: "dfdf"},
  name: 'name',
};
