import { App, Stack } from 'aws-cdk-lib';
import * as workspaces from 'aws-cdk-lib/aws-workspaces';
import { Construct } from 'constructs';

class WorkSpacesStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Assuming the Directory ID is known and exists. Replace 'your-directory-id' with the actual Directory ID.
    const directoryId = 'your-directory-id';

    // Create a WorkSpaces workspace with root volume encryption enabled
    new workspaces.CfnWorkspace(this, 'MyWorkspace', {
      directoryId: directoryId, // Use the known Directory ID
      bundleId: 'wsb-12345678', // Replace with your actual bundle ID
      userName: 'my-user',
      rootVolumeEncryptionEnabled: true,
      userVolumeEncryptionEnabled: false, // Set to true if you want user volume encryption
      // Other properties for your Workspace as needed
    });
  }
}

const app = new App();
new WorkSpacesStack(app, 'WorkSpacesStack');
app.synth();
