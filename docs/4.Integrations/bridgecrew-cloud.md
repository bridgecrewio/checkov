# Integrate Checkov with Bridgecrew Cloud
You can integrate checkov with bridgecrew's platform. This allows you to include checkov's scan results of a repository
into your bridgecrew account.

## Setup
In order to do so, first you need to acquire a bridgecrew issued API key.
 
//todo add screens when available

## Execution
After acquiring the API key, run checkov as follows:

`checkov -d <directory> --bc-api-key <key> --repo-id <repo_id> --branch <name>`

arguments:
- `<key>` - Bridgecrew issued API key
- `<repo_id>` - Identifying string of the scanned repository, of the standard Git repository naming form: `<owner>/<name>`
- `<branch>` - Branch name to be persisted on platform, defaults to the master branch
After successfully terminating, the results are persisted on bridgecrew's platform, and are available in it.


## Example usage
`checkov -d . --bc-api-key 84b8f259-a3dv-5c1e-9422-1bdc9aec0487 --repo-id bridgecrewio/checkov --branch some_feature` 
//TODO add a screenshot of violations
