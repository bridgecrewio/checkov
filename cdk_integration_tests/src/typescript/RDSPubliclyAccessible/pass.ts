// SOURCE
import { DatabaseInstance } from '@aws-cdk/aws-rds';

// SINK
new DatabaseInstance(stack, 'MyDatabaseInstance', {
    instanceType: ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
    vpc, publicly_accessible: true
});
