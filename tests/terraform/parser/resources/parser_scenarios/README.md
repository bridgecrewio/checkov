Child directories contain parsing scenarios along with an `expected.json` file with the
total expected result output. During real evaluation all files will use absolute paths. To
make tests work across various systems, test expectations are written with relative paths
and tests will convert to absolute paths on the fly.

If evaluations are also being tested, an `eval.json` file may be created with the expected
evaluation data.