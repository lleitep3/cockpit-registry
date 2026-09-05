# GitHub Integration Rule

## Gold Rule: Use `cockpit github` for every GitHub operation

Whenever you need to interact with GitHub — search code, view issues or pull requests, inspect or watch GitHub Actions workflow runs, list commits, comment on PRs, approve PRs, or mark change-request review threads as resolved — always use the `cockpit github <command>` wrapper provided by the `github-tools` package.

Do **not** invoke `gh` directly. The `github-tools` package reads the GitHub token from the AICockpit vault and injects it into every `gh` invocation, ensuring consistent authentication and auditability.

### Example workflows

- Inspect a repository: `cockpit github run repo view`
- List recent workflow runs: `cockpit github actions list --repo owner/repo`
- Watch a running workflow: `cockpit github actions watch <run-id>`
- Read workflow logs: `cockpit github actions logs <run-id>`
- List latest commits on a branch: `cockpit github commits main --limit 10`
- Comment on a PR: `cockpit github pr comment 42 --body "Thanks for the review"`
- Approve a PR: `cockpit github pr approve 42`
- Resolve change-request threads: `cockpit github pr resolve 42`

Configure the integration first with `cockpit github configure --token <TOKEN>`.
