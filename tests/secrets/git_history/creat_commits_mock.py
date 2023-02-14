import pickle
import git
# Create an instance of the Repo class and store its return value
repo = git.Repo('test2')
commits = list(repo.iter_commits(repo.active_branch, max_count=7))
# Pickle the repo object and save it to a file
with open('mock_git_commits.pkl', 'wb') as f:
    pickle.dump(commits, f)