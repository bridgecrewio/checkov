# GitHub Workflow

When solving an issue that requires code changes, follow this workflow:

1.  **Create a branch:** Use the `create_branch` tool from the `github.com/github/github-mcp-server` to create a new branch for the issue. The branch name should be descriptive, like `fix/1234-description` or `feat/1234-description`.
2.  **Commit changes:** After making the necessary code changes, use the `create_or_update_file` or `push_files` tool to commit the changes to the new branch. The commit message should be descriptive and reference the issue number.
3.  **Create a pull request:** Use the `create_pull_request` tool to open a new pull request from the branch to the main branch of the repository. The pull request title and body should be descriptive and reference the issue number.

Do not fork the repository unless absolutely necessary. Use the provided GitHub MCP server tools to work directly with the repository.
