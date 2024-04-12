import { App, Stack } from 'aws-cdk-lib';
import * as transfer from 'aws-cdk-lib/aws-transfer';
import { Construct } from 'constructs';

class MyTransferServerStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define Transfer Server with EndpointType set to VPC
    new transfer.CfnServer(this, 'MyTransferServer', {
      endpointType: 'VPC',
      // Other properties as needed for your Transfer Server
    });
  }
}

class MyTransferServerStack2 extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define Transfer Server with EndpointType set to VPC_ENDPOINT
    new transfer.CfnServer(this, 'MyTransferServer2', {
      endpointType: 'VPC_ENDPOINT',
      // Other properties as needed for your Transfer Server
    });
  }
}

const app = new App();
new MyTransferServerStack(app, "MyTransferServerStack");
new MyTransferServerStack2(app, "MyTransferServerStack2");
app.synth();
