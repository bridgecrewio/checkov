import os

BC_FROM_BRANCH = os.getenv('BC_FROM_BRANCH', "")
BC_TO_BRANCH = os.getenv('BC_TO_BRANCH', "")
if not BC_TO_BRANCH:  # support flow of direct commit from the branch into the same branch
    BC_TO_BRANCH = BC_FROM_BRANCH
BC_PR_ID = os.getenv('BC_PR_ID', "")
BC_PR_URL = os.getenv('BC_PR_URL', "")
BC_COMMIT_HASH = os.getenv('BC_COMMIT_HASH', "")
BC_COMMIT_URL = os.getenv('BC_COMMIT_URL', "")
BC_AUTHOR_NAME = os.getenv('BC_AUTHOR_NAME', "")
BC_AUTHOR_URL = os.getenv('BC_AUTHOR_URL', "")
BC_RUN_ID = os.getenv('BC_RUN_ID', "")
BC_RUN_URL = os.getenv('BC_RUN_URL', "")
BC_REPOSITORY_URL = os.getenv('BC_REPOSITORY_URL', "")
