# Integrate Checkov with Bridgecrew Cloud
You can integrate checkov with Bridgecrew's platform. This allows you to include checkov's scan results of a repository
into your Bridgecrew account.
First, you need to acquire a Bridgecrew issued API token. To do so, follow these steps:- Register (for free) to Bridgecrew's platform at [bridgecrew.cloud](https://www.bridgecrew.cloud/)

## Setup
First, you need to acquire a Bridgecrew issued API token. To do so, follow these steps: 
- Register (for free) to Bridgecrew's platform at [bridgecrew.cloud](https://www.bridgecrew.cloud/)
- After signing in, navigate to the [integrations page](https://www.bridgecrew.cloud/integrations), and click the API Token integration:
![bc-api-key](bc-api-integration.png)
- Acquire the issued API key (under the `Bridgecrew Token` title) for execution

## Execution
After acquiring the issued API key, run checkov as follows:

- `checkov -d <directory> --bc-api-key <key> --repo-id <repo_id> --branch <name>`

Or by using the `-f` file flag:
- `checkov -f <file_1> <file_2> ... <file_n> --bc-api-key <key> --repo-id <repo_id> --branch <name>`

### Arguments:
- `<key>` - Bridgecrew issued API key
- `<repo_id>` - Identifying string of the scanned repository, following the standard Git repository naming scheme: `<owner>/<name>`
- `<branch>` - Branch name to be persisted on platform, defaults to the master branch. NOTE: please make sure the scanned directory (supplied with `-d` flag)
is currently checked out from the given branch name.

## Bridgecrew cloud view
After successfully terminating, the scan results are persisted on [Bridgecrew Cloud](https://www.bridgecrew.cloud), and are available as possible violations
that can be seen
in the [incidents view](https://www.bridgecrew.cloud/incidents):
![bc-violations](bc-violations.png)

## Example usage
The following command scans the repository identified as `foo/bar`, on branch `develop`, using a Bridgecrew API key:
`checkov -d . --bc-api-key 84b8f259-a3dv-5c1e-9422-1bdc9aec0487 --repo-id foo/bar --branch develop` 
