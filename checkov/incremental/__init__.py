"""Incremental (PR diff) scanning support for Checkov.

Periodic scan:  `checkov -d <repo> --incremental-metadata-out metadata.json`
                Scans the whole repository and persists a *metadata graph*: per framework, the scan units,
                the files each unit depends on (with content hashes), the dependency edges between files,
                and the findings each unit produced.

PR scan:        `checkov -d <repo> --incremental-baseline metadata.json --changed-files a.tf,b.yaml`
                Uses only the MR diff (changed/added/deleted files) and the persisted metadata graph to
                decide which units can be affected, re-scans just those units with the stock runners, and
                merges their findings with the persisted findings of every other unit.

Everything here is opt-in; nothing changes when the flags are not used.
"""
