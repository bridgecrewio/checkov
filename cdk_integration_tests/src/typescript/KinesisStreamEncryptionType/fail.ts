import { aws_kinesis as kinesis } from 'aws-cdk-lib';

const cfnSecurityConfigurationProps1: kinesis.CfnStreamProps = {
  streamEncryption: { encryptionType: "None", keyId: "dfdf"},
  name: 'name',
};

const cfnSecurityConfigurationProps2: kinesis.CfnStreamProps = {
  name: 'name',
};
