# GitHub Integration Rule

## Gold Rule: Use `cockpit github` for every GitHub operation

Whenever you need to interact with GitHub — search code, view issues or pull requests, inspect or watch GitHub Actions workflow runs, list commits, comment on PRs, approve PRs, mark change-request review threads as resolved, or commit code as a specific GitHub user — always use the `cockpit github <command>` wrapper provided by the `github-tools` package.

Do **not** invoke `gh` or `git` directly for GitHub-related work. The `github-tools` package reads the GitHub token from the AICockpit vault and injects it into every `gh` invocation, ensuring consistent authentication and auditability.

### Profiles

The package supports multiple GitHub profiles. Register a profile with a user label and token, and optionally set it as the default. Use `--user <label>` to select a profile for a single command.

- Register a profile: `cockpit github configure --user <USER> --token <TOKEN> --default`
- List profiles: `cockpit github configure --list`
- Use a profile: `cockpit github --user <USER> run repo view`
- Commit as a profile: `cockpit github --user <USER> git commit -m "..."`

### Example workflows

- Inspect a repository: `cockpit github run repo view`
- List recent workflow runs: `cockpit github actions list --repo owner/repo`
- Watch a running workflow: `cockpit github actions watch <run-id>`
- Read workflow logs: `cockpit github actions logs <run-id>`
- List latest commits on a branch: `cockpit github commits main --limit 10`
- Comment on a PR: `cockpit github pr comment 42 --body "Thanks for the review"`
- Approve a PR: `cockpit github pr approve 42`
- Resolve change-request threads: `cockpit github pr resolve 42`
- Commit as another user: `cockpit github --user colleague git commit -m "fix"`

Configure the integration first with `cockpit github configure --user <USER> --token <TOKEN>`.
