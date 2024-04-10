import { App, Stack } from 'aws-cdk-lib';
import * as transfer from 'aws-cdk-lib/aws-transfer';
import { Construct } from 'constructs';

class MyTransferServerStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define Transfer Server with EndpointType set to a custom value
    new transfer.CfnServer(this, 'MyTransferServer', {
      endpointType: 'abc', // Replace 'abc' with your endpoint type
      // Other properties as needed for your Transfer Server
    });
  }
}

const app = new App();
new MyTransferServerStack(app, "MyTransferServerStack");
app.synth();
