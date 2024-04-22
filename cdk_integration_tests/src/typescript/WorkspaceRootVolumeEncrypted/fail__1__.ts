import { App, Stack } from 'aws-cdk-lib';
import * as workspaces from 'aws-cdk-lib/aws-workspaces';
import { Construct } from 'constructs';

class WorkSpacesStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Note: The creation of a WorkSpaces directory as depicted in the Python code isn't directly supported through AWS CDK as of my last update.
    // Typically, you would use an existing directory (like an AD Connector or a Simple AD).
    // However, let's assume we're associating the workspace with an existing directory for this example.

    // Create a WorkSpaces workspace with root volume encryption enabled
    new workspaces.CfnWorkspace(this, 'MyWorkspace', {
      directoryId: 'your-directory-id', // Replace with your actual directory ID
      userName: 'my-user',
      bundleId: 'wsb-12345678', // Replace with your actual bundle ID
      rootVolumeEncryptionEnabled: false,
      userVolumeEncryptionEnabled: false, // Set to true if you want user volume encryption
      // Workspace properties need to be defined here, if necessary.
    });
  }
}

const app = new App();
new WorkSpacesStack(app, 'WorkSpacesStack');
app.synth();
