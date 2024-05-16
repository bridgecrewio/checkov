import unittest

from checkov.common.util.type_forcers import convert_prisma_policy_filter_to_dict


class TestTypeForcers(unittest.TestCase):
    def test_convert_prisma_policy_filter_to_dict(self):
        self.assertDictEqual(convert_prisma_policy_filter_to_dict('F1=A,F2=B'), {'F1': 'A', 'F2': 'B'})
        self.assertDictEqual(convert_prisma_policy_filter_to_dict(''), {})
        self.assertDictEqual(convert_prisma_policy_filter_to_dict(None), {})
        self.assertDictEqual(convert_prisma_policy_filter_to_dict('F1 =   A,   F2= B '), {'F1': 'A', 'F2': 'B'})
        self.assertDictEqual(convert_prisma_policy_filter_to_dict('F1=A,B,F2=C'), {'F1': 'A', 'F2': 'C'})
        self.assertDictEqual(convert_prisma_policy_filter_to_dict('F1=A,F2=B,C'), {'F1': 'A', 'F2': 'B'})

        policy_string = 'policy.name=AWS S3 bucket ACL grants READ permission to everyone'
        filter_string = convert_prisma_policy_filter_to_dict(policy_string)
        self.assertDictEqual(filter_string, {'policy.name': 'AWS S3 bucket ACL grants READ permission to everyone'})



if __name__ == '__main__':
    unittest.main()
