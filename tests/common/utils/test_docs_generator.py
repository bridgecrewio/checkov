import unittest

from checkov.common.util.docs_generator import get_compare_key


class TestOutputSorting(unittest.TestCase):

    def test_id_sorting_for_ckv_pattern(self):
        # keep all other things the same so sorting is based on the id
        check_ids = [
            ['CKV_AWS_1', '', '', '', ''],
            ['CKV_K8S_11', '', '', '', ''],
            ['CKV_K8S_15', '', '', '', ''],
            ['CKV_K8S_9', '', '', '', ''],
            ['CKV_K8S_2', '', '', '', ''],
            ['CKV2_K8S_2', '', '', '', ''],
            ['CKV_AZURE_11', '', '', '', ''],
            ['CKV_AZURE_32', '', '', '', ''],
            ['CKV_GIT_1', '', '', '', ''],
            ['CKV_AZURE_10', '', '', '', ''],
            ['CKV2_AWS_1', '', '', '', ''],
            ['CKV_AZURE_22', '', '', '', ''],
            ['CKV_K8S_20', '', '', '', ''],
            ['CKV_GCP_1', '', '', '', ''],
            ['CKV_K8S_1', '', '', '', ''],
            ['CKV_GCP_10', '', '', '', ''],
            ['CKV_AZURE_12', '', '', '', ''],
            ['CKV_K8S_10', '', '', '', ''],
            ['CKV_AWS_20', '', '', '', ''],
        ]
        sorted_check_ids = sorted(check_ids, key=get_compare_key)
        self.assertEqual(sorted_check_ids, [
            ['CKV_AWS_1', '', '', '', ''],
            ['CKV_AWS_20', '', '', '', ''],
            ['CKV2_AWS_1', '', '', '', ''],
            ['CKV_AZURE_10', '', '', '', ''],
            ['CKV_AZURE_11', '', '', '', ''],
            ['CKV_AZURE_12', '', '', '', ''],
            ['CKV_AZURE_22', '', '', '', ''],
            ['CKV_AZURE_32', '', '', '', ''],
            ['CKV_GCP_1', '', '', '', ''],
            ['CKV_GCP_10', '', '', '', ''],
            ['CKV_GIT_1', '', '', '', ''],
            ['CKV_K8S_1', '', '', '', ''],
            ['CKV_K8S_2', '', '', '', ''],
            ['CKV_K8S_9', '', '', '', ''],
            ['CKV_K8S_10', '', '', '', ''],
            ['CKV_K8S_11', '', '', '', ''],
            ['CKV_K8S_15', '', '', '', ''],
            ['CKV_K8S_20', '', '', '', ''],
            ['CKV2_K8S_2', '', '', '', ''],
        ])


if __name__ == '__main__':
    unittest.main()
