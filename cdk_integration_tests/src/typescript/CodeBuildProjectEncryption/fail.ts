import * as cdk from 'aws-cdk-lib';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';

export class CodeBuildStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create a CodeBuild project
    const project = new codebuild.Project(this, 'MyCodeBuildProject', {
      projectName: 'MyCodeBuildProject',
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_4_0,
        environmentVariables: {
          'EXAMPLE_ENV_VARIABLE': { value: 'example-value' },
        },
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          install: {
            commands: [
              'npm install',
            ],
          },
          build: {
            commands: [
              'npm run build',
            ],
          },
        },
      }),
    });

    // Ensure that encryption is not disabled
    project.node.addDependency(kmsKey);
  }
}

// Example usage
const app = new cdk.App();
new CodeBuildStack(app, 'CodeBuildStack');
