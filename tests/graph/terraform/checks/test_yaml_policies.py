import json
import os
import unittest
import warnings

import yaml
from checkov.graph.terraform import checks
from checkov.graph.terraform.checks_infra.nx_checks_parser import NXGraphCheckParser
from checkov.graph.terraform.checks_infra.registry import Registry


class TestYamlPolicies(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['UNIQUE_TAG'] = ''
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_VPCHasFlowLog(self):
        self.go("VPCHasFlowLog")

    def test_APIGWLoggingLevelsDefinedProperly(self):
        self.go("APIGWLoggingLevelsDefinedProperly")

    def test_GuardDutyIsEnabled(self):
        self.go("GuardDutyIsEnabled")

    def test_SGToEC2AndENI(self):
        self.go("SGToEC2AndENI")

    def test_StorageContainerActivityLogsNotPublic(self):
        self.go("StorageContainerActivityLogsNotPublic")

    def test_StorageCriticalDataEncryptedCMK(self):
        self.go("StorageCriticalDataEncryptedCMK")

    def test_VAconfiguredToSendReports(self):
        self.go("VAconfiguredToSendReports")

    def test_VAconfiguredToSendReportsToAdmins(self):
        self.go("VAconfiguredToSendReportsToAdmins")

    def test_VAisEnabledInStorageAccount(self):
        self.go("VAisEnabledInStorageAccount")

    def test_VAsetPeriodicScansOnSQL(self):
        self.go("VAsetPeriodicScansOnSQL")

    def test_CloudtrailHasCloudwatch(self):
        self.go("CloudtrailHasCloudwatch")

    def test_S3BucketHasPublicAccessBlock(self):
        self.go("S3BucketHasPublicAccessBlock")

    def test_AccessToPostgreSQLFromAzureServicesIsDisabled(self):
        self.go("AccessToPostgreSQLFromAzureServicesIsDisabled")

    def test_AzureActiveDirectoryAdminIsConfigured(self):
        self.go("AzureActiveDirectoryAdminIsConfigured")

    def test_DisableAccessToSqlDBInstanceForRootUsersWithoutPassword(self):
        self.go("DisableAccessToSqlDBInstanceForRootUsersWithoutPassword")

    def test_GCPProjectHasNoLegacyNetworks(self):
        self.go("GCPProjectHasNoLegacyNetworks")

    def test_AzureDataFactoriesEncryptedWithCustomerManagedKey(self):
        self.go("AzureDataFactoriesEncryptedWithCustomerManagedKey")

    def test_AzureUnattachedDisksAreEncrypted(self):
        self.go("AzureUnattachedDisksAreEncrypted")

    def test_AzureAntimalwareIsConfiguredWithAutoUpdatesForVMs(self):
        self.go("AzureAntimalwareIsConfiguredWithAutoUpdatesForVMs")

    def test_ALBRedirectsHTTPToHTTPS(self):
        self.go("ALBRedirectsHTTPToHTTPS")

    def test_GCPLogBucketsConfiguredUsingLock(self):
        self.go("GCPLogBucketsConfiguredUsingLock")

    def test_GCPAuditLogsConfiguredForAllServicesAndUsers(self):
        self.go("GCPAuditLogsConfiguredForAllServicesAndUsers")

    def test_GCPKMSCryptoKeysAreNotPubliclyAccessible(self):
        self.go("GCPKMSCryptoKeysAreNotPubliclyAccessible")

    def test_VirtualMachinesUtilizingManagedDisks(self):
        self.go("VirtualMachinesUtilizingManagedDisks")

    def test_RDSClusterHasBackupPlan(self):
        self.go("RDSClusterHasBackupPlan")

    def test_RedshiftClusterHasBackupPlan(self):
        self.go("RedshiftClusterHasBackupPlan")

    def test_EBSAddedBackup(self):
        self.go("EBSAddedBackup")

    def test_AMRClustersNotOpenToInternet(self):
        self.go("AMRClustersNotOpenToInternet")

    def test_AutoScallingEnabledELB(self):
        self.go("AutoScallingEnabledELB")

    def test_EC2hasVPC(self):
        self.go("EC2hasVPC")

    def test_IAMGroupHasAtLeastOneUser(self):
        self.go("IAMGroupHasAtLeastOneUser")

    def test_IAMUsersAreMembersAtLeastOneGroup(self):
        self.go("IAMUsersAreMembersAtLeastOneGroup")

    def test_DataExplorerEncryptionUsesCustomKey(self):
        self.go("DataExplorerEncryptionUsesCustomKey")

    def test_MSQLenablesCustomerManagedKey(self):
        self.go("MSQLenablesCustomerManagedKey")

    def test_PGSQLenablesCustomerManagedKey(self):
        self.go("PGSQLenablesCustomerManagedKey")

    def test_StorageLoggingIsEnabledForBlobService(self):
        self.go("StorageLoggingIsEnabledForBlobService")

    def test_StorageLoggingIsEnabledForTableService(self):
        self.go("StorageLoggingIsEnabledForTableService")

    def test_VMHasBackUpMachine(self):
        self.go("VMHasBackUpMachine")

    def test_SubnetHasACL(self):
        self.go("SubnetHasACL")

    def test_GKEClustersAreNotUsingDefaultServiceAccount(self):
        self.go("GKEClustersAreNotUsingDefaultServiceAccount")

    def test_AzureStorageAccountsUseCustomerManagedKeyForEncryption(self):
        self.go("AzureStorageAccountsUseCustomerManagedKeyForEncryption")

    def test_AzureMSSQLServerHasSecurityAlertPolicy(self):
        self.go("AzureMSSQLServerHasSecurityAlertPolicy")

    def test_AzureSynapseWorkspacesHaveNoIPFirewallRulesAttached(self):
        self.go("AzureSynapseWorkspacesHaveNoIPFirewallRulesAttached")

    def test_EncryptedEBSVolumeOnlyConnectedToEC2s(self):
        self.go("EncryptedEBSVolumeOnlyConnectedToEC2s")

    def test_EIPAllocatedToVPCAttachedEC2(self):
        self.go("EIPAllocatedToVPCAttachedEC2")

    def test_registry_load(self):
        registry = Registry(parser=NXGraphCheckParser())
        registry.load_checks()
        self.assertGreater(len(registry.checks), 0)

    @staticmethod
    def go(dir_name):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                f"resources/{dir_name}")
        assert os.path.exists(dir_path)
        policy_dir_path = os.path.dirname(checks.__file__)
        assert os.path.exists(policy_dir_path)
        found = False
        for root, d_names, f_names in os.walk(policy_dir_path):
            for f_name in f_names:
                if f_name == f"{dir_name}.yaml":
                    found = True
                    policy = load_yaml_data(f_name, root)
                    assert policy is not None
                    expected = load_yaml_data("expected.yaml", dir_path)
                    assert expected is not None
        assert found


def load_yaml_data(source_file_name, dir_path):
    expected_path = os.path.join(dir_path, source_file_name)
    if not os.path.exists(expected_path):
        return None

    with open(expected_path, "r") as f:
        expected_data = yaml.safe_load(f)

    return json.loads(json.dumps(expected_data))
