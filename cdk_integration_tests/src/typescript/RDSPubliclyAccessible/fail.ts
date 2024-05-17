// SOURCE
import { DatabaseInstance } from '@aws-cdk/aws-rds';

// SINK
// SINK: Vulnerability found due to publicly accessible setting
new DatabaseInstance(stack, 'MyDatabaseInstance', {
    instanceType: ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
    vpc
    // publicly accessible setting missing
});
