import {aws_rds as rds} from 'aws-cdk-lib';

const instance2 = new rds.DatabaseInstance(this, "PostgresInstance2", {
    engine: rds.DatabaseInstanceEngine.POSTGRES,
    credentials: {
        username: 'username',
        password: 'password'
    },
    monitoringInterval: 1,
});

const instance1 = new rds.DatabaseInstance(this, "PostgresInstance2", {
    engine: rds.DatabaseInstanceEngine.POSTGRES,
    credentials: {
        username: 'username',
        password: 'password'
    },
    monitoringInterval: 322424,
});

