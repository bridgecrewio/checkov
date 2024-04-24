import {aws_glue as glue} from 'aws-cdk-lib';

const cfnSecurityConfiguration1 = new glue.CfnCrawler(this, 'MyCfnSecurityConfiguration', {
    crawlerSecurityConfiguration: 'securityConfiguration',
    name: 'name',
});

const cfnSecurityConfiguration2 = new glue.CfnDevEndpoint(this, 'MyCfnSecurityConfiguration', {
    securityConfiguration: 'securityConfiguration',
    name: 'name',
});

const cfnSecurityConfiguration3 = new glue.CfnJob(this, 'MyCfnSecurityConfiguration', {
    securityConfiguration: 'securityConfiguration',
    name: 'name',
});

const cfnSecurityConfigurationProps1: glue.CfnCrawlerProps = {
    name: 'name',
    crawlerSecurityConfiguration: 'securityConfiguration',
};

const cfnSecurityConfigurationProps2: glue.CfnDevEndpointProps = {
    name: 'name',
    securityConfiguration: 'securityConfiguration',
};

const cfnSecurityConfigurationProps3: glue.CfnJobProps = {
    name: 'name',
    securityConfiguration: 'securityConfiguration',
};

