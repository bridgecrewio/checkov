import unittest

from checkov.common.util.type_forcers import convert_prisma_policy_filter_to_params


class TestTypeForcers(unittest.TestCase):
    def test_convert_prisma_policy_filter_to_dict(self):
        self.assertListEqual(convert_prisma_policy_filter_to_params('F1=A,F2=B'), [('F1', 'A'), ('F2', 'B')])
        self.assertListEqual(convert_prisma_policy_filter_to_params(''), [])
        self.assertListEqual(convert_prisma_policy_filter_to_params(None), [])
        self.assertListEqual(convert_prisma_policy_filter_to_params('F1 =   A,   F2= B '), [('F1', 'A'), ('F2', 'B')])
        self.assertListEqual(convert_prisma_policy_filter_to_params('F1=A,B,F2=C'), [('F1', 'A'), ('F2', 'C')])
        self.assertListEqual(convert_prisma_policy_filter_to_params('F1=A,F2=B,C'), [('F1', 'A'), ('F2', 'B')])
        self.assertListEqual(convert_prisma_policy_filter_to_params('F1=A,F2=B,F1=C'), [('F1', 'A'), ('F2', 'B'), ('F1', 'C')])
        self.assertListEqual(convert_prisma_policy_filter_to_params('F1=A,F2=B,F1=C,F1=DDD'), [('F1', 'A'), ('F2', 'B'), ('F1', 'C'), ('F1', 'DDD')])

        policy_string = 'policy.name=AWS S3 bucket ACL grants READ permission to everyone'
        filter_string = convert_prisma_policy_filter_to_params(policy_string)
        self.assertListEqual(filter_string, [('policy.name', 'AWS S3 bucket ACL grants READ permission to everyone')])


if __name__ == '__main__':
    unittest.main()
