from __future__ import annotations

from unittest import mock

from checkov.contributor_metrics import process_contributor, parse_gitlog


def test_process_contributor():
    contributor = 'Fake User <fake.user@gmail.com> (50):\n    commit-1667835804\n    commit-1667835527\n    ' \
                  'commit-1667834817\n    commit-1667826784\n    commit-1667808222'

    result = process_contributor(contributor)

    assert result == "Fake User <fake.user@gmail.com> 1667835804"


@mock.patch("subprocess.Popen")
def test_parse_gitlog(mock_subproc_popen):
    process_mock = mock.Mock()
    output = 'Fake User <fake1@paloaltonetworks.com> (40):\n      commit-1666516907\n      commit-1666259461\n      ' \
             'commit-1666259213\n      commit-1666258676\n      commit-1666258296\n      commit-1666258146\n      ' \
             'commit-1660669175\n      commit-1660668538\n      commit-1660626680\n      commit-1660626648\n      ' \
             'commit-1660589354\n      commit-1660588125\n\n' \
             'dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> (38):\n      ' \
             'commit-1667819806\n      commit-1667819799\n      commit-1667819792\n      commit-1667216836\n       ' \
             'commit-1662541125\n      commit-1662476433\n      commit-1661850978\n      commit-1661850966\n       ' \
             'commit-1661746095\n      commit-1661154962\n      commit-1661154940\n\n' \
             'Fake User <fake2@paloaltonetworks.com> (31):\n      commit-1667216980\n      commit-1667216720\n      ' \
             'commit-1667216720\n      commit-1661265981\n      commit-1661265975\n      commit-1660808330\n      ' \
             'commit-1660799407\n      commit-1660737117\n      commit-1660632107\n      commit-1660631663'
    attrs = {"communicate.return_value": (output.encode('utf-8'), '')}
    process_mock.configure_mock(**attrs)
    mock_subproc_popen.return_value = process_mock

    result = parse_gitlog("my_repo", "jenkins")
    assert result == {"repository": "my_repo",
                      "source": "jenkins",
                      "contributors": ["Fake User <fake1@paloaltonetworks.com> 1666516907",
                                                                "dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> 1667819806",
                                                                "Fake User <fake2@paloaltonetworks.com> 1667216980"],
                      'failedAttempts': []}
