// SOURCE
import { DatabaseInstance } from '@aws-cdk/aws-rds';

// SINK
// SINK: Vulnerability found due to missing Multi-AZ setting
new DatabaseInstance(stack, 'MyDatabaseInstance', {
    instanceType: ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
    vpc
    // missing Multi-AZ setting
});
