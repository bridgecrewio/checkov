// The code below shows an example of how to instantiate this type.
// The values are placeholders you should change.
import {aws_glue as glue} from 'aws-cdk-lib';

const cfnDataCatalogEncryptionSettingsProps1: glue.CfnDataCatalogEncryptionSettingsProps = {
    catalogId: 'catalogId',
    dataCatalogEncryptionSettings: {
        connectionPasswordEncryption: {
            kmsKeyId: 'kmsKeyId',
            returnConnectionPasswordEncrypted: false,
        },
        encryptionAtRest: {
            catalogEncryptionMode: 'DISABLED',
            catalogEncryptionServiceRole: 'catalogEncryptionServiceRole',
            sseAwsKmsKeyId: 'sseAwsKmsKeyId',
        },
    },
};

let cfnDataCatalogEncryptionSettingsProps2: glue.CfnDataCatalogEncryptionSettingsProps = {
    catalogId: 'catalogId',
    dataCatalogEncryptionSettings: {
        connectionPasswordEncryption: {
            returnConnectionPasswordEncrypted: true,
        },
    },
    encryptionAtRest: {
        catalogEncryptionMode: 'DISABLED',
        catalogEncryptionServiceRole: 'catalogEncryptionServiceRole',
        sseAwsKmsKeyId: 'sseAwsKmsKeyId',
    },
};