import { aws_kinesis as kinesis } from 'aws-cdk-lib';

const cfnSecurityConfiguration1 = new kinesis.CfnStream(this, 'MyCfnSecurityConfiguration', {
  streamEncryption: { encryptionType: "None", keyId: "dfdf"},
  name: 'name',
});

const cfnSecurityConfiguration2 = new kinesis.CfnStream(this, 'MyCfnSecurityConfiguration', {
  name: 'name',
});
