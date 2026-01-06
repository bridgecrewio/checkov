# solve-issue.md
<parameters>
issue: "GitHub issue number (e.g. 7239)"
</parameters>

# 0. Setup (always)
- Create/overwrite a dedicated branch
  <github.create_branch>
    branch: "fix/issue-{{issue}}"
    from_branch: "main"
  </github.create_branch>

# 1. Load the GitHub issue for context (always)
<terminal>gh issue view {{issue}} --json title,body,labels,url</terminal>

# 2. Research & implement fix (always) 
- Detect tech stack from labels/body.  
- <browser.search> "{{tech}} {{relevant keyword}}" for docs/examples.  
- Edit or add code to address the issue.
- Stage all changes.

# 3. Run tests (don't run)
# <terminal>npm test</terminal>
# <terminal>pytest</terminal>

# 4. Commit & push (always)
<github.push_files>
  branch: "fix/issue-{{issue}}"
  message: "Fix(#{{issue}}): A brief description of the fix"
  files: "{{list of modified files}}"
</github.push_files>

# 5. Open a pull request (always)
<github.create_pull_request>
  title: "Fix(#{{issue}}): A brief description of the fix"
  body: "Closes #{{issue}}. A more detailed description of the changes."
</github.create_pull_request>

# 6. Finish (always)
<exit>Done – PR is open and ready for review. 🎉</exit>
